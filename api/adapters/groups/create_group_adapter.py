from api.schemas.groups.create_group_schema import *
from domain.entities.group import Group


class CreateGroupAdapter:
    """
    Class with static methods used for converting request and response to domain objs
    for creation endpoints
    """

    @staticmethod
    def to_create_group_domain(group: CreateGroupRequest) -> Group:
        return Group(
            name=group.name,
            color=group.color,
            image_url=group.image_url,
            user_count=group.user_count
        )

    @staticmethod
    def to_create_group_response(group: Group) -> CreateGroupResponse:
        return CreateGroupResponse(
            gid=group.gid,
            name=group.name,
            color=group.color,
            image_url=group.image_url,
            user_count=group.user_count
        )

