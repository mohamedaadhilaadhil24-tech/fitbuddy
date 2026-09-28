from app.config import WORKOUT_MODEL, call_gemini

UPDATE_PROMPT = """You are an expert fitness coach revising a workout plan.

Original 7-day plan:
{original_plan}

User feedback: "{feedback}"

Regenerate the FULL updated 7-day plan (Day 1 through Day 7) incorporating the feedback
while keeping the plan balanced and appropriate for the original goal. Keep the same
plain-text structure: daily focus, warm-up, main workout with sets/reps, cool-down.
Return ONLY the updated plan as plain text, no markdown symbols."""


def update_workout_plan(original_plan: str, feedback: str) -> str:
    prompt = UPDATE_PROMPT.format(original_plan=original_plan, feedback=feedback)
    return call_gemini(prompt, WORKOUT_MODEL)
