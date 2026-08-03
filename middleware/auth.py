"""Authentication middleware — FastAPI dependency for protected routes."""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.exceptions import AuthenticationError
from app.security import decode_token
from services import user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Extract and verify JWT from the Authorization header.

    Returns the full user document (serialized).
    Raises AuthenticationError if token is invalid/expired or user not found.
    """
    try:
        payload = decode_token(token)
        user_id: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")

        if user_id is None or token_type != "access":
            raise AuthenticationError("Invalid token.")
    except JWTError:
        raise AuthenticationError("Token is invalid or expired.")

    try:
        user = await user_service.get_user_by_id(user_id)
    except Exception:
        raise AuthenticationError("User not found.")

    return user
