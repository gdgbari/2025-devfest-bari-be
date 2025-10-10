from typing import Annotated
from fastapi import APIRouter, status, Depends

from domain.services.user_service import UserService
from api.dependencies import get_user_service

router = APIRouter(prefix="/users", tags=["Users"])

@router.delete(
    "/{uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "User not found - either in Firebase Auth or Firestore"},
        500: {"description": "Internal server error"},
    },
)
def delete_user(
    uid: str,
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> None:
    """Delete user from Firebase Auth and Firestore"""
    user_service.delete_user(uid)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        500: {"description": "Internal server error"}
    },
)
def delete_all_users(
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> None:
    """Delete all users from Firebase Auth and Firestore (use with caution!)"""
    user_service.delete_all_users()