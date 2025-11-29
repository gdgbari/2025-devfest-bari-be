from fastapi import APIRouter, Depends, status

from core.authorization import check_user_role, verify_id_token
from core.dependencies import GroupServiceDep
from domain.entities.user import User

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.delete(
    "",
    description="Delete all groups from Firestore (use with caution!)",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "All groups deleted successfully"},
        400: {"description": "Bad request - Firestore operation failed"},
        401: {"description": "Unauthorized - Invalid or expired token"},
        403: {"description": "Forbidden - Insufficient privileges"},
        500: {"description": "Internal server error"},
    },
)
def delete_all_groups(
    group_service: GroupServiceDep,
    user_token=Depends(verify_id_token),
) -> None:

    check_user_role(user_token)
    group_service.delete_all_groups()


@router.delete(
    "/{gid}",
    description="Delete group from Firestore by name (GID)",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Group deleted successfully"},
        400: {"description": "Bad request - Firestore operation failed"},
        401: {"description": "Unauthorized - Invalid or expired token"},
        403: {"description": "Forbidden - Insufficient privileges"},
        404: {"description": "Not found - Group not found in Firestore"},
        500: {"description": "Internal server error"},
    },
)
def delete_group(
    gid: str,
    group_service: GroupServiceDep,
    user_token: User = Depends(verify_id_token),
) -> None:
    """
    Delete a group.
    """
    check_user_role(user_token)

    group_service.delete_group(group_id)
    return None
