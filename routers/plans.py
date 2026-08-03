"""Plan, milestone, and resource routes."""

from fastapi import APIRouter, Depends, status

from middleware.auth import get_current_user
from models.plan import (
    MilestoneCreate,
    MilestoneUpdate,
    PlanCreate,
    PlanResponse,
    PlanUpdate,
)
from models.resource import ResourceCreate, ResourceResponse, ResourceUpdate
from services import plan_service, resource_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Plan
# ---------------------------------------------------------------------------

@router.post(
    "/{goal_id}/plan",
    response_model=PlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a plan for a goal",
)
async def create_plan(
    goal_id: str,
    payload: PlanCreate,
    current_user: dict = Depends(get_current_user),
):
    return await plan_service.create_plan(current_user["_id"], goal_id, payload)


@router.get(
    "/{goal_id}/plan",
    response_model=PlanResponse,
    summary="Get the plan for a goal",
)
async def get_plan(
    goal_id: str,
    current_user: dict = Depends(get_current_user),
):
    return await plan_service.get_plan(current_user["_id"], goal_id)


@router.patch(
    "/{goal_id}/plan",
    response_model=PlanResponse,
    summary="Update plan schedule",
)
async def update_plan(
    goal_id: str,
    payload: PlanUpdate,
    current_user: dict = Depends(get_current_user),
):
    return await plan_service.update_plan(current_user["_id"], goal_id, payload)


# ---------------------------------------------------------------------------
# Milestones
# ---------------------------------------------------------------------------

@router.post(
    "/{goal_id}/plan/milestones",
    response_model=PlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a milestone",
)
async def add_milestone(
    goal_id: str,
    payload: MilestoneCreate,
    current_user: dict = Depends(get_current_user),
):
    return await plan_service.add_milestone(current_user["_id"], goal_id, payload)


@router.patch(
    "/{goal_id}/plan/milestones/{milestone_id}",
    response_model=PlanResponse,
    summary="Update a milestone",
)
async def update_milestone(
    goal_id: str,
    milestone_id: str,
    payload: MilestoneUpdate,
    current_user: dict = Depends(get_current_user),
):
    return await plan_service.update_milestone(
        current_user["_id"], goal_id, milestone_id, payload
    )


@router.delete(
    "/{goal_id}/plan/milestones/{milestone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a milestone",
)
async def delete_milestone(
    goal_id: str,
    milestone_id: str,
    current_user: dict = Depends(get_current_user),
):
    await plan_service.delete_milestone(current_user["_id"], goal_id, milestone_id)


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------

@router.post(
    "/{goal_id}/resources",
    response_model=ResourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a resource",
)
async def create_resource(
    goal_id: str,
    payload: ResourceCreate,
    current_user: dict = Depends(get_current_user),
):
    return await resource_service.create_resource(current_user["_id"], goal_id, payload)


@router.get(
    "/{goal_id}/resources",
    response_model=list[ResourceResponse],
    summary="List resources for a goal",
)
async def list_resources(
    goal_id: str,
    current_user: dict = Depends(get_current_user),
):
    return await resource_service.list_resources(current_user["_id"], goal_id)


@router.patch(
    "/{goal_id}/resources/{resource_id}",
    response_model=ResourceResponse,
    summary="Update a resource",
)
async def update_resource(
    goal_id: str,
    resource_id: str,
    payload: ResourceUpdate,
    current_user: dict = Depends(get_current_user),
):
    return await resource_service.update_resource(
        current_user["_id"], goal_id, resource_id, payload
    )


@router.delete(
    "/{goal_id}/resources/{resource_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a resource",
)
async def delete_resource(
    goal_id: str,
    resource_id: str,
    current_user: dict = Depends(get_current_user),
):
    await resource_service.delete_resource(current_user["_id"], goal_id, resource_id)
