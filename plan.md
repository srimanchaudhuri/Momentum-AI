# MomentumAI — Backend Architecture Plan

## Overview

MomentumAI is an AI-powered goal tracking app. Users onboard through an AI chatbot conversation, receive a generated plan with schedules and resources, customize it, then track daily/weekly progress on a visual dashboard.

This plan covers the **complete backend** — from authentication to AI integration to real-time progress tracking.

---

## Current State

What we already have:

| Component | Status |
|---|---|
| FastAPI app with lifespan | ✅ Done |
| PyMongo async (MongoDB) | ✅ Done |
| User CRUD (model → service → router) | ✅ Done |
| Global exception handlers | ✅ Done |
| Centralized logger | ✅ Done |
| Config via pydantic-settings | ✅ Done |

---

## Proposed Project Structure

```
Momentum-AI/
├── main.py                          # App entry point
├── pyproject.toml
├── .env
│
├── app/                             # Core application wiring
│   ├── config.py                    # Settings (existing)
│   ├── database.py                  # MongoDB lifecycle (existing)
│   ├── exceptions.py                # Domain exceptions (existing)
│   ├── exception_handlers.py        # Global handlers (existing)
│   ├── logger.py                    # Logger factory (existing)
│   └── security.py                  # [NEW] JWT creation/verification, password hashing
│
├── models/                          # Pydantic schemas (request/response)
│   ├── user.py                      # (existing)
│   ├── auth.py                      # [NEW] Login, token, signup schemas
│   ├── goal.py                      # [NEW] Goal CRUD schemas
│   ├── onboarding.py                # [NEW] AI conversation step schemas
│   ├── plan.py                      # [NEW] Plan, schedule, milestone schemas
│   ├── resource.py                  # [NEW] Resource recommendation schemas
│   ├── progress.py                  # [NEW] Daily/weekly log schemas
│   ├── notification.py              # [NEW] Notification schemas
│   └── dashboard.py                 # [NEW] Aggregated dashboard data schemas
│
├── services/                        # Business logic (HTTP-agnostic)
│   ├── user_service.py              # (existing)
│   ├── auth_service.py              # [NEW] Signup, login, token refresh
│   ├── goal_service.py              # [NEW] Goal CRUD + lifecycle
│   ├── onboarding_service.py        # [NEW] AI conversation flow manager
│   ├── ai_service.py                # [NEW] Gemini/LLM integration
│   ├── plan_service.py              # [NEW] Plan generation + customization
│   ├── resource_service.py          # [NEW] Resource search + filtering
│   ├── progress_service.py          # [NEW] Progress logging + analytics
│   ├── notification_service.py      # [NEW] Notification creation + delivery
│   ├── scheduler_service.py         # [NEW] Background job scheduling
│   └── dashboard_service.py         # [NEW] Aggregated stats + chart data
│
├── routers/                         # Thin HTTP controllers
│   ├── users.py                     # (existing)
│   ├── auth.py                      # [NEW] /api/auth/*
│   ├── goals.py                     # [NEW] /api/goals/*
│   ├── onboarding.py                # [NEW] /api/onboarding/*
│   ├── progress.py                  # [NEW] /api/goals/{id}/progress/*
│   ├── notifications.py             # [NEW] /api/notifications/*
│   └── dashboard.py                 # [NEW] /api/dashboard/*
│
├── middleware/                       # [NEW] Request middleware
│   ├── __init__.py
│   └── auth.py                      # JWT verification dependency
│
└── tasks/                           # [NEW] Background / scheduled tasks
    ├── __init__.py
    ├── daily_reminder.py            # Daily check-in notifications
    └── progress_evaluator.py        # Periodic progress recalculation
```

---

## MongoDB Collections

```
momentum_db
├── users                  # User accounts + auth data
├── goals                  # User goals with metadata
├── onboarding_sessions    # AI conversation state per goal
├── plans                  # Generated plans (schedule, milestones)
├── resources              # Recommended resources per plan
├── progress_logs          # Daily/weekly check-in entries
└── notifications          # Notification records
```

---

## Phase 1: Authentication & Security

### What we need
- Password hashing (bcrypt via `passlib`)
- JWT access + refresh tokens (`python-jose`)
- Auth middleware (FastAPI `Depends()`)

### New config vars (`.env`)
```
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
GEMINI_API_KEY=your-gemini-key
```

