from api.schemas.groups.update_group_schema import *
from domain.entities.group import Group


class UpdateGroupAdapters:
    """
    Class with static methods used for converting request and response to domain objs
    for updating endpoints
    """

    @staticmethod
    def to_update_response(group: Group) -> UpdateGroupResponse:
        return UpdateGroupResponse(
            gid=group.gid,
            name=group.name,
            color=group.color,
            image_url=group.image_url,
            user_count=group.user_count
        )

