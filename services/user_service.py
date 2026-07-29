"""Business logic for User CRUD operations."""

from datetime import datetime, timezone

from bson import ObjectId

from app.database import get_database
from app.exceptions import DuplicateError, InvalidIdError, NotFoundError
from app.logger import get_logger
from models.user import UserCreate, UserUpdate

logger = get_logger(__name__)


def _collection():
    return get_database()["users"]


def _serialize(doc: dict) -> dict:
    """Convert MongoDB document to a response-friendly dict."""
    doc["_id"] = str(doc["_id"])
    return doc


def _to_object_id(user_id: str) -> ObjectId:
    """Convert a string to ObjectId or raise InvalidIdError."""
    if not ObjectId.is_valid(user_id):
        raise InvalidIdError(user_id)
    return ObjectId(user_id)


async def create_user(payload: UserCreate) -> dict:
    """Insert a new user. Returns the created document.

    Raises:
        DuplicateError: If a user with the same email already exists.
    """
    collection = _collection()

    if await collection.find_one({"email": payload.email}):
        raise DuplicateError("A user with this email already exists.")

    now = datetime.now(timezone.utc)
    document = {
        **payload.model_dump(),
        "created_at": now,
        "updated_at": now,
    }

    result = await collection.insert_one(document)
    created = await collection.find_one({"_id": result.inserted_id})
    logger.info("User created: %s", result.inserted_id)
    return _serialize(created)


async def get_user_by_id(user_id: str) -> dict:
    """Fetch a single user by ID.

    Raises:
        InvalidIdError: If user_id is not a valid ObjectId.
        NotFoundError: If no user matches the ID.
    """
    oid = _to_object_id(user_id)
    user = await _collection().find_one({"_id": oid})
    if not user:
        raise NotFoundError("User", user_id)
    return _serialize(user)


async def list_users(page: int, per_page: int) -> tuple[list[dict], int]:
    """Return a paginated list of users and the total count."""
    collection = _collection()
    skip = (page - 1) * per_page

    total = await collection.count_documents({})
    cursor = collection.find({}).skip(skip).limit(per_page).sort("created_at", -1)
    users = [_serialize(doc) async for doc in cursor]

    return users, total


async def update_user(user_id: str, payload: UserUpdate) -> dict:
    """Apply a partial update. Returns the updated document.

    Raises:
        InvalidIdError: If user_id is not a valid ObjectId.
        NotFoundError: If no user matches the ID.
    """
    oid = _to_object_id(user_id)
    collection = _collection()

    update_data = payload.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc)

    result = await collection.update_one({"_id": oid}, {"$set": update_data})

    if result.matched_count == 0:
        raise NotFoundError("User", user_id)

    updated = await collection.find_one({"_id": oid})
    logger.info("User updated: %s", user_id)
    return _serialize(updated)


async def delete_user(user_id: str) -> None:
    """Delete a user by ID.

    Raises:
        InvalidIdError: If user_id is not a valid ObjectId.
        NotFoundError: If no user matches the ID.
    """
    oid = _to_object_id(user_id)
    result = await _collection().delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise NotFoundError("User", user_id)
    logger.info("User deleted: %s", user_id)
