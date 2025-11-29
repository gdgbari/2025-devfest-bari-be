from fastapi import APIRouter, Depends, status

from api.adapters.users.read_user_adapter import ReadUserAdapters
from api.schemas.users.read_user_schema import GetUserResponse
from core.authorization import verify_id_token, check_user_checked_in, check_user_role
from core.dependencies import CheckInServiceDep
from domain.entities.user import User
from domain.entities.role import Role

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/check-in",
    description="Assign a group to the current authenticated user using round-robin",
    response_model=GetUserResponse,
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
    user_token: User = Depends(verify_id_token),
) -> GetUserResponse:
    """
    Check in a user.
    """
    check_user_role(user_token, min_role=Role.ATTENDEE)
    
    # Check if user has already checked in
    check_user_checked_in(user_token, is_checked_in=False)

    user = check_in_service.check_in(user_token.uid)
    return ReadUserAdapters.to_get_user_response(user)
