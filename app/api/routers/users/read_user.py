from fastapi import APIRouter, status

from api.adapters.users.read_user_adapter import ReadUserAdapters
from api.schemas.users.read_user_schema import GetUserResponse, GetUserListResponse
from domain.entities.user import User
from domain.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.get(
    "",
    response_model=GetUserListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        500: {"description": "Internal server error"}
    },
)
def read_all_users() -> GetUserListResponse:
    """Get all users from Firebase Auth and Firestore"""
    users: list[User] = UserService.read_all_users()
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
def read_user(uid: str) -> GetUserResponse:
    """Get user by UID from Firebase Auth and Firestore"""
    user: User = UserService.read_user(uid)
    return ReadUserAdapters.to_get_user_response(user)