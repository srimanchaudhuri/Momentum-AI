"""Business logic for learning resource management."""

from datetime import datetime, timezone

from bson import ObjectId

from app.database import get_database
from app.exceptions import AuthorizationError, InvalidIdError, NotFoundError
from app.logger import get_logger
from models.resource import ResourceCreate, ResourceUpdate

logger = get_logger(__name__)


def _collection():
    return get_database()["resources"]


def _serialize(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    doc["plan_id"] = str(doc["plan_id"])
    doc["goal_id"] = str(doc["goal_id"])
    return doc


def _to_oid(value: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise InvalidIdError(value)
    return ObjectId(value)


async def _verify_goal_ownership(user_id: str, goal_id: str) -> None:
    goal = await get_database()["goals"].find_one({"_id": _to_oid(goal_id)})
    if not goal:
        raise NotFoundError("Goal", goal_id)
    if str(goal["user_id"]) != user_id:
        raise AuthorizationError()


async def create_resource(
    user_id: str, goal_id: str, payload: ResourceCreate
) -> dict:
    """Add a resource to a goal."""
    await _verify_goal_ownership(user_id, goal_id)
    goid = _to_oid(goal_id)

    # Get plan_id if exists
    plan = await get_database()["plans"].find_one({"goal_id": goid})
    plan_id = plan["_id"] if plan else goid  # fallback to goal_id

    now = datetime.now(timezone.utc)
    document = {
        "plan_id": plan_id,
        "goal_id": goid,
        **payload.model_dump(),
        "is_selected": True,
        "created_at": now,
    }

    result = await _collection().insert_one(document)
    created = await _collection().find_one({"_id": result.inserted_id})
    logger.info("Resource added to goal %s", goal_id)
    return _serialize(created)


async def list_resources(user_id: str, goal_id: str) -> list[dict]:
    """List all resources for a goal."""
    await _verify_goal_ownership(user_id, goal_id)
    goid = _to_oid(goal_id)

    cursor = _collection().find({"goal_id": goid}).sort("order", 1)
    return [_serialize(doc) async for doc in cursor]


async def update_resource(
    user_id: str, goal_id: str, resource_id: str, payload: ResourceUpdate
) -> dict:
    """Update a resource (toggle selection, reorder, etc.)."""
    await _verify_goal_ownership(user_id, goal_id)
    rid = _to_oid(resource_id)

    resource = await _collection().find_one({"_id": rid, "goal_id": _to_oid(goal_id)})
    if not resource:
        raise NotFoundError("Resource", resource_id)

    update_data = payload.model_dump(exclude_unset=True)
    if update_data:
        # Serialize cost if present
        if "cost" in update_data and update_data["cost"] is not None:
            update_data["cost"] = update_data["cost"]
        await _collection().update_one({"_id": rid}, {"$set": update_data})

    updated = await _collection().find_one({"_id": rid})
    logger.info("Resource %s updated", resource_id)
    return _serialize(updated)


async def delete_resource(
    user_id: str, goal_id: str, resource_id: str
) -> None:
    """Delete a resource."""
    await _verify_goal_ownership(user_id, goal_id)
    rid = _to_oid(resource_id)

    result = await _collection().delete_one({"_id": rid, "goal_id": _to_oid(goal_id)})
    if result.deleted_count == 0:
        raise NotFoundError("Resource", resource_id)
    logger.info("Resource %s deleted", resource_id)
