from typing import Annotated
from fastapi import APIRouter, status, Depends

from domain.services.user_service import UserService
from core.dependencies import get_user_service
from core.authorization import authorize
from domain.entities.role import Role

router = APIRouter(
    prefix="/users",
    dependencies=[Depends(authorize(min_role=Role.STAFF))],
    tags=["Users"])

@router.delete(
    "/{uid}",
    description="Delete user from Firebase Auth and Firestore",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "User not found - either in Firebase Auth or Firestore"},
        400: {"description": "Error during deletion"},
        500: {"description": "Internal server error"},
    },
)
def delete_user(
    uid: str,
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> None:

    user_service.delete_user(uid)


@router.delete(
    "",
    description="Delete all users from Firebase Auth and Firestore (use with caution!)",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        400: {"description": "Error during deletion"},
        500: {"description": "Internal server error"}
    },
)
def delete_all_users(
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> None:

    user_service.delete_all_users()
