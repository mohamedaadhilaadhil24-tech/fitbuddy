# FitBuddy – AI Fitness Plan Generator using Gemini Models

<p align="center">
  <img src="static/images/logo.png" alt="FitBuddy logo" width="140" />
</p>

## 1. Project Description

FitBuddy is a web-based application that uses AI to generate personalized workout plans and
nutrition tips based on a user's fitness goals — such as weight loss, muscle gain, or general
wellness. Built with **FastAPI** and integrated with **Google's Gemini models**, FitBuddy
simplifies the process of creating structured and effective fitness routines.

The application takes user information — age, weight, goal, and preferred workout intensity
(low / medium / high) — and generates a customized **7-day fitness plan**. Users can also submit
feedback to update and refine their plan using AI. A complementary nutrition or recovery tip is
provided based on the selected goal.

With a clean, glassmorphism user interface and database support via **SQLite**, FitBuddy ensures
each user's data and generated plan are stored and accessible. It offers both API endpoints
(interactive docs at `/docs`) and an interactive HTML/Jinja2 interface for ease of use.

## 2. Scenarios

- **Scenario 1 – Plan Generation:** A user inputs their personal details (name, age, weight,
  fitness goal such as "weight loss" or "muscle gain", and preferred intensity — low, medium or
  high) and receives a personalized, day-by-day 7-day workout plan tailored to their objective
  and experience level, enhancing motivation and adherence.
- **Scenario 2 – Feedback Refinement:** A user submits feedback on their existing plan (e.g.,
  "more focus on cardio" or "include more rest days"). The system regenerates an updated plan,
  keeping users engaged with dynamic, evolving fitness support.
