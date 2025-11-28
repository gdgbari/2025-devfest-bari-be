from api.schemas.tags.create_tag_schema import CreateTagRequest, CreateTagResponse
from domain.entities.tag import Tag


class CreateTagAdapter:
    """
    Class with static methods used for converting request and response to domain objs
    for tag creation endpoints
    """

    @staticmethod
    def to_create_tag_domain(request: CreateTagRequest) -> Tag:
        """Convert CreateTagRequest to Tag domain object"""
        return Tag(
            points=request.points,
            tag_id=request.tag_id
        )

    @staticmethod
    def to_create_tag_response(tag: Tag) -> CreateTagResponse:
        """Convert Tag domain object to CreateTagResponse"""
        return CreateTagResponse(
            tag_id=tag.tag_id,
            points=tag.points,
            secret=tag.secret
        )

