from fastapi import APIRouter, Depends, status

from api.adapters.groups.update_group_adapter import UpdateGroupAdapters
from api.schemas.groups.update_group_schema import UpdateGroupRequest
from api.schemas.groups.read_group_schema import GetGroupResponse
from api.adapters.groups.read_group_adapter import ReadGroupAdapters
from core.authorization import check_user_role, verify_id_token
from core.dependencies import GroupServiceDep
from domain.entities.group import Group
from domain.entities.user import User

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.put(
    "/{gid}",
    description="Update group information in Firestore by name (GID)",
    response_model=GetGroupResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Group updated successfully"},
        400: {"description": "Bad request - Invalid data or Firestore operation failed"},
        401: {"description": "Unauthorized - Invalid or expired token"},
        403: {"description": "Forbidden - Insufficient privileges"},
        404: {"description": "Not found - Group not found in Firestore"},
        500: {"description": "Internal server error"},
    },
)
def update_group(
    group_id: str,
    group_update: UpdateGroupRequest,
    group_service: GroupServiceDep,
    user_token: User = Depends(verify_id_token),
) -> GetGroupResponse:
    """
    Update a group.
    """
    check_user_role(user_token)

    updated_group: Group = group_service.update_group(group_id, group_update.model_dump(exclude_unset=True))
    return ReadGroupAdapters.to_get_group_response(updated_group)