### New dependencies
```
passlib[bcrypt]>=1.7.4
python-jose[cryptography]>=3.3.0
google-genai>=1.0.0
httpx>=0.28.0
apscheduler>=3.10.0
```

### `app/security.py`
```python
# Password hashing
hash_password(plain: str) -> str
verify_password(plain: str, hashed: str) -> bool

# JWT
create_access_token(user_id: str) -> str
create_refresh_token(user_id: str) -> str
decode_token(token: str) -> dict     # returns {"sub": user_id, "exp": ...}
```

### `middleware/auth.py`
```python
async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """FastAPI dependency — extracts and verifies JWT from Authorization header.
    Returns the user document. Raises 401 if invalid."""
```

### `routers/auth.py` — API Endpoints
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/auth/signup` | Create account (hashes password, returns tokens) |
| `POST` | `/api/auth/login` | Verify credentials, return access + refresh tokens |
| `POST` | `/api/auth/refresh` | Exchange refresh token for new access token |

### User model changes
- `password` field stores **hashed** value (never returned in responses)
- Add `is_active: bool` field for soft-disable

---

## Phase 2: Goal & Onboarding System

### How the AI conversation flow works

The onboarding is a **multi-step, stateful conversation** stored in MongoDB. Each step has a question from the AI and an answer from the user.

```
Screen 1: "What is your goal?"               → user answers
Screen 2: "What's your timeline?"             → user answers
Screen 3: "What's your current skill level?"   → user answers
Screen 4: "How many hours/day can you dedicate?" → user answers
          ↓
   AI generates plan
```

### `onboarding_sessions` collection schema
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "status": "in_progress | completed | abandoned",
  "steps": [
    {
      "step_number": 1,
      "question": "What goal would you like to achieve?",
      "answer": "Learn machine learning",
      "answered_at": "2026-07-30T10:00:00Z"
    },
    {
      "step_number": 2,
      "question": "What's your timeline for this goal?",
      "answer": "3 months",
      "answered_at": "2026-07-30T10:01:00Z"
    }
  ],
  "current_step": 2,
  "goal_id": null,            // set after completion → links to generated goal
  "created_at": "...",
  "updated_at": "..."
}
```

### `goals` collection schema
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "title": "Learn Machine Learning",
  "description": "AI-generated summary of the goal",
  "timeline": {
    "start_date": "2026-08-01",
    "target_date": "2026-11-01",
    "duration_days": 92
  },
  "status": "active | paused | completed | abandoned",
  "progress_percent": 45.5,
  "onboarding_session_id": ObjectId,
  "created_at": "...",
  "updated_at": "..."
}
```

### `routers/onboarding.py` — API Endpoints
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/onboarding/start` | Start a new onboarding session, return first AI question |
| `GET` | `/api/onboarding/{session_id}` | Get current session state |
| `POST` | `/api/onboarding/{session_id}/answer` | Submit answer to current step, get next question |
| `POST` | `/api/onboarding/{session_id}/complete` | Finalize session → triggers AI plan generation |

### `routers/goals.py` — API Endpoints
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/goals` | List all goals for current user |
| `GET` | `/api/goals/{goal_id}` | Get goal detail with progress |
| `PATCH` | `/api/goals/{goal_id}` | Update goal (title, timeline, status) |
| `DELETE` | `/api/goals/{goal_id}` | Abandon/delete a goal |

---

## Phase 3: AI Service & Plan Generation

### `services/ai_service.py`

This is the **core AI integration** — wraps the Gemini API to:
1. Generate contextual onboarding questions
2. Deep-search and create a structured plan
3. Recommend resources

```python
async def generate_next_question(session: dict) -> str:
    """Given the conversation so far, generate the next relevant question."""

async def generate_plan(session: dict) -> dict:
    """Given a completed onboarding session, generate a full plan with:
    - Weekly schedule
    - Milestones with target dates
    - Resource recommendations
    Uses Gemini with structured output (JSON mode)."""

async def search_resources(goal: str, budget: str | None) -> list[dict]:
    """Search for relevant resources (courses, books, tools).
    Uses Gemini's grounding/search capabilities."""
