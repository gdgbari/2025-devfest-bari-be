from api.schemas.tags.assign_tag_schema import AssignTagResponse
from api.schemas.tags.assign_tag_schema import AssignTagBySecretResponse


class AssignTagAdapter:
    """
    Class with static methods used for converting request and response
    for tag assignment endpoints
    """

    @staticmethod
    def to_assign_tag_response(tag_id: str, uid: str, points: int) -> AssignTagResponse:
        """
        Convert to AssignTagResponse.
        """
        return AssignTagResponse(
            tag_id=tag_id,
            user_id=uid,
            points=points
        )

    @staticmethod
    def to_assign_tag_by_secret_response(secret: str, uid: str, points: int) -> AssignTagBySecretResponse:
        """
        Convert to AssignTagResponse.
        """
        return AssignTagBySecretResponse(
            secret=secret,
            user_id=uid,
            points=points
        )

