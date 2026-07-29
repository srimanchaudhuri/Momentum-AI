"""User CRUD routes."""

from fastapi import APIRouter, HTTPException, Query, status

from models.user import UserCreate, UserListResponse, UserResponse, UserUpdate
from services import user_service

router = APIRouter()


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
async def create_user(payload: UserCreate):
    return await user_service.create_user(payload)


# ---------------------------------------------------------------------------
# READ (single)
# ---------------------------------------------------------------------------

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a user by ID",
)
async def get_user(user_id: str):
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
async def update_user(user_id: str, payload: UserUpdate):
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
async def delete_user(user_id: str):
    await user_service.delete_user(user_id)