```

> [!IMPORTANT]
> The AI service should use **structured output** (Gemini's JSON mode or function calling) to ensure the plan response is always parseable — not free-form text that needs regex parsing.

### `plans` collection schema
```json
{
  "_id": ObjectId,
  "goal_id": ObjectId,
  "user_id": ObjectId,
  "schedule": {
    "hours_per_day": 2,
    "days_per_week": ["Mon", "Tue", "Wed", "Thu", "Fri"],
    "weekly_plan": [
      {
        "week": 1,
        "focus": "Python fundamentals",
        "tasks": ["Complete Python basics course", "Practice 10 problems"],
        "hours": 10
      }
    ]
  },
  "milestones": [
    {
      "id": "m1",
      "title": "Complete Python fundamentals",
      "target_date": "2026-08-15",
      "status": "pending | in_progress | completed",
      "progress_percent": 0,
      "order": 1
    }
  ],
  "is_customized": false,        // true after user modifies
  "version": 1,                  // increments on re-generation
  "created_at": "...",
  "updated_at": "..."
}
```

### `resources` collection schema
```json
{
  "_id": ObjectId,
  "plan_id": ObjectId,
  "goal_id": ObjectId,
  "title": "Machine Learning Specialization",
  "type": "course | book | tool | article | video",
  "url": "https://...",
  "provider": "Coursera",
  "cost": { "amount": 49.99, "currency": "USD" },
  "is_free": false,
  "is_selected": true,          // user can toggle
  "ai_reason": "Covers fundamentals with hands-on projects",
  "order": 1
}
```

### Plan & Resource API Endpoints
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/goals/{goal_id}/plan` | Get the current plan |
| `PATCH` | `/api/goals/{goal_id}/plan` | Customize schedule/milestones |
| `POST` | `/api/goals/{goal_id}/plan/regenerate` | Ask AI to regenerate the plan |
| `GET` | `/api/goals/{goal_id}/resources` | List resources |
| `PATCH` | `/api/goals/{goal_id}/resources/{id}` | Toggle/reorder a resource |
| `POST` | `/api/goals/{goal_id}/resources/refresh` | Ask AI for new resource suggestions |

---

## Phase 4: Progress Tracking

### `progress_logs` collection schema
```json
{
  "_id": ObjectId,
  "goal_id": ObjectId,
  "user_id": ObjectId,
  "type": "daily | weekly",
  "date": "2026-08-15",
  "entries": {
    "hours_spent": 2.5,
    "tasks_completed": ["Read chapter 3", "Solved 5 problems"],
    "milestone_updates": [
      { "milestone_id": "m1", "progress_percent": 60 }
    ],
    "mood": "motivated",         // optional self-report
    "notes": "Struggled with recursion but got it eventually"
  },
  "ai_feedback": "Great progress! You're ahead of schedule on milestone 1.",
  "created_at": "..."
}
```

### Progress API Endpoints
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/goals/{goal_id}/progress` | Log a daily/weekly check-in |
| `GET` | `/api/goals/{goal_id}/progress` | Get progress history (with date range filter) |
| `GET` | `/api/goals/{goal_id}/progress/summary` | Aggregated stats (for dashboard charts) |

### How progress updates the goal
```
User submits daily log
    → progress_service calculates new milestone percentages
    → updates goal.progress_percent (weighted average of milestones)
    → ai_service generates feedback message
    → returns updated stats to frontend
```

---

## Phase 5: Dashboard & Analytics

### `routers/dashboard.py` — API Endpoints
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/dashboard` | Full dashboard data for current user |
| `GET` | `/api/dashboard/goals/{goal_id}` | Detailed analytics for a single goal |

### Dashboard response shape
```json
{
  "active_goals": 2,
  "goals": [
    {
      "goal_id": "...",
      "title": "Learn Machine Learning",
      "progress_percent": 45.5,
      "hiker_position": 0.455,        // 0.0 = base, 1.0 = peak
      "days_remaining": 47,
      "eta": "2026-10-28",
      "deadline": "2026-11-01",
      "on_track": true,
      "streak_days": 12,              // consecutive days with check-ins
      "current_milestone": {
        "title": "Complete Python fundamentals",
        "progress_percent": 80
      },
      "weekly_hours": [2.5, 3.0, 1.5, 2.0],   // last 4 weeks
      "progress_history": [             // for line chart
        { "date": "2026-08-01", "percent": 5 },
        { "date": "2026-08-08", "percent": 12 },
        { "date": "2026-08-15", "percent": 22 }
      ]
    }
  ],
  "today": {
    "pending_checkins": ["Learn Machine Learning"],
    "tasks_due": ["Read chapter 5", "Complete quiz 3"]
  }
}
```

