from api.schemas.tags.update_tag_schema import UpdateTagRequest, UpdateTagResponse
from domain.entities.tag import Tag


class UpdateTagAdapter:
    """
    Class with static methods used for converting request and response to domain objs
    for tag updating endpoints
    """

    @staticmethod
    def to_update_response(tag: Tag) -> UpdateTagResponse:
        """Convert Tag domain object to UpdateTagResponse"""
        return UpdateTagResponse(
            tag_id=tag.tag_id,
            points=tag.points
        )

