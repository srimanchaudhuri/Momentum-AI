"""Business logic for Goal CRUD operations."""

from datetime import date, datetime, timezone

from bson import ObjectId

from app.database import get_database
from app.exceptions import AuthorizationError, InvalidIdError, NotFoundError
from app.logger import get_logger
from models.goal import GoalCreate, GoalUpdate

logger = get_logger(__name__)


def _collection():
    return get_database()["goals"]


def _serialize(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    doc["user_id"] = str(doc["user_id"])
    if doc.get("onboarding_session_id"):
        doc["onboarding_session_id"] = str(doc["onboarding_session_id"])
    return doc


def _to_oid(value: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise InvalidIdError(value)
    return ObjectId(value)


async def _get_goal_or_404(user_id: str, goal_id: str) -> dict:
    """Fetch a goal and verify ownership."""
    oid = _to_oid(goal_id)
    goal = await _collection().find_one({"_id": oid})
    if not goal:
        raise NotFoundError("Goal", goal_id)
    if str(goal["user_id"]) != user_id:
        raise AuthorizationError()
    return goal


async def create_goal(user_id: str, payload: GoalCreate) -> dict:
    """Create a new goal for the user."""
    now = datetime.now(timezone.utc)
    today = date.today()

    document = {
        "user_id": ObjectId(user_id),
        "title": payload.title,
        "description": payload.description,
        "timeline": {
            "start_date": today.isoformat(),
            "target_date": payload.target_date.isoformat(),
            "duration_days": (payload.target_date - today).days,
        },
        "status": "active",
        "progress_percent": 0.0,
        "onboarding_session_id": None,
        "created_at": now,
        "updated_at": now,
    }

    result = await _collection().insert_one(document)
    created = await _collection().find_one({"_id": result.inserted_id})
    logger.info("Goal created: %s for user %s", result.inserted_id, user_id)
    return _serialize(created)


async def get_goal(user_id: str, goal_id: str) -> dict:
    """Get a single goal with ownership check."""
    goal = await _get_goal_or_404(user_id, goal_id)
    return _serialize(goal)


async def list_goals(
    user_id: str, page: int, per_page: int
) -> tuple[list[dict], int]:
    """List all goals for a user with pagination."""
    collection = _collection()
    uid = ObjectId(user_id)
    skip = (page - 1) * per_page

    total = await collection.count_documents({"user_id": uid})
    cursor = (
        collection.find({"user_id": uid})
        .skip(skip)
        .limit(per_page)
        .sort("created_at", -1)
    )
    goals = [_serialize(doc) async for doc in cursor]
    return goals, total


async def update_goal(user_id: str, goal_id: str, payload: GoalUpdate) -> dict:
    """Update a goal with ownership check."""
    await _get_goal_or_404(user_id, goal_id)
    oid = _to_oid(goal_id)

    update_data = payload.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc)

    # If target_date changed, recalculate timeline
    if "target_date" in update_data:
        target = update_data.pop("target_date")
        today = date.today()
        update_data["timeline.target_date"] = target.isoformat()
        update_data["timeline.duration_days"] = (target - today).days

    await _collection().update_one({"_id": oid}, {"$set": update_data})
    updated = await _collection().find_one({"_id": oid})
    logger.info("Goal updated: %s", goal_id)
    return _serialize(updated)


async def delete_goal(user_id: str, goal_id: str) -> None:
    """Delete a goal with ownership check."""
    await _get_goal_or_404(user_id, goal_id)
    oid = _to_oid(goal_id)
    await _collection().delete_one({"_id": oid})
    logger.info("Goal deleted: %s", goal_id)
