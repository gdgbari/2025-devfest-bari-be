from fastapi import APIRouter, Depends, status

from api.adapters.groups.read_group_adapter import ReadGroupAdapters
from api.schemas.groups.read_group_schema import (GetGroupListResponse,
                                                  GetGroupResponse)
from core.authorization import check_user_role, verify_id_token
from core.dependencies import GroupServiceDep
from domain.entities.user import User
from domain.entities.group import Group

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.get(
    "",
    description="Get all groups from Firestore",
    response_model=GetGroupListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "List of groups retrieved successfully"},
        400: {"description": "Bad request - Firestore operation failed"},
        401: {"description": "Unauthorized - Invalid or expired token"},
        403: {"description": "Forbidden - Insufficient privileges"},
        500: {"description": "Internal server error"},
    },
)
def read_all_groups(
    group_service: GroupServiceDep,
    user_token: User = Depends(verify_id_token),
) -> GetGroupListResponse:
    """
    Get all groups.
    """
    check_user_role(user_token)

    groups: list[Group] = group_service.read_all_groups()
    return ReadGroupAdapters.to_get_groups_response(groups)


@router.get(
    "/{gid}",
    description="Get group by name (GID) from Firestore",
    response_model=GetGroupResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Group retrieved successfully"},
        400: {"description": "Bad request - Firestore operation failed"},
        401: {"description": "Unauthorized - Invalid or expired token"},
        403: {"description": "Forbidden - Insufficient privileges"},
        404: {"description": "Not found - Group not found in Firestore"},
        500: {"description": "Internal server error"},
    },
)
def read_group(
    gid: str,
    group_service: GroupServiceDep,
    user_token=Depends(verify_id_token),
) -> GetGroupResponse:

    check_user_role(user_token)
    group: Group = group_service.read_group(gid)
    return ReadGroupAdapters.to_get_group_response(group)

