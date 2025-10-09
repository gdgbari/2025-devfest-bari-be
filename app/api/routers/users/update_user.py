from typing import Annotated
from fastapi import APIRouter, status, Depends

from api.adapters.users.update_user_adapter import UpdateUserAdapters
from api.schemas.users.update_user_schema import UpdateUserRequest, UpdateUserResponse
from domain.entities.user import User
from domain.services.user_service import UserService
from core.dependencies import get_user_service
from core.authorization import authorize

router = APIRouter(
    prefix="/users",
    dependencies=[Depends(authorize())],
    tags=["Users"])

@router.put(
    "/{uid}",
    description="Update user information in Firebase Auth and Firestore",
    response_model=UpdateUserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Bad request - invalid data or no data to update"},
        404: {"description": "User not found - either in Firebase Auth or Firestore"},
        500: {"description": "Internal server error"},
    },
)
def update_user(
    uid: str,
    user_update: UpdateUserRequest,
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> UpdateUserResponse:

    updated_user: User = user_service.update_user(uid, user_update.model_dump())
    return UpdateUserAdapters.to_update_response(updated_user)
