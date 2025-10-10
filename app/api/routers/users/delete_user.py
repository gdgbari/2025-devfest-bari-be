from fastapi import APIRouter, status

from domain.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.delete(
    "/{uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "User not found - either in Firebase Auth or Firestore"},
        500: {"description": "Internal server error"},
    },
)
def delete_user(uid: str) -> None:
    """Delete user from Firebase Auth and Firestore"""
    UserService.delete_user(uid)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        500: {"description": "Internal server error"}
    },
)
def delete_all_users() -> None:
    """Delete all users from Firebase Auth and Firestore (use with caution!)"""
    UserService.delete_all_users()