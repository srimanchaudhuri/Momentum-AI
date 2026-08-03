"""Dashboard routes — aggregated analytics."""

from fastapi import APIRouter, Depends

from middleware.auth import get_current_user
from models.dashboard import DashboardResponse, GoalDashboard
from services import dashboard_service

router = APIRouter()


@router.get(
    "/",
    response_model=DashboardResponse,
    summary="Get full dashboard for current user",
)
async def get_dashboard(current_user: dict = Depends(get_current_user)):
    return await dashboard_service.get_dashboard(current_user["_id"])


@router.get(
    "/goals/{goal_id}",
    response_model=GoalDashboard,
    summary="Get detailed analytics for a single goal",
)
async def get_goal_dashboard(
    goal_id: str,
    current_user: dict = Depends(get_current_user),
):
    return await dashboard_service.get_goal_dashboard(current_user["_id"], goal_id)
