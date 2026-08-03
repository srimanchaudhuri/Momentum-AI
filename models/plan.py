"""Pydantic schemas for plans, milestones, and schedules."""

from datetime import date, datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Milestone schemas
# ---------------------------------------------------------------------------

class MilestoneCreate(BaseModel):
    """Schema for adding a milestone to a plan."""

    title: str = Field(..., min_length=1, max_length=200)
    target_date: date
    order: int = Field(1, ge=1)


class MilestoneUpdate(BaseModel):
    """Schema for updating a milestone — all fields optional."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    target_date: Optional[date] = None
    status: Optional[str] = Field(None, pattern=r"^(pending|in_progress|completed)$")
    progress_percent: Optional[float] = Field(None, ge=0, le=100)
    order: Optional[int] = Field(None, ge=1)


class MilestoneResponse(BaseModel):
    """Milestone within a plan."""

    id: str
    title: str
    target_date: date
    status: str = "pending"
    progress_percent: float = 0.0
    order: int


# ---------------------------------------------------------------------------
# Schedule schemas
# ---------------------------------------------------------------------------

class WeeklyPlanItem(BaseModel):
    """A single week in the schedule."""

    week: int
    focus: str
    tasks: list[str] = []
    hours: float = 0.0


class ScheduleCreate(BaseModel):
    """Schema for creating/updating a schedule."""

    hours_per_day: float = Field(..., gt=0, le=24)
    days_per_week: list[str] = Field(..., min_length=1)
    weekly_plan: list[WeeklyPlanItem] = []


# ---------------------------------------------------------------------------
# Plan schemas
# ---------------------------------------------------------------------------

class PlanCreate(BaseModel):
    """Schema for creating a plan for a goal."""

    schedule: ScheduleCreate
    milestones: list[MilestoneCreate] = []


class PlanUpdate(BaseModel):
    """Schema for updating a plan — all fields optional."""

    schedule: Optional[ScheduleCreate] = None


class PlanResponse(BaseModel):
    """Full plan document returned to the client."""

    id: str = Field(..., alias="_id")
    goal_id: str
    user_id: str
    schedule: dict
    milestones: list[MilestoneResponse]
    is_customized: bool = False
    version: int = 1
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
    )
