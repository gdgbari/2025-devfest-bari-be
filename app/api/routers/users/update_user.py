from fastapi import APIRouter, Depends, status

from api.adapters.users.update_user_adapter import UpdateUserAdapters
from api.schemas.users.update_user_schema import UpdateUserRequest
from api.schemas.users.read_user_schema import GetUserResponse
from api.adapters.users.read_user_adapter import ReadUserAdapters
from core.authorization import check_user_role, verify_id_token
from core.dependencies import UserServiceDep
from domain.entities.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.put(
    "/{uid}",
    description="Update user information in Firebase Auth and Firestore",
    response_model=GetUserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "User updated successfully"},
        400: {"description": "Bad request - Invalid data or Firebase operation failed"},
        401: {"description": "Unauthorized - Invalid or expired token"},
        403: {"description": "Forbidden - Insufficient privileges or not the owner"},
        404: {"description": "Not found - User not found in Firestore"},
        500: {"description": "Internal server error"},
    },
)
def update_user(
    uid: str,
    user_update: UpdateUserRequest,
    user_service: UserServiceDep,
    user_token: User = Depends(verify_id_token),
) -> GetUserResponse:
    """
    Update a user.
    """
    check_user_role(user_token, allow_owner=True, uid=uid)

    updated_user: User = user_service.update_user(uid, user_update.model_dump(exclude_unset=True))
    return ReadUserAdapters.to_get_user_response(updated_user)
