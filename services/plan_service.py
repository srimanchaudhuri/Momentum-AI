"""Business logic for plan and milestone management."""

from datetime import datetime, timezone
from uuid import uuid4

from bson import ObjectId

from app.database import get_database
from app.exceptions import AuthorizationError, InvalidIdError, NotFoundError
from app.logger import get_logger
from models.plan import MilestoneCreate, MilestoneUpdate, PlanCreate, PlanUpdate

logger = get_logger(__name__)


def _collection():
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


async def _verify_goal_ownership(user_id: str, goal_id: str) -> None:
    """Verify the user owns the goal."""
    goal = await get_database()["goals"].find_one({"_id": _to_oid(goal_id)})
    if not goal:
        raise NotFoundError("Goal", goal_id)
    if str(goal["user_id"]) != user_id:
        raise AuthorizationError()


async def _get_plan_or_404(user_id: str, goal_id: str) -> dict:
    """Fetch the plan for a goal with ownership check."""
    await _verify_goal_ownership(user_id, goal_id)
    plan = await _collection().find_one({"goal_id": _to_oid(goal_id)})
    if not plan:
        raise NotFoundError("Plan for goal", goal_id)
    return plan


async def create_plan(user_id: str, goal_id: str, payload: PlanCreate) -> dict:
    """Create a plan for a goal."""
    await _verify_goal_ownership(user_id, goal_id)

    # Check if plan already exists
    existing = await _collection().find_one({"goal_id": _to_oid(goal_id)})
    if existing:
        raise NotFoundError("Plan already exists for this goal. Use PATCH to update.", "")

    now = datetime.now(timezone.utc)
    milestones = []
    for m in payload.milestones:
        milestones.append({
            "id": str(uuid4())[:8],
            "title": m.title,
            "target_date": m.target_date.isoformat(),
            "status": "pending",
            "progress_percent": 0.0,
            "order": m.order,
        })

    document = {
        "goal_id": _to_oid(goal_id),
        "user_id": ObjectId(user_id),
        "schedule": payload.schedule.model_dump(),
        "milestones": milestones,
        "is_customized": False,
        "version": 1,
        "created_at": now,
        "updated_at": now,
    }

    result = await _collection().insert_one(document)
    created = await _collection().find_one({"_id": result.inserted_id})
    logger.info("Plan created for goal %s", goal_id)
    return _serialize(created)


async def get_plan(user_id: str, goal_id: str) -> dict:
    """Get the plan for a goal."""
    plan = await _get_plan_or_404(user_id, goal_id)
    return _serialize(plan)


async def update_plan(user_id: str, goal_id: str, payload: PlanUpdate) -> dict:
    """Update the plan schedule."""
    plan = await _get_plan_or_404(user_id, goal_id)
    now = datetime.now(timezone.utc)

    update_data: dict = {"updated_at": now, "is_customized": True}
    if payload.schedule:
        update_data["schedule"] = payload.schedule.model_dump()

    await _collection().update_one(
        {"_id": plan["_id"]},
        {"$set": update_data, "$inc": {"version": 1}},
    )

    updated = await _collection().find_one({"_id": plan["_id"]})
    logger.info("Plan updated for goal %s", goal_id)
    return _serialize(updated)


# ---------------------------------------------------------------------------
# Milestone operations
# ---------------------------------------------------------------------------

async def add_milestone(
    user_id: str, goal_id: str, payload: MilestoneCreate
) -> dict:
    """Add a milestone to an existing plan."""
    plan = await _get_plan_or_404(user_id, goal_id)
    now = datetime.now(timezone.utc)

    milestone = {
        "id": str(uuid4())[:8],
        "title": payload.title,
        "target_date": payload.target_date.isoformat(),
        "status": "pending",
        "progress_percent": 0.0,
        "order": payload.order,
    }

    await _collection().update_one(
        {"_id": plan["_id"]},
        {
            "$push": {"milestones": milestone},
            "$set": {"updated_at": now, "is_customized": True},
        },
    )

    updated = await _collection().find_one({"_id": plan["_id"]})
    logger.info("Milestone added to plan for goal %s", goal_id)
    return _serialize(updated)


async def update_milestone(
    user_id: str, goal_id: str, milestone_id: str, payload: MilestoneUpdate
) -> dict:
    """Update a specific milestone within a plan."""
    plan = await _get_plan_or_404(user_id, goal_id)
    now = datetime.now(timezone.utc)

    # Find milestone index
    idx = None
    for i, m in enumerate(plan["milestones"]):
        if m["id"] == milestone_id:
            idx = i
            break
    if idx is None:
        raise NotFoundError("Milestone", milestone_id)

    update_fields: dict = {"updated_at": now, "is_customized": True}
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        if key == "target_date" and value is not None:
            value = value.isoformat()
        update_fields[f"milestones.{idx}.{key}"] = value

    await _collection().update_one({"_id": plan["_id"]}, {"$set": update_fields})
    updated = await _collection().find_one({"_id": plan["_id"]})
    logger.info("Milestone %s updated in plan for goal %s", milestone_id, goal_id)
    return _serialize(updated)


async def delete_milestone(
    user_id: str, goal_id: str, milestone_id: str
) -> None:
    """Remove a milestone from a plan."""
    plan = await _get_plan_or_404(user_id, goal_id)
    now = datetime.now(timezone.utc)

    found = any(m["id"] == milestone_id for m in plan["milestones"])
    if not found:
        raise NotFoundError("Milestone", milestone_id)

    await _collection().update_one(
        {"_id": plan["_id"]},
        {
            "$pull": {"milestones": {"id": milestone_id}},
            "$set": {"updated_at": now, "is_customized": True},
        },
    )
    logger.info("Milestone %s deleted from plan for goal %s", milestone_id, goal_id)
