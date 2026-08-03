"""Pydantic schemas for progress tracking."""

from datetime import date, datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class MilestoneProgress(BaseModel):
    """Progress update for a single milestone."""

    milestone_id: str
    progress_percent: float = Field(..., ge=0, le=100)


class ProgressLogCreate(BaseModel):
    """Schema for logging a daily/weekly check-in."""

    type: str = Field("daily", pattern=r"^(daily|weekly)$")
    hours_spent: float = Field(..., ge=0, le=24)
    tasks_completed: list[str] = []
    milestone_updates: list[MilestoneProgress] = []
    mood: Optional[str] = Field(
        None,
        pattern=r"^(motivated|neutral|struggling|burnt_out)$",
    )
    notes: Optional[str] = Field(None, max_length=2000)


class ProgressLogResponse(BaseModel):
    """Progress log document returned to the client."""

    id: str = Field(..., alias="_id")
    goal_id: str
    user_id: str
    type: str
    date: date
    entries: dict
    ai_feedback: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
    )


class ProgressSummaryResponse(BaseModel):
    """Aggregated progress stats for a goal."""

    goal_id: str
    total_hours: float
    total_logs: int
    avg_hours_per_log: float
    streak_days: int
    tasks_completed_count: int
    progress_percent: float
    mood_distribution: dict  # {"motivated": 5, "neutral": 3, ...}
