from fastapi import APIRouter, Depends, status

from api.adapters.groups.update_group_adapter import UpdateGroupAdapters
from api.schemas.groups.update_group_schema import (UpdateGroupRequest,
                                                    UpdateGroupResponse)
from core.authorization import check_user_role, verify_id_token
from core.dependencies import GroupServiceDep
from domain.entities.group import Group

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.put(
    "/{gid}",
    description="Update group information in Firestore by name (GID)",
    response_model=UpdateGroupResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Group updated successfully"},
        400: {"description": "Bad request - Invalid data or Firestore operation failed"},
        401: {"description": "Unauthorized - Invalid or expired token"},
        404: {"description": "Not found - Group not found in Firestore"},
        500: {"description": "Internal server error"},
    },
)
def update_group(
    gid: str,
    group_update: UpdateGroupRequest,
    group_service: GroupServiceDep,
    user_token=Depends(verify_id_token),
) -> UpdateGroupResponse:

    check_user_role(user_token)
    updated_group: Group = group_service.update_group(gid, group_update.model_dump())
    return UpdateGroupAdapters.to_update_response(updated_group)

