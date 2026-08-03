"""Pydantic schemas for authentication."""

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """Schema for user registration."""

    first_name: str = Field(..., min_length=1, max_length=50, examples=["Sriman"])
    last_name: str = Field(..., min_length=1, max_length=50, examples=["Chaudhuri"])
    email: EmailStr = Field(..., examples=["user@example.com"])
    password: str = Field(..., min_length=8, max_length=72)
    age: int = Field(..., ge=1, le=150)


class LoginRequest(BaseModel):
    """Schema for user login."""

    email: EmailStr = Field(..., examples=["user@example.com"])
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """JWT token pair returned after login/signup."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Schema for refreshing an access token."""

    refresh_token: str
