"""Business logic for notification management."""

from datetime import datetime, timezone

from bson import ObjectId

from app.database import get_database
from app.exceptions import InvalidIdError, NotFoundError
from app.logger import get_logger

logger = get_logger(__name__)


def _collection():
    return get_database()["notifications"]


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


async def create_notification(
    user_id: str,
    type: str,
    title: str,
    body: str,
    goal_id: str | None = None,
) -> dict:
    """Create a notification for a user."""
    now = datetime.now(timezone.utc)
    document = {
        "user_id": ObjectId(user_id),
        "goal_id": ObjectId(goal_id) if goal_id else None,
        "type": type,
        "title": title,
        "body": body,
        "is_read": False,
        "created_at": now,
    }

    result = await _collection().insert_one(document)
    created = await _collection().find_one({"_id": result.inserted_id})
    logger.info("Notification created for user %s: %s", user_id, type)
    return _serialize(created)


async def list_notifications(
    user_id: str, page: int, per_page: int
) -> tuple[list[dict], int, int]:
    """List notifications for a user (unread first). Returns (items, total, unread_count)."""
    uid = ObjectId(user_id)
    skip = (page - 1) * per_page

    total = await _collection().count_documents({"user_id": uid})
    unread_count = await _collection().count_documents({"user_id": uid, "is_read": False})

    cursor = (
        _collection()
        .find({"user_id": uid})
        .sort([("is_read", 1), ("created_at", -1)])
        .skip(skip)
        .limit(per_page)
    )
    notifications = [_serialize(doc) async for doc in cursor]

    return notifications, total, unread_count


async def mark_read(user_id: str, notification_id: str) -> dict:
    """Mark a single notification as read."""
    nid = _to_oid(notification_id)
    uid = ObjectId(user_id)

    result = await _collection().update_one(
        {"_id": nid, "user_id": uid},
        {"$set": {"is_read": True}},
    )
    if result.matched_count == 0:
        raise NotFoundError("Notification", notification_id)

    updated = await _collection().find_one({"_id": nid})
    return _serialize(updated)


async def mark_all_read(user_id: str) -> int:
    """Mark all notifications as read. Returns count updated."""
    uid = ObjectId(user_id)
    result = await _collection().update_many(
        {"user_id": uid, "is_read": False},
        {"$set": {"is_read": True}},
    )
    logger.info("Marked %d notifications as read for user %s", result.modified_count, user_id)
    return result.modified_count
