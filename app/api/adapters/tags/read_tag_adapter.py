from api.schemas.tags.read_tag_schema import GetTagResponse, GetTagListResponse
from domain.entities.tag import Tag


class ReadTagAdapter:
    """
    Class with static methods used for converting domain objects to response
    for tag reading endpoints
    """

    @staticmethod
    def to_get_tag_response(tag: Tag) -> GetTagResponse:
        """Convert Tag domain object to GetTagResponse"""
        return GetTagResponse(
            tag_id=tag.tag_id,
            points=tag.points,
            secret=tag.secret
        )

    @staticmethod
    def to_get_tags_response(tags: list[Tag]) -> GetTagListResponse:
        """Convert list of Tag domain objects to GetTagListResponse"""
        return GetTagListResponse(
            tags=[
                ReadTagAdapter.to_get_tag_response(tag)
                for tag in tags
            ],
            total=len(tags)
        )

