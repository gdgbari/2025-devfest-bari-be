from fastapi import APIRouter, Depends, status

from api.adapters.groups.create_group_adapter import CreateGroupAdapter
from api.schemas.groups.create_group_schema import (CreateGroupRequest,
                                                    CreateGroupResponse)
from core.authorization import check_user_role, verify_id_token
from core.dependencies import GroupServiceDep
from domain.entities.group import Group

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.post(
    "",
    description="Endpoint for creating a new Group in database",
    response_model=CreateGroupResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_group(
    request: CreateGroupRequest,
    group_service: GroupServiceDep,
    user_token=Depends(verify_id_token),
) -> CreateGroupResponse:

    check_user_role(user_token)
    new_group: Group = group_service.create_group(
        CreateGroupAdapter.to_create_group_domain(request)
    )
    return CreateGroupAdapter.to_create_group_response(new_group)

