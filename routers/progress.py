"""Progress tracking routes."""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from middleware.auth import get_current_user
from models.progress import (
    ProgressLogCreate,
    ProgressLogResponse,
    ProgressSummaryResponse,
)
from services import progress_service

router = APIRouter()


@router.post(
    "/{goal_id}/progress",
    response_model=ProgressLogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log a daily or weekly check-in",
)
async def log_progress(
    goal_id: str,
    payload: ProgressLogCreate,
    current_user: dict = Depends(get_current_user),
):
    return await progress_service.log_progress(current_user["_id"], goal_id, payload)


@router.get(
    "/{goal_id}/progress",
    response_model=list[ProgressLogResponse],
    summary="Get progress history",
)
async def get_progress_history(
    goal_id: str,
    date_from: Optional[date] = Query(None, description="Start date filter"),
    date_to: Optional[date] = Query(None, description="End date filter"),
    current_user: dict = Depends(get_current_user),
):
    return await progress_service.get_progress_history(
        current_user["_id"], goal_id, date_from, date_to
    )


@router.get(
    "/{goal_id}/progress/summary",
    response_model=ProgressSummaryResponse,
    summary="Get aggregated progress stats",
)
async def get_progress_summary(
    goal_id: str,
    current_user: dict = Depends(get_current_user),
):
    return await progress_service.get_progress_summary(current_user["_id"], goal_id)
