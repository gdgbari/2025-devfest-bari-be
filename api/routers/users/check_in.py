from fastapi import APIRouter, Depends, status

from api.adapters.users.check_in_adapter import CheckInAdapter
from api.schemas.users.check_in_schema import CheckInResponse
from core.authorization import verify_id_token, check_user_checked_in
from core.dependencies import CheckInServiceDep
from domain.entities.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/check-in",
    description="Assign a group to the current authenticated user using round-robin",
    response_model=CheckInResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Group assigned successfully"},
        400: {"description": "Bad request - No groups available or assignment failed"},
        401: {"description": "Unauthorized - Invalid or expired token"},
        403: {"description": "Forbidden - Check-in is closed or user has insufficient permissions"},
        404: {"description": "Not found - User not found"},
        500: {"description": "Internal server error"},
    },
)
def assign_group_to_current_user(
    check_in_service: CheckInServiceDep,
    user_token=Depends(verify_id_token),
) -> CheckInResponse:
    """
    Assigns a group to the current user.
    """
    check_user_checked_in(user_token=user_token, is_checked_in=False)
    uid = user_token.uid

    updated_user: User = check_in_service.check_in(uid=uid)

    return CheckInAdapter.to_response(updated_user)
