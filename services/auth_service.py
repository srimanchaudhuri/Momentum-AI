"""Authentication business logic — signup, login, token refresh."""

from datetime import datetime, timezone

from bson import ObjectId

from app.database import get_database
from app.exceptions import AuthenticationError, DuplicateError
from app.logger import get_logger
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

logger = get_logger(__name__)


def _users():
    return get_database()["users"]


def _serialize(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc


def _make_tokens(user_id: str) -> dict:
    """Generate access + refresh token pair."""
    return {
        "access_token": create_access_token(user_id),
        "refresh_token": create_refresh_token(user_id),
        "token_type": "bearer",
    }


async def signup(
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    age: int,
) -> dict:
    """Register a new user and return tokens.

    Raises:
        DuplicateError: If email is already taken.
    """
    collection = _users()

    if await collection.find_one({"email": email}):
        raise DuplicateError("A user with this email already exists.")

    now = datetime.now(timezone.utc)
    document = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": hash_password(password),
        "age": age,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }

    result = await collection.insert_one(document)
    user_id = str(result.inserted_id)
    logger.info("User signed up: %s", user_id)

    return _make_tokens(user_id)


async def login(email: str, password: str) -> dict:
    """Verify credentials and return tokens.

    Raises:
        AuthenticationError: If email not found or password doesn't match.
    """
    user = await _users().find_one({"email": email})

    if not user or not verify_password(password, user["password"]):
        raise AuthenticationError("Invalid email or password.")

    if not user.get("is_active", True):
        raise AuthenticationError("Account is deactivated.")

    user_id = str(user["_id"])
    logger.info("User logged in: %s", user_id)

    return _make_tokens(user_id)


async def refresh(refresh_token: str) -> dict:
    """Validate a refresh token and issue a new access token.

    Raises:
        AuthenticationError: If token is invalid, expired, or not a refresh token.
    """
    from jose import JWTError

    try:
        payload = decode_token(refresh_token)
        user_id = payload.get("sub")
        token_type = payload.get("type")

        if not user_id or token_type != "refresh":
            raise AuthenticationError("Invalid refresh token.")
    except JWTError:
        raise AuthenticationError("Refresh token is invalid or expired.")

    # Verify user still exists
    user = await _users().find_one({"_id": ObjectId(user_id)})
    if not user:
        raise AuthenticationError("User not found.")

    return _make_tokens(user_id)


async def get_user_by_id(user_id: str) -> dict:
    """Fetch user by ID (used by auth middleware). Excludes password."""
    user = await _users().find_one({"_id": ObjectId(user_id)})
    if not user:
        raise AuthenticationError("User not found.")
    user = _serialize(user)
    user.pop("password", None)
    return user
