"""Pydantic schemas for the onboarding conversation flow."""

from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class OnboardingStepResponse(BaseModel):
    """A single step in the onboarding conversation."""

    step_number: int
    question: str
    answer: Optional[str] = None
    answered_at: Optional[datetime] = None


class AnswerRequest(BaseModel):
    """Submit an answer to the current onboarding question."""

    answer: str = Field(..., min_length=1, max_length=2000)


class OnboardingStartResponse(BaseModel):
    """Returned when a new onboarding session begins."""

    session_id: str
    step: OnboardingStepResponse
    total_steps: int


class StepResponse(BaseModel):
    """Returned after answering a question."""

    session_id: str
    answered_step: OnboardingStepResponse
    next_step: Optional[OnboardingStepResponse] = None
    is_complete: bool = False


class OnboardingSessionResponse(BaseModel):
    """Full onboarding session state."""

    id: str = Field(..., alias="_id")
    user_id: str
    status: str
    steps: list[OnboardingStepResponse]
    current_step: int
    goal_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
    )
