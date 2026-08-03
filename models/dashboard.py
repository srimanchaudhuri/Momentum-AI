"""Pydantic schemas for the dashboard API."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class CurrentMilestone(BaseModel):
    """The milestone the user is currently working on."""

    title: str
    progress_percent: float


class ProgressPoint(BaseModel):
    """A single data point in the progress history chart."""

    date: date
    percent: float


class GoalDashboard(BaseModel):
    """Dashboard data for a single goal."""

    goal_id: str
    title: str
    progress_percent: float
    hiker_position: float = Field(
        ..., ge=0.0, le=1.0,
        description="0.0 = base of mountain, 1.0 = peak",
    )
    days_remaining: int
    eta: Optional[date] = None
    deadline: date
    on_track: bool
    streak_days: int = 0
    current_milestone: Optional[CurrentMilestone] = None
    weekly_hours: list[float] = []
    progress_history: list[ProgressPoint] = []


class TodaySummary(BaseModel):
    """What needs attention today."""

    pending_checkins: list[str] = []  # goal titles that need check-in
    tasks_due: list[str] = []


class DashboardResponse(BaseModel):
    """Full dashboard response for the current user."""

    active_goals: int
    goals: list[GoalDashboard]
    today: TodaySummary
