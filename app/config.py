import logging
import os
import re
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()

logger = logging.getLogger("fitbuddy.gemini")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
WORKOUT_MODEL = os.getenv("WORKOUT_MODEL", "gemini-flash-latest")
TIP_MODEL = os.getenv("TIP_MODEL", "gemini-flash-latest")
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "gemini-3.5-flash,gemini-3.6-flash,gemini-flash-lite-latest")

client = genai.Client(api_key=GOOGLE_API_KEY)

RETRY_HINT_RE = re.compile(r"retry in ([0-9.]+)s", re.IGNORECASE)


class GeminiError(Exception):
    pass


def _delay_from_message(message: str, default: float) -> float:
    match = RETRY_HINT_RE.search(message)
    if match:
        return min(float(match.group(1)) + 2.0, 50.0)
    return default


def call_gemini(prompt: str, model_name: str, retries: int = 3) -> str:
    candidates = [model_name]
    for extra in FALLBACK_MODEL.split(","):
        extra = extra.strip()
        if extra and extra not in candidates:
            candidates.append(extra)

    errors = []
    for name in candidates:
        for attempt in range(retries):
            try:
                logger.info("gemini call model=%s attempt=%s", name, attempt + 1)
                response = client.models.generate_content(model=name, contents=prompt)
                text = (response.text or "").strip()
                if text:
                    logger.info("gemini ok model=%s chars=%s", name, len(text))
                    return text
                logger.warning("gemini empty response model=%s", name)
                errors.append(f"{name}: empty response")
                break
            except Exception as exc:
                message = str(exc)
                logger.warning(
                    "gemini fail model=%s attempt=%s err=%s", name, attempt + 1, message[:400]
                )
                errors.append(f"{name}: {message}")

                transient = (
                    "503" in message
                    or "UNAVAILABLE" in message
                    or "getaddrinfo" in message
                    or "Errno 11001" in message
                    or "Connection" in message
                    or "timed out" in message
                )
                rate_limited = "429" in message or "RESOURCE_EXHAUSTED" in message
                exhausted_forever = "limit: 0" in message
                last_attempt = attempt >= retries - 1

                if exhausted_forever or last_attempt:
                    break

                if rate_limited:
                    delay = _delay_from_message(message, 3 * (2 ** attempt))
                elif transient:
                    delay = 3 * (attempt + 1)
                else:
                    break

                logger.info("waiting %ss before retry model=%s", delay, name)
                time.sleep(delay)
    raise GeminiError(" | ".join(errors))
