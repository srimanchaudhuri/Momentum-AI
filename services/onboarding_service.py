"""Business logic for the onboarding conversation flow.

Uses predefined questions. AI-generated questions will be plugged in later.
"""

from datetime import datetime, timezone

from bson import ObjectId

from app.database import get_database
from app.exceptions import (
    AppException,
    AuthorizationError,
    InvalidIdError,
    NotFoundError,
)
from app.logger import get_logger

logger = get_logger(__name__)

# Predefined onboarding questions (AI replaces these later)
ONBOARDING_QUESTIONS = [
    "What goal would you like to achieve?",
    "What is your timeline for this goal?",
    "What is your current experience or skill level in this area?",
    "How many hours per day can you dedicate to this goal?",
    "Do you have a budget for resources (courses, books, tools)?",
]


def _collection():
    return get_database()["onboarding_sessions"]


def _goals():
    return get_database()["goals"]


def _serialize(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    doc["user_id"] = str(doc["user_id"])
    if doc.get("goal_id"):
        doc["goal_id"] = str(doc["goal_id"])
    return doc


def _to_oid(value: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise InvalidIdError(value)
    return ObjectId(value)


async def start_session(user_id: str) -> dict:
    """Create a new onboarding session with the first question."""
    now = datetime.now(timezone.utc)
    first_question = ONBOARDING_QUESTIONS[0]

    document = {
        "user_id": ObjectId(user_id),
        "status": "in_progress",
        "steps": [
            {
                "step_number": 1,
                "question": first_question,
                "answer": None,
                "answered_at": None,
            }
        ],
        "current_step": 1,
        "goal_id": None,
        "created_at": now,
        "updated_at": now,
    }

    result = await _collection().insert_one(document)
    logger.info("Onboarding session started: %s", result.inserted_id)

    return {
        "session_id": str(result.inserted_id),
        "step": {
            "step_number": 1,
            "question": first_question,
            "answer": None,
            "answered_at": None,
        },
        "total_steps": len(ONBOARDING_QUESTIONS),
    }


async def _get_session_or_404(user_id: str, session_id: str) -> dict:
    """Fetch session and verify ownership."""
    oid = _to_oid(session_id)
    session = await _collection().find_one({"_id": oid})
    if not session:
        raise NotFoundError("Onboarding session", session_id)
    if str(session["user_id"]) != user_id:
        raise AuthorizationError()
    return session


async def get_session(user_id: str, session_id: str) -> dict:
    """Get full session state."""
    session = await _get_session_or_404(user_id, session_id)
    return _serialize(session)


async def answer_step(user_id: str, session_id: str, answer: str) -> dict:
    """Submit an answer to the current step and advance to the next.

    Returns the answered step and the next question (if any).
    """
    session = await _get_session_or_404(user_id, session_id)

    if session["status"] != "in_progress":
        raise AppException("This onboarding session is already completed.", 400)

    current = session["current_step"]
    now = datetime.now(timezone.utc)

    # Update the current step with the answer
    await _collection().update_one(
        {"_id": session["_id"], "steps.step_number": current},
        {
            "$set": {
                f"steps.{current - 1}.answer": answer,
                f"steps.{current - 1}.answered_at": now,
                "updated_at": now,
            }
        },
    )

    answered_step = {
        "step_number": current,
        "question": session["steps"][current - 1]["question"],
        "answer": answer,
        "answered_at": now,
    }

    # Check if there are more questions
    next_step_num = current + 1
    if next_step_num <= len(ONBOARDING_QUESTIONS):
        next_question = ONBOARDING_QUESTIONS[next_step_num - 1]
        next_step = {
            "step_number": next_step_num,
            "question": next_question,
            "answer": None,
            "answered_at": None,
        }

        await _collection().update_one(
            {"_id": session["_id"]},
            {
                "$push": {"steps": next_step},
                "$set": {"current_step": next_step_num, "updated_at": now},
            },
        )

        return {
            "session_id": str(session["_id"]),
            "answered_step": answered_step,
            "next_step": next_step,
            "is_complete": False,
        }

    # No more questions
    return {
        "session_id": str(session["_id"]),
        "answered_step": answered_step,
        "next_step": None,
        "is_complete": True,
    }


async def complete_session(user_id: str, session_id: str) -> dict:
    """Mark session as complete and create a goal stub from the answers."""
    session = await _get_session_or_404(user_id, session_id)

    if session["status"] == "completed":
        raise AppException("Session is already completed.", 400)

    # Check all questions are answered
    for step in session["steps"]:
        if step["answer"] is None:
            raise AppException(
                f"Step {step['step_number']} has not been answered yet.", 400
            )

    now = datetime.now(timezone.utc)

    # Extract answers to create a goal stub
    answers = {s["step_number"]: s["answer"] for s in session["steps"]}
    goal_title = answers.get(1, "Untitled Goal")

    from datetime import date, timedelta

    # Try to parse timeline from answer, default to 90 days
    target_date = (date.today() + timedelta(days=90)).isoformat()
    today = date.today()

    goal_doc = {
        "user_id": ObjectId(user_id),
        "title": goal_title,
        "description": f"Goal created from onboarding. Skill level: {answers.get(3, 'N/A')}. "
                        f"Hours/day: {answers.get(4, 'N/A')}. Budget: {answers.get(5, 'N/A')}.",
        "timeline": {
            "start_date": today.isoformat(),
            "target_date": target_date,
            "duration_days": 90,
        },
        "status": "active",
        "progress_percent": 0.0,
        "onboarding_session_id": session["_id"],
        "created_at": now,
        "updated_at": now,
    }

    goal_result = await _goals().insert_one(goal_doc)
    goal_id = goal_result.inserted_id

    # Update session as completed
    await _collection().update_one(
        {"_id": session["_id"]},
        {"$set": {"status": "completed", "goal_id": goal_id, "updated_at": now}},
    )

    logger.info(
        "Onboarding completed: session=%s goal=%s", session_id, goal_id
    )

    updated = await _collection().find_one({"_id": session["_id"]})
    return _serialize(updated)
