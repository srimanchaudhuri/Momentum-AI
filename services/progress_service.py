"""Business logic for progress tracking and analytics."""

from datetime import date, datetime, timedelta, timezone

from bson import ObjectId

from app.database import get_database
from app.exceptions import AuthorizationError, InvalidIdError, NotFoundError
from app.logger import get_logger
from models.progress import ProgressLogCreate

logger = get_logger(__name__)


def _logs():
    return get_database()["progress_logs"]


def _goals():
    return get_database()["goals"]


def _plans():
    return get_database()["plans"]


def _serialize(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    doc["goal_id"] = str(doc["goal_id"])
    doc["user_id"] = str(doc["user_id"])
    return doc


def _to_oid(value: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise InvalidIdError(value)
    return ObjectId(value)


async def _verify_goal_ownership(user_id: str, goal_id: str) -> dict:
    goal = await _goals().find_one({"_id": _to_oid(goal_id)})
    if not goal:
        raise NotFoundError("Goal", goal_id)
    if str(goal["user_id"]) != user_id:
        raise AuthorizationError()
    return goal


async def log_progress(
    user_id: str, goal_id: str, payload: ProgressLogCreate
) -> dict:
    """Log a daily or weekly check-in and update goal progress."""
    goal = await _verify_goal_ownership(user_id, goal_id)
    goid = _to_oid(goal_id)
    now = datetime.now(timezone.utc)
    today = date.today()

    document = {
        "goal_id": goid,
        "user_id": ObjectId(user_id),
        "type": payload.type,
        "date": today.isoformat(),
        "entries": {
            "hours_spent": payload.hours_spent,
            "tasks_completed": payload.tasks_completed,
            "milestone_updates": [m.model_dump() for m in payload.milestone_updates],
            "mood": payload.mood,
            "notes": payload.notes,
        },
        "ai_feedback": None,  # AI fills this later
        "created_at": now,
    }

    result = await _logs().insert_one(document)

    # Update milestone progress in the plan if provided
    if payload.milestone_updates:
        plan = await _plans().find_one({"goal_id": goid})
        if plan:
            for mu in payload.milestone_updates:
                for i, m in enumerate(plan["milestones"]):
                    if m["id"] == mu.milestone_id:
                        status = "completed" if mu.progress_percent >= 100 else "in_progress"
                        await _plans().update_one(
                            {"_id": plan["_id"]},
                            {
                                "$set": {
                                    f"milestones.{i}.progress_percent": mu.progress_percent,
                                    f"milestones.{i}.status": status,
                                }
                            },
                        )

    # Recalculate overall goal progress from milestones
    await _recalculate_goal_progress(goid)

    created = await _logs().find_one({"_id": result.inserted_id})
    logger.info("Progress logged for goal %s", goal_id)
    return _serialize(created)


async def _recalculate_goal_progress(goal_id: ObjectId) -> None:
    """Recalculate goal progress_percent from milestone averages."""
    plan = await _plans().find_one({"goal_id": goal_id})
    if not plan or not plan.get("milestones"):
        return

    milestones = plan["milestones"]
    avg = sum(m.get("progress_percent", 0) for m in milestones) / len(milestones)

    await _goals().update_one(
        {"_id": goal_id},
        {"$set": {"progress_percent": round(avg, 1), "updated_at": datetime.now(timezone.utc)}},
    )


async def get_progress_history(
    user_id: str,
    goal_id: str,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[dict]:
    """Get progress log history for a goal with optional date filtering."""
    await _verify_goal_ownership(user_id, goal_id)
    goid = _to_oid(goal_id)

    query: dict = {"goal_id": goid}
    if date_from or date_to:
        date_filter = {}
        if date_from:
            date_filter["$gte"] = date_from.isoformat()
        if date_to:
            date_filter["$lte"] = date_to.isoformat()
        query["date"] = date_filter

    cursor = _logs().find(query).sort("date", -1)
    return [_serialize(doc) async for doc in cursor]


async def get_progress_summary(user_id: str, goal_id: str) -> dict:
    """Get aggregated progress stats for a goal."""
    goal = await _verify_goal_ownership(user_id, goal_id)
    goid = _to_oid(goal_id)

    logs = []
    async for doc in _logs().find({"goal_id": goid}).sort("date", 1):
        logs.append(doc)

    total_hours = sum(l["entries"].get("hours_spent", 0) for l in logs)
    total_tasks = sum(len(l["entries"].get("tasks_completed", [])) for l in logs)

    # Mood distribution
    mood_dist: dict = {}
    for l in logs:
        mood = l["entries"].get("mood")
        if mood:
            mood_dist[mood] = mood_dist.get(mood, 0) + 1

    # Streak calculation (consecutive days with logs)
    streak = 0
    if logs:
        today = date.today()
        check_date = today
        log_dates = {l["date"] for l in logs}
        while check_date.isoformat() in log_dates:
            streak += 1
            check_date -= timedelta(days=1)

    total_logs = len(logs)
    return {
        "goal_id": goal_id,
        "total_hours": round(total_hours, 1),
        "total_logs": total_logs,
        "avg_hours_per_log": round(total_hours / total_logs, 1) if total_logs else 0.0,
        "streak_days": streak,
        "tasks_completed_count": total_tasks,
        "progress_percent": goal.get("progress_percent", 0.0),
        "mood_distribution": mood_dist,
    }
