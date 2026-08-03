"""Pydantic schemas for User CRUD operations."""

from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------------------------------------------------------------------------
# Request schemas (what the client sends)
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    """Schema for creating a new user."""

    first_name: str = Field(..., min_length=1, max_length=50, examples=["Sriman"])
    last_name: str = Field(..., min_length=1, max_length=50, examples=["Chaudhuri"])
    email: EmailStr = Field(..., examples=["user@example.com"])
    password: str = Field(..., min_length=8, max_length=72)
    age: int = Field(..., ge=1, le=150)


class UserUpdate(BaseModel):
    """Schema for updating a user — all fields optional."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=1, le=150)


# ---------------------------------------------------------------------------
# Response schemas (what the API returns)
# ---------------------------------------------------------------------------

class UserResponse(BaseModel):
    """Schema returned to the client — never includes the password."""

    id: str = Field(..., alias="_id")
    first_name: str
    last_name: str
    email: str
    age: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
    )


class UserListResponse(BaseModel):
    """Paginated list response."""

    users: list[UserResponse]
    total: int
    page: int
    per_page: int