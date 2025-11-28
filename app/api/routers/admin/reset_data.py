from fastapi import APIRouter, Depends, status, HTTPException
from core.dependencies import get_admin_service
from domain.services.admin_service import AdminService
from core.authorization import verify_id_token, check_user_role
from domain.entities.role import Role

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post(
    "/reset-data",
    status_code=status.HTTP_200_OK,
    description="Reset all data: leaderboard, tags, quiz results",
    responses={
        200: {"description": "Data reset successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Insufficient privileges"},
        500: {"description": "Internal server error"},
    }
)
def reset_data(
    admin_service: AdminService = Depends(get_admin_service),
    user_token=Depends(verify_id_token),
):
    """
    Resets all data in the system.
    """
    # Check if user is admin
    check_user_role(user_token)

    admin_service.reset_all_data()

    return {"message": "All data has been reset successfully"}
