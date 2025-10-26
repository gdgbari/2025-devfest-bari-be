from api.adapters.users.read_user_adapter import ReadUserAdapters
from api.schemas.users.read_user_schema import (GetUserListResponse,
                                                GetUserResponse)
from core.authorization import check_user_role, verify_id_token
from core.dependencies import UserServiceDep
from domain.entities.user import User
from fastapi import APIRouter, Depends, status

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    description="Get all users from Firebase Auth and Firestore",
    response_model=GetUserListResponse,
    status_code=status.HTTP_200_OK,
)
def read_all_users(
    user_service: UserServiceDep,
    user_token=Depends(verify_id_token),
) -> GetUserListResponse:

    check_user_role(user_token)
    users: list[User] = user_service.read_all_users()
    return ReadUserAdapters.to_get_users_response(users)


@router.get(
    "/me",
    description="Get current authenticated user from Firebase Auth and Firestore",
    response_model=GetUserResponse,
    status_code=status.HTTP_200_OK,
)
def read_current_user(
    user_service: UserServiceDep,
    user_token=Depends(verify_id_token),
) -> GetUserResponse:

    uid = user_token.uid
    user: User = user_service.read_user(uid)
    return ReadUserAdapters.to_get_user_response(user)


@router.get(
    "/{uid}",
    description="Get user by UID from Firebase Auth and Firestore",
    response_model=GetUserResponse,
    status_code=status.HTTP_200_OK,
)
def read_user(
    uid: str,
    user_service: UserServiceDep,
    user_token=Depends(verify_id_token),
) -> GetUserResponse:

    check_user_role(
        user_token=user_token,
        allow_owner=True,
        uid=uid,
    )
    user: User = user_service.read_user(uid)
    return ReadUserAdapters.to_get_user_response(user)