> [!NOTE]
> The `hiker_position` field (0.0–1.0) is what the frontend uses to position the hiker on the mountain animation. It maps directly to `progress_percent / 100`.

---

## Phase 6: Notifications & Scheduling

### `notifications` collection schema
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "goal_id": ObjectId,
  "type": "daily_reminder | weekly_summary | milestone_reached | deadline_warning | streak_alert",
  "title": "Time for your daily check-in!",
  "body": "You've been on a 12-day streak for 'Learn ML'. Don't break it!",
  "is_read": false,
  "created_at": "..."
}
```

### Notification API Endpoints
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/notifications` | List notifications (paginated, unread first) |
| `PATCH` | `/api/notifications/{id}/read` | Mark as read |
| `POST` | `/api/notifications/read-all` | Mark all as read |

### Background Tasks (`tasks/`)

Using **APScheduler** for recurring jobs:

| Task | Schedule | Description |
|---|---|---|
| `daily_reminder.py` | Every day at 9 AM (user timezone) | Create "daily check-in" notification for active goals |
| `progress_evaluator.py` | Every Sunday midnight | Calculate weekly summaries, detect off-track goals, generate alerts |

---

## Implementation Order

> [!IMPORTANT]
> Each phase builds on the previous. This is the recommended execution order.

| Phase | What | Dependencies | Estimated Files |
|---|---|---|---|
| **1** | Auth (signup, login, JWT, middleware) | None (builds on user_service) | ~8 files |
| **2** | Goal + Onboarding (CRUD, AI conversation) | Phase 1 (needs auth) | ~10 files |
| **3** | AI + Plan Generation (Gemini integration) | Phase 2 (needs goals) | ~6 files |
| **4** | Progress Tracking (daily logs, analytics) | Phase 3 (needs plan/milestones) | ~6 files |
| **5** | Dashboard (aggregated data endpoints) | Phase 4 (needs progress data) | ~4 files |
| **6** | Notifications + Scheduler (background jobs) | Phase 4 (needs progress) | ~6 files |

---

## Config Changes Needed

#### `app/config.py` additions:
```python
# Auth
JWT_SECRET_KEY: str
JWT_ALGORITHM: str = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

# AI
GEMINI_API_KEY: str
GEMINI_MODEL: str = "gemini-2.5-flash"

# Scheduler
DAILY_REMINDER_HOUR: int = 9    # 9 AM
```

---

## New Dependencies

```toml
dependencies = [
    "fastapi[standard]>=0.115.0",
    "pymongo>=4.12.0",
    "pydantic[email]>=2.11.0",
    "pydantic-settings>=2.9.0",
    "python-dotenv>=1.1.0",
    # --- NEW ---
    "passlib[bcrypt]>=1.7.4",      # password hashing
    "python-jose[cryptography]>=3.3.0",  # JWT tokens
    "google-genai>=1.0.0",         # Gemini AI
    "httpx>=0.28.0",               # async HTTP (for AI/search)
    "apscheduler>=3.10.0",         # background job scheduling
]
```

---

## Open Questions

> [!IMPORTANT]
> These decisions will affect the implementation. Please review:

1. **AI Provider**: I assumed **Google Gemini** since you're in the Google ecosystem. Do you want Gemini, OpenAI, or should I design an abstraction that supports both?

2. **Notification delivery**: The current plan stores notifications in MongoDB and serves them via API (pull-based). Do you also want **push notifications** (WebSocket for real-time, or FCM for mobile)? This significantly changes the architecture.

3. **Multi-goal support**: Should a user be able to have **multiple active goals** simultaneously, or only one at a time?

4. **Budget for resources**: You mentioned users can customize resources "according to budget." Should we store a user's budget preference, or just let them filter resources by free/paid?

5. **User timezone**: Daily reminders need to fire at the right time per user. Should we store a `timezone` field on the user profile?

---

## Verification Plan

### Automated Tests
For each phase, I'll verify with:
```bash
# Import check — all modules load without errors
uv run python -c "from main import app"

# Run the dev server and hit endpoints
uv run fastapi dev main.py
```

### Manual Verification
- Test each API endpoint via the auto-generated **Swagger UI** (`/docs`)
- Verify MongoDB documents are created correctly using `mongosh`
- Test the AI conversation flow end-to-end (onboarding → plan generation)
