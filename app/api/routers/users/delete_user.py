from fastapi import APIRouter, Depends, status

from core.authorization import check_user_role, verify_id_token
from core.dependencies import UserServiceDep

router = APIRouter(prefix="/users", tags=["Users"])


@router.delete(
    "",
    description="Delete all users from Firebase Auth and Firestore (use with caution!)",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_all_users(
    user_service: UserServiceDep,
    user_token=Depends(verify_id_token),
) -> None:

    check_user_role(user_token)
    user_service.delete_all_users()


@router.delete(
    "/{uid}",
    description="Delete user from Firebase Auth and Firestore",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    uid: str,
    user_service: UserServiceDep,
    user_token=Depends(verify_id_token),
) -> None:

    check_user_role(
        user_token=user_token,
        allow_owner=True,
        uid=uid,
    )
    user_service.delete_user(uid)
