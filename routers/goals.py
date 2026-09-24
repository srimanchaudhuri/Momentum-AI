"""Goal CRUD routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from middleware.auth import get_current_user
from models.goal import GoalCreate, GoalListResponse, GoalResponse, GoalUpdate
from services import goal_service

router = APIRouter()


@router.post(
    "/",
    response_model=GoalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new goal",
)
async def create_goal(
    payload: GoalCreate,
    current_user: dict = Depends(get_current_user),
):
    return await goal_service.create_goal(current_user["_id"], payload)


@router.get(
    "/",
    response_model=GoalListResponse,
    summary="List your goals",
)
async def list_goals(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    goals, total = await goal_service.list_goals(current_user["_id"], page, per_page)
    return GoalListResponse(goals=goals, total=total, page=page, per_page=per_page)


@router.get(
    "/{goal_id}",
    response_model=GoalResponse,
    summary="Get a goal by ID",
)
async def get_goal(
    goal_id: str,
    current_user: dict = Depends(get_current_user),
):
    return await goal_service.get_goal(current_user["_id"], goal_id)


@router.patch(
    "/{goal_id}",
    response_model=GoalResponse,
    summary="Update a goal",
)
async def update_goal(
    goal_id: str,
    payload: GoalUpdate,
    current_user: dict = Depends(get_current_user),
):
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No fields provided for update.",
        )
    return await goal_service.update_goal(current_user["_id"], goal_id, payload)


@router.delete(
    "/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a goal",
)
async def delete_goal(
    goal_id: str,
    current_user: dict = Depends(get_current_user),
):
    await goal_service.delete_goal(current_user["_id"], goal_id)