from api.adapters.users.update_user_adapter import UpdateUserAdapters
from api.schemas.users.update_user_schema import (UpdateUserRequest,
                                                  UpdateUserResponse)
from core.authorization import check_user_role, verify_id_token
from core.dependencies import UserServiceDep
from domain.entities.user import User
from fastapi import APIRouter, Depends, status

router = APIRouter(prefix="/users", tags=["Users"])


@router.put(
    "/{uid}",
    description="Update user information in Firebase Auth and Firestore",
    response_model=UpdateUserResponse,
    status_code=status.HTTP_200_OK,
)
def update_user(
    uid: str,
    user_update: UpdateUserRequest,
    user_service: UserServiceDep,
    user_token=Depends(verify_id_token),
) -> UpdateUserResponse:

    check_user_role(
        user_token=user_token,
        allow_owner=True,
        uid=uid,
    )
    updated_user: User = user_service.update_user(uid, user_update.model_dump())
    return UpdateUserAdapters.to_update_response(updated_user)
