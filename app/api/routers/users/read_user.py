from typing import Annotated
from fastapi import APIRouter, status, Depends

from api.adapters.users.read_user_adapter import ReadUserAdapters
from api.schemas.users.read_user_schema import GetUserResponse, GetUserListResponse
from domain.entities.user import User
from domain.services.user_service import UserService
from core.dependencies import get_user_service
from core.authorization import authorize

router = APIRouter(
    prefix="/users",
    dependencies=[Depends(authorize())],
    tags=["Users"])

@router.get(
    "",
    description="Get all users from Firebase Auth and Firestore",
    response_model=GetUserListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        500: {"description": "Internal server error"}
    },
)
def read_all_users(
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> GetUserListResponse:

    users: list[User] = user_service.read_all_users()
    return ReadUserAdapters.to_get_users_response(users)


@router.get(
    "/{uid}",
    description="Get user by UID from Firebase Auth and Firestore",
    response_model=GetUserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "User not found - either in Firebase Auth or Firestore"},
        500: {"description": "Internal server error"},
    },
)
def read_user(
    uid: str,
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> GetUserResponse:

    user: User = user_service.read_user(uid)
    return ReadUserAdapters.to_get_user_response(user)
