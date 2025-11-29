from fastapi import APIRouter, Depends, status

from api.adapters.tags.read_tag_adapter import ReadTagAdapter
from api.schemas.tags.read_tag_schema import GetTagListResponse, GetTagResponse
from core.authorization import check_user_role, verify_id_token
from core.dependencies import TagServiceDep
from domain.entities.tag import Tag
from domain.entities.user import User

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get(
    "",
    description="Get all tags from Firestore",
    response_model=GetTagListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "List of tags retrieved successfully"},
        400: {"description": "Bad request - Firestore operation failed"},
        401: {"description": "Unauthorized - Invalid or expired token"},
        403: {"description": "Forbidden - Insufficient privileges"},
        500: {"description": "Internal server error"},
    },
)
def read_all_tags(
    tag_service: TagServiceDep,
    user_token: User = Depends(verify_id_token),
) -> GetTagListResponse:
    """Get all tags"""

    check_user_role(user_token)
    tags: list[Tag] = tag_service.read_all_tags()
    return ReadTagAdapter.to_get_tags_response(tags)


@router.get(
    "/{tag_id}",
    description="Get tag by ID from Firestore",
    response_model=GetTagResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Tag retrieved successfully"},
        400: {"description": "Bad request - Firestore operation failed"},
        401: {"description": "Unauthorized - Invalid or expired token"},
        403: {"description": "Forbidden - Insufficient privileges"},
        404: {"description": "Not found - Tag not found in Firestore"},
        500: {"description": "Internal server error"},
    },
)
def read_tag(
    tag_id: str,
    tag_service: TagServiceDep,
    user_token: User = Depends(verify_id_token),
) -> GetTagResponse:
    """
    Get a tag by ID.
    """
    check_user_role(user_token)

    tag = tag_service.read_tag(tag_id)
    return ReadTagAdapter.to_get_tag_response(tag)
