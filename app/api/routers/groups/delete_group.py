from fastapi import APIRouter, Depends, status

from core.authorization import check_user_role, verify_id_token
from core.dependencies import GroupServiceDep

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.delete(
    "",
    description="Delete all groups from Firestore (use with caution!)",
    status_code=status.HTTP_204_NO_CONTENT,
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
)
def delete_group(
    gid: str,
    group_service: GroupServiceDep,
    user_token=Depends(verify_id_token),
) -> None:

    check_user_role(user_token)
    group_service.delete_group(gid)

