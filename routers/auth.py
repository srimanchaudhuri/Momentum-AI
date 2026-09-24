"""Authentication routes — signup, login, refresh, me."""

import email
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from middleware.auth import get_current_user
from models.auth import LoginRequest, RefreshRequest, SignupRequest, TokenResponse
from models.user import UserResponse
from services import auth_service

router = APIRouter()


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account",
)
async def signup(payload: SignupRequest):
    return await auth_service.signup(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        password=payload.password,
        age=payload.age,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):

    return await auth_service.login(
        email=form_data.username,
        password=form_data.password 
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
async def refresh(payload: RefreshRequest):
    return await auth_service.refresh(refresh_token=payload.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def me(current_user: dict = Depends(get_current_user)):
    return current_user
