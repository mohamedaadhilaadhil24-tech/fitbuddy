from app.config import TIP_MODEL, call_gemini

TIP_PROMPT = """You are a nutrition and recovery coach.
Give ONE concise, practical nutrition or recovery tip (maximum 3 sentences) for a person
whose fitness goal is "{goal}". Make it specific and actionable, e.g. food choices,
hydration, protein timing, sleep or stretching. Return only the tip as plain text."""


def generate_nutrition_tip_with_flash(goal: str) -> str:
    return call_gemini(TIP_PROMPT.format(goal=goal), TIP_MODEL)
