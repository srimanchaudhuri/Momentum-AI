"""Notification routes."""

from fastapi import APIRouter, Depends, Query

from middleware.auth import get_current_user
from models.notification import NotificationListResponse, NotificationResponse
from services import notification_service

router = APIRouter()


@router.get(
    "/",
    response_model=NotificationListResponse,
    summary="List notifications",
)
async def list_notifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    notifications, total, unread = await notification_service.list_notifications(
        current_user["_id"], page, per_page
    )
    return NotificationListResponse(
        notifications=notifications,
        total=total,
        unread_count=unread,
        page=page,
        per_page=per_page,
    )


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark a notification as read",
)
async def mark_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
):
    return await notification_service.mark_read(current_user["_id"], notification_id)


@router.post(
    "/read-all",
    summary="Mark all notifications as read",
)
async def mark_all_read(current_user: dict = Depends(get_current_user)):
    count = await notification_service.mark_all_read(current_user["_id"])
    return {"marked_read": count}
