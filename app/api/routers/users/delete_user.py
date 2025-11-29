from fastapi import APIRouter, Depends, status

from core.authorization import check_user_role, verify_id_token
from core.dependencies import UserServiceDep
from domain.entities.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.delete(
    "/{uid}",
    description="Delete user from Firebase Auth and Firestore",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "User deleted successfully"},
        400: {"description": "Bad request - Firebase operation failed"},
        401: {"description": "Unauthorized - Invalid or expired token"},
        403: {"description": "Forbidden - Insufficient privileges or not the owner"},
        404: {"description": "Not found - User not found in Firebase Auth or Firestore"},
        500: {"description": "Internal server error"},
    },
)
def delete_user(
    uid: str,
    user_service: UserServiceDep,
    user_token: User = Depends(verify_id_token),
) -> None:
    """
    Delete a user.
    """
    check_user_role(user_token, allow_owner=True, uid=uid)

    user_service.delete_user(uid)
    return None
