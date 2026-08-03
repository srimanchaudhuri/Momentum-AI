"""Onboarding conversation flow routes."""

from fastapi import APIRouter, Depends, status

from middleware.auth import get_current_user
from models.onboarding import (
    AnswerRequest,
    OnboardingSessionResponse,
    OnboardingStartResponse,
    StepResponse,
)
from services import onboarding_service

router = APIRouter()


@router.post(
    "/start",
    response_model=OnboardingStartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new onboarding session",
)
async def start_session(current_user: dict = Depends(get_current_user)):
    return await onboarding_service.start_session(current_user["_id"])


@router.get(
    "/{session_id}",
    response_model=OnboardingSessionResponse,
    summary="Get onboarding session state",
)
async def get_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
):
    return await onboarding_service.get_session(current_user["_id"], session_id)


@router.post(
    "/{session_id}/answer",
    response_model=StepResponse,
    summary="Submit an answer to the current question",
)
async def answer_step(
    session_id: str,
    payload: AnswerRequest,
    current_user: dict = Depends(get_current_user),
):
    return await onboarding_service.answer_step(
        current_user["_id"], session_id, payload.answer
    )


@router.post(
    "/{session_id}/complete",
    response_model=OnboardingSessionResponse,
    summary="Complete onboarding and create a goal",
)
async def complete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
):
    return await onboarding_service.complete_session(current_user["_id"], session_id)
