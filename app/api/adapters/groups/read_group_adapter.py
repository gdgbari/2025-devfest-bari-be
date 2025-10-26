from api.schemas.groups.read_group_schema import *
from domain.entities.group import Group


class ReadGroupAdapters:
    """
    Class with static methods used for converting request and response to domain objs
    for reading endpoints
    """

    @staticmethod
    def to_get_group_response(group: Group) -> GetGroupResponse:
        return GetGroupResponse(
            gid=group.gid,
            name=group.name,
            color=group.color,
            image_url=group.image_url,
            user_count=group.user_count
        )

    @staticmethod
    def to_get_groups_response(
        groups: list[Group],
    ) -> GetGroupListResponse:
        return GetGroupListResponse(
            groups=[
                ReadGroupAdapters.to_get_group_response(group)
                for group in groups
            ],
            total=len(groups),
        )