- **Scenario 3 – Nutrition / Recovery Tip:** A user requests a tip based on their selected goal.
  The platform delivers a concise, relevant suggestion (e.g., "Include protein in your
  post-workout meal" for muscle gain) that complements the workout plan.
- **Scenario 4 – Admin / Coach Dashboard:** An admin or coach accesses `/view-all-users` to see
  all registered users and their workout plans — comparing original and updated versions and
  monitoring activity — streamlining oversight for trainers managing multiple clients.

## 3. Technical Architecture

**Stack:** FastAPI (backend) · Gemini via `google-genai` SDK (AI layer) · SQLite + SQLAlchemy
(persistence) · Jinja2 + HTML/CSS (frontend) · Uvicorn (ASGI server)

```
Browser (HTML/CSS, glassmorphism UI)
        │  POST /generate-workout, /submit-feedback
        ▼
FastAPI  ── routes.py ── Pydantic validation (UserInput, FeedbackRequest)
        │         │
        │         ├─► gemini_generator.py  ──► Gemini (7-day workout plan)
        │         ├─► gemini_flash_generator.py ──► Gemini (nutrition tip)
        │         └─► updated_plan.py      ──► Gemini (feedback-based revision)
        │
        └─► database.py (SQLAlchemy ORM) ──► fitbuddy.db (SQLite)
```

**Templates:** `index.html` (input form) · `result.html` (plan, tip, feedback) ·
`all_users.html` (admin panel)

### Pre-requisites

| Skill / Tool | Documentation |
|---|---|
| FastAPI Framework | [FastAPI Documentation](https://fastapi.tiangolo.com/) |
| Gemini API | [Google Generative AI Documentation](https://ai.google.dev/) |
| HTML, CSS, Jinja2 | [W3Schools HTML/CSS/Jinja2](https://www.w3schools.com/) |
| Python Programming | [Python Official Docs](https://docs.python.org/3/) |
| Version Control with Git | [Git Documentation](https://git-scm.com/doc) |
| SQLAlchemy & SQLite | [SQLAlchemy Docs](https://docs.sqlalchemy.org/) |
| Environment Setup (pip, venv) | [Virtualenv Guide](https://virtualenv.pypa.io/en/latest/) |
| Uvicorn ASGI Server | [Uvicorn Docs](https://www.uvicorn.org/) |

## 4. Project Workflow

| Milestone | Focus | Activities |
|---|---|---|
| **M1** | Model selection & Architecture | 1.1 Research/select generative AI model · 1.2 Define architecture · 1.3 Set up dev environment |
| **M2** | Core functionalities | 2.1 Develop core functions · 2.2 FastAPI backend for routing & input processing |
| **M3** | routes.py Development | 3.1 Main application logic in routes.py |
| **M4** | Frontend Development | 4.1 Design UI · 4.2 Dynamic templates with Jinja2 |
| **M5** | Deployment | 5.1 Prepare local deployment · 5.2 Test & verify |

## 5. Milestone 1 – Model Selection & Architecture

**Requirements:** the AI model had to generate structured 7-day workout plans, provide concise
nutrition tips, update plans from feedback, and perform well in real-time web interaction.

**Model evaluation:** Hugging Face models were tested first —
**T5 & BART** (text generation), **DistilBERT** (intent classification), **Bloom** (general
generation). They showed promise but required Hugging Face hosting or local GPU setup, plus
fine-tuning or complex prompting to produce structured plans — so they were rejected.

**Selected: Google Gemini models** (via the modern `google-genai` SDK):
- **Gemini (Flash class)** – structured 7-day workout generation and feedback-based plan
  updating: rich, context-aware, reliably formatted responses
- **Gemini Flash (lite/quick)** – fast, practical nutrition tips; lightweight and efficient for
  quick API calls

Reasons: API-based and trivial to integrate with FastAPI, naturally understands structured
formatting (days, sections), high accuracy with minimal prompt tuning, scalable for
feedback-based revisions. Model names are **configurable in `.env`** (`WORKOUT_MODEL`,
`TIP_MODEL`, `FALLBACK_MODEL`) with an automatic fallback chain, so retired model versions can
be swapped without code changes.

**Environment setup:**
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt        # fastapi uvicorn jinja2 sqlalchemy python-multipart google-genai python-dotenv
uvicorn app.main:app --reload          # http://127.0.0.1:8000  ·  API docs: /docs
```

## 6. Milestone 2 – Core Functionalities

| Function | File | Model | Purpose |
|---|---|---|---|
| `generate_workout_gemini()` | `app/gemini_generator.py` | Gemini (Pro role) | Personalized 7-day plan: warm-up (5–10 min), main workout (exercises, sets, reps), cool-down — matched to goal & intensity |
| `generate_nutrition_tip_with_flash()` | `app/gemini_flash_generator.py` | Gemini Flash | Concise, goal-aligned nutrition/recovery tip |
| `update_workout_plan()` | `app/updated_plan.py` | Gemini (Pro role) | Original plan + user feedback → revised full 7-day plan |
| `save_user()`, `save_plan()`, `update_plan()`, `get_original_plan()`, `get_user()`, `get_all_users()`, `get_all_plans()`, `delete_user()` | `app/database.py` | – | SQLAlchemy CRUD; original and updated plans stored as separate fields |
| `call_gemini()` | `app/config.py` | – | Shared client with exponential backoff, server-hinted retry delays, and model fallback chain |

Validation uses Pydantic schemas **`UserInput`** and **`FeedbackRequest`** (`app/schemas.py`)
for the `/generate-workout` and `/submit-feedback` routes. A dedicated admin view renders at
`/view-all-users`.

## 7. Milestone 3 – routes.py

| Route | Method | Logic |
|---|---|---|
| `/` | GET | Serves the input form (`index.html`) |
| `/generate-workout` | POST | Form data → `UserInput` Pydantic model → `generate_workout_gemini()` + `generate_nutrition_tip_with_flash()` → `save_user()` / `save_plan()` → `result.html` |
| `/submit-feedback` | POST | Captures feedback + user_id → retrieves original plan from DB → `update_workout_plan()` → `update_plan()` → `result.html` with updated plan |
| `/view-all-users` | GET | `get_all_users()` + `get_all_plans()` → `all_users.html` admin dashboard |
| `/delete-user/{user_id}` | POST | Deletes a user and their plans → redirect to admin |

Resilience: AI calls are wrapped so any Gemini failure returns a friendly, styled error message
(HTTP 502) instead of a raw internal-server-error page; failures are logged to `server.err.log`.

## 8. Milestone 4 – Frontend

Three Jinja2 templates under `/templates`, styled by a single shared stylesheet
(`/static/css/style.css`) with a studio-level glassmorphism theme:

- **index.html** – input form: username, user_id, age, weight, goal, intensity. Floating glass
  topbar, ambient gradient blobs behind translucent cards, black pill CTA (`Generate plan →`).
- **result.html** – renders `{{ workout_plan }}` and `{{ nutrition_tip }}` (plan in a monospace
  `<pre>` block), profile summary tiles, success badge, and the feedback form posting to
  `/submit-feedback`. AI failures render a styled `{{ error }}` alert.
- **all_users.html** – loops `{% for user in users %}` with `{% set plan = plans.get(...) %}` to
  show original vs updated plans side by side, plus per-user delete.

Setup: `Jinja2Templates(directory=TEMPLATE_DIR)` + `TemplateResponse(request, name, context)`.
Responsive via Flexbox/CSS grid and mobile media queries.

## 9. Milestone 5 – Deployment & Testing

**Setup:** virtual environment + `requirements.txt`; sensitive config via `.env` loaded with
`python-dotenv` (`GOOGLE_API_KEY` + model names). `.env` is git-ignored.

**Run:**
```powershell
cd C:\Users\acer\FitBuddy
venv\Scripts\activate
uvicorn app.main:app --reload
```
App: `http://127.0.0.1:8000` · API docs: `http://127.0.0.1:8000/docs`

**Verified pages:**
- **Home** – clean form (Name, User ID, Age, Weight, Goal, Intensity) with "Generate Plan" CTA
- **Personalized workout page** – user summary + day-wise plan (focus, exercises, sets/reps,
  rest intervals, warm-up/cool-down) generated by Gemini
- **Nutrition Tip** – concise goal-aligned advice beneath the plan
- **Feedback page** – enter user ID + feedback → plan regenerated with confirmation badge
- **View All Users** – admin table of every user with original and updated plans

**Verified end-to-end:** generate → feedback → admin → delete all return correct responses
(200/303); AI error paths return a friendly styled 502 page; all request/attempt logs captured
in `server.err.log`.

## 10. Conclusion

FitBuddy – AI Fitness Plan Generator is a comprehensive, user-centric web application that
showcases the synergy between artificial intelligence and health-tech. Using Google Gemini
models, it generates personalized 7-day workout plans and daily nutrition/recovery tips from
simple user inputs, built on FastAPI for backend logic, SQLAlchemy + SQLite for persistence, and
Jinja2 for a clean, responsive, glassmorphism UI.

Its dynamic feedback feature sets it apart: users comment on the effectiveness or difficulty of
their plan and the system intelligently regenerates it, ensuring ongoing customization. The
administrative view — showing all users with original and updated plans — supports transparency
and monitoring, making FitBuddy suitable for individuals and for coaches or institutions
managing multiple fitness profiles. Overall, FitBuddy is a scalable, adaptable AI-powered
solution that personalizes the fitness journey and evolves with the user's progress.

---

## Quick Reference

### Project Structure
```
FitBuddy\
├── app\
│   ├── main.py                   # FastAPI entry (lifespan, logging, static, router)
│   ├── routes.py                 # All routes + graceful AI error handling
│   ├── gemini_generator.py       # generate_workout_gemini()
│   ├── gemini_flash_generator.py # generate_nutrition_tip_with_flash()
│   ├── updated_plan.py           # update_workout_plan()
│   ├── database.py               # SQLAlchemy models + CRUD
│   ├── schemas.py                # Pydantic: UserInput, FeedbackRequest
│   └── config.py                 # .env loading, Gemini client, retries/fallback
├── templates\                    # index.html · result.html · all_users.html
├── static\css\style.css          # Shared glassmorphism theme
├── requirements.txt
├── .env                          # GOOGLE_API_KEY + models (git-ignored)
├── server.log / server.err.log   # runtime logs (git-ignored)
└── fitbuddy.db                   # SQLite (created at first run)
```

### .env
```
GOOGLE_API_KEY=your_key_here
WORKOUT_MODEL=gemini-flash-latest
TIP_MODEL=gemini-flash-latest
FALLBACK_MODEL=gemini-3.5-flash,gemini-3.6-flash,gemini-flash-lite-latest
```
> Free-tier note: Pro-class models have a 0 request quota (billing required), so the app
> defaults to Flash models. Retries respect the server's "retry in Ns" quota hints.

### Security
`.env` contains your API key and is listed in `.gitignore` — never commit or share it.
#   f i t b u d d y  
 #   f i t b u d d y  
 