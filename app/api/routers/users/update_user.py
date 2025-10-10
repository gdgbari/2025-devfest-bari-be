from fastapi import APIRouter, status

from api.adapters.users.update_user_adapter import UpdateUserAdapters
from api.schemas.users.update_user_schema import UpdateUserRequest, UpdateUserResponse
from domain.entities.user import User
from domain.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.put(
    "/{uid}",
    response_model=UpdateUserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Bad request - invalid data or no data to update"},
        404: {"description": "User not found - either in Firebase Auth or Firestore"},
        500: {"description": "Internal server error"},
    },
)
def update_user(uid: str, user_update: UpdateUserRequest) -> UpdateUserResponse:
    """Update user information in Firebase Auth and Firestore"""
    updated_user: User = UserService.update_user(uid, user_update.model_dump())
    return UpdateUserAdapters.to_update_response(updated_user)