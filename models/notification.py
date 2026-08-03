"""Pydantic schemas for notifications."""

from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class NotificationResponse(BaseModel):
    """Notification document returned to the client."""

    id: str = Field(..., alias="_id")
    user_id: str
    goal_id: str | None = None
    type: str  # daily_reminder, weekly_summary, milestone_reached, deadline_warning, streak_alert
    title: str
    body: str
    is_read: bool = False
    created_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
    )


class NotificationListResponse(BaseModel):
    """Paginated notification list."""

    notifications: list[NotificationResponse]
    total: int
    unread_count: int
    page: int
    per_page: int
