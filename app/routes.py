import logging
import os

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import GeminiError
from app.database import (
    delete_user,
    get_all_plans,
    get_all_users,
    get_original_plan,
    get_user,
    save_plan,
    save_user,
    update_plan,
)
from app.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.gemini_generator import generate_workout_gemini
from app.schemas import FeedbackRequest, UserInput
from app.updated_plan import update_workout_plan

logger = logging.getLogger("fitbuddy.routes")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

router = APIRouter()

AI_BUSY_MESSAGE = (
    "The AI service is busy right now. Your plan could not be generated - "
    "please wait a few seconds and try again."
)

FALLBACK_TIP = (
    "Tip unavailable right now - please try again in a few seconds. "
    "General advice: stay hydrated and prioritize protein after workouts."
)


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
):
    user = UserInput(
        username=username,
        user_id=user_id,
        age=age,
        weight=weight,
        goal=goal,
        intensity=intensity,
    )

    try:
        workout_plan = generate_workout_gemini(user)
    except GeminiError as exc:
        logger.error("workout generation failed user_id=%s err=%s", user.user_id, str(exc)[:600])
        return templates.TemplateResponse(
            request,
            "result.html",
            {
                "request": request,
                "user": user,
                "workout_plan": "",
                "nutrition_tip": "",
                "updated": False,
                "error": AI_BUSY_MESSAGE,
            },
            status_code=502,
        )

    try:
        nutrition_tip = generate_nutrition_tip_with_flash(user.goal)
    except GeminiError as exc:
        logger.warning("tip generation failed user_id=%s err=%s", user.user_id, str(exc)[:600])
        nutrition_tip = FALLBACK_TIP

    try:
        save_user(user.user_id, user.username, user.age, user.weight, user.goal, user.intensity)
        save_plan(user.user_id, workout_plan)
    except Exception:
        logger.exception("db save failed user_id=%s", user.user_id)

    return templates.TemplateResponse(
        request,
        "result.html",
        {
            "request": request,
            "user": user,
            "workout_plan": workout_plan,
            "nutrition_tip": nutrition_tip,
            "updated": False,
            "error": None,
        },
    )


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
):
    req = FeedbackRequest(user_id=user_id, feedback=feedback)
    user = get_user(req.user_id)
    plan = get_original_plan(req.user_id)

    if not user or not plan:
        return templates.TemplateResponse(
            request,
            "result.html",
            {
                "request": request,
                "user": None,
                "workout_plan": "",
                "nutrition_tip": "",
                "updated": False,
                "error": f"No user or plan found for ID '{req.user_id}'.",
            },
            status_code=404,
        )

    user_input = UserInput(
        username=user.username,
        user_id=user.user_id,
        age=user.age,
        weight=user.weight,
        goal=user.goal,
        intensity=user.intensity,
    )

    try:
        updated_plan = update_workout_plan(plan.original_plan, req.feedback)
    except GeminiError as exc:
        logger.error("plan update failed user_id=%s err=%s", req.user_id, str(exc)[:600])
        return templates.TemplateResponse(
            request,
            "result.html",
            {
                "request": request,
                "user": user_input,
                "workout_plan": plan.original_plan,
                "nutrition_tip": "",
                "updated": False,
                "error": AI_BUSY_MESSAGE,
            },
            status_code=502,
        )

    try:
        update_plan(req.user_id, updated_plan, req.feedback)
    except Exception:
        logger.exception("db update failed user_id=%s", req.user_id)

    try:
        nutrition_tip = generate_nutrition_tip_with_flash(user.goal)
    except GeminiError as exc:
        logger.warning("tip generation failed user_id=%s err=%s", req.user_id, str(exc)[:600])
        nutrition_tip = FALLBACK_TIP

    return templates.TemplateResponse(
        request,
        "result.html",
        {
            "request": request,
            "user": user_input,
            "workout_plan": updated_plan,
            "nutrition_tip": nutrition_tip,
            "updated": True,
            "error": None,
        },
    )


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request):
    users = get_all_users()
    plans = {plan.user_id: plan for plan in get_all_plans()}
    return templates.TemplateResponse(
        request,
        "all_users.html",
        {"request": request, "users": users, "plans": plans},
    )


@router.post("/delete-user/{user_id}")
def delete_user_route(user_id: str):
    delete_user(user_id)
    return RedirectResponse(url="/view-all-users", status_code=303)
