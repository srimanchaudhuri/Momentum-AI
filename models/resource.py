"""Pydantic schemas for learning resources."""

from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class CostInfo(BaseModel):
    """Cost information for a resource."""

    amount: float = Field(0.0, ge=0)
    currency: str = Field("USD", max_length=3)


class ResourceCreate(BaseModel):
    """Schema for adding a resource to a goal."""

    title: str = Field(..., min_length=1, max_length=300)
    type: str = Field(..., pattern=r"^(course|book|tool|article|video)$")
    url: Optional[str] = Field(None, max_length=2000)
    provider: Optional[str] = Field(None, max_length=100)
    cost: CostInfo = CostInfo()
    is_free: bool = True
    ai_reason: Optional[str] = Field(None, max_length=500)
    order: int = Field(1, ge=1)


class ResourceUpdate(BaseModel):
    """Schema for updating a resource — all fields optional."""

    title: Optional[str] = Field(None, min_length=1, max_length=300)
    type: Optional[str] = Field(None, pattern=r"^(course|book|tool|article|video)$")
    url: Optional[str] = Field(None, max_length=2000)
    provider: Optional[str] = Field(None, max_length=100)
    cost: Optional[CostInfo] = None
    is_free: Optional[bool] = None
    is_selected: Optional[bool] = None
    order: Optional[int] = Field(None, ge=1)


class ResourceResponse(BaseModel):
    """Resource document returned to the client."""

    id: str = Field(..., alias="_id")
    plan_id: str
    goal_id: str
    title: str
    type: str
    url: Optional[str] = None
    provider: Optional[str] = None
    cost: CostInfo
    is_free: bool
    is_selected: bool = True
    ai_reason: Optional[str] = None
    order: int
    created_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
    )
