"""User routes — profile management (creation handled by /api/auth/signup)."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from middleware.auth import get_current_user
from models.user import UserListResponse, UserResponse, UserUpdate
from services import user_service

router = APIRouter()


# ---------------------------------------------------------------------------
# READ (single)
# ---------------------------------------------------------------------------

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a user by ID",
)
async def get_user(
    user_id: str,
    _current_user: dict = Depends(get_current_user),
):
    return await user_service.get_user_by_id(user_id)


# ---------------------------------------------------------------------------
# READ (list with pagination)
# ---------------------------------------------------------------------------

@router.get(
    "/",
    response_model=UserListResponse,
    summary="List users with pagination",
)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    _current_user: dict = Depends(get_current_user),
):
    users, total = await user_service.list_users(page, per_page)
    return UserListResponse(users=users, total=total, page=page, per_page=per_page)


# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------

@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update a user",
)
async def update_user(
    user_id: str,
    payload: UserUpdate,
    _current_user: dict = Depends(get_current_user),
):
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No fields provided for update.",
        )
    return await user_service.update_user(user_id, payload)


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
)
async def delete_user(
    user_id: str,
    _current_user: dict = Depends(get_current_user),
):
    await user_service.delete_user(user_id)