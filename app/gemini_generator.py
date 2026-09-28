from app.config import WORKOUT_MODEL, call_gemini
from app.schemas import UserInput

WORKOUT_PROMPT = """You are an expert fitness coach. Create a personalized 7-day workout plan.

User profile:
- Name: {username}
- Age: {age} years
- Weight: {weight} kg
- Fitness goal: {goal}
- Preferred intensity: {intensity}

Requirements:
- Cover Day 1 through Day 7 with a clear focus per day (e.g. full body, upper body, lower body, cardio, core, flexibility, active rest).
- For each day include: warm-up (5-10 mins), main workout with exercise names and sets/reps (or duration), and cool-down/recovery.
- Match volume and difficulty to the "{intensity}" intensity level.
- Include at least one rest or active-recovery day.
- Return ONLY the plan as plain text, neatly formatted, no markdown symbols."""


def generate_workout_gemini(user: UserInput) -> str:
    prompt = WORKOUT_PROMPT.format(
        username=user.username,
        age=user.age,
        weight=user.weight,
        goal=user.goal,
        intensity=user.intensity,
    )
    return call_gemini(prompt, WORKOUT_MODEL)
