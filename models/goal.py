"""Pydantic schemas for Goal CRUD operations."""

from datetime import date, datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class GoalCreate(BaseModel):
    """Schema for creating a new goal."""

    title: str = Field(..., min_length=1, max_length=200, examples=["Learn Machine Learning"])
    description: Optional[str] = Field(None, max_length=2000)
    target_date: date = Field(..., examples=["2026-11-01"])


class GoalUpdate(BaseModel):
    """Schema for updating a goal — all fields optional."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    target_date: Optional[date] = None
    status: Optional[str] = Field(None, pattern=r"^(active|paused|completed|abandoned)$")


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class GoalResponse(BaseModel):
    """Full goal document returned to the client."""

    id: str = Field(..., alias="_id")
    user_id: str
    title: str
    description: Optional[str] = None
    timeline: dict
    status: str
    progress_percent: float
    onboarding_session_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
    )


class GoalListResponse(BaseModel):
    """Paginated goal list."""

    goals: list[GoalResponse]
    total: int
    page: int
    per_page: int
