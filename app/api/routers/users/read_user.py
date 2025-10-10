from typing import Annotated
from fastapi import APIRouter, status, Depends

from api.adapters.users.read_user_adapter import ReadUserAdapters
from api.schemas.users.read_user_schema import GetUserResponse, GetUserListResponse
from domain.entities.user import User
from domain.services.user_service import UserService
from api.dependencies import get_user_service

router = APIRouter(prefix="/users", tags=["Users"])

@router.get(
    "",
    response_model=GetUserListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        500: {"description": "Internal server error"}
    },
)
def read_all_users(
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> GetUserListResponse:
    
    """Get all users from Firebase Auth and Firestore"""
    users: list[User] = user_service.read_all_users()
    return ReadUserAdapters.to_get_users_response(users)


@router.get(
    "/{uid}",
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
    
    """Get user by UID from Firebase Auth and Firestore"""
    user: User = user_service.read_user(uid)
    return ReadUserAdapters.to_get_user_response(user)