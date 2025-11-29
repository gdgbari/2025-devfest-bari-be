from fastapi import APIRouter, Depends, status

from api.adapters.tags.create_tag_adapter import CreateTagAdapter
from api.schemas.tags.create_tag_schema import CreateTagRequest
from api.schemas.tags.read_tag_schema import GetTagResponse
from api.adapters.tags.read_tag_adapter import ReadTagAdapter
from core.authorization import check_user_role, verify_id_token
from core.dependencies import TagServiceDep
from domain.entities.tag import Tag
from domain.entities.user import User
from domain.entities.role import Role

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.post(
    "",
    description="Endpoint for creating a new Tag in database",
    response_model=GetTagResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Tag created successfully"},
        400: {"description": "Bad request - Invalid tag data or Firestore operation failed"},
        401: {"description": "Unauthorized - Invalid or expired token"},
        403: {"description": "Forbidden - Insufficient privileges"},
        409: {"description": "Conflict - Tag already exists"},
        500: {"description": "Internal server error"},
    },
)
def create_tag(
    request: CreateTagRequest,
    tag_service: TagServiceDep,
    user_token: User = Depends(verify_id_token),
) -> GetTagResponse:
    """
    Create a new tag.
    """
    # Check if user has staff role
    check_user_role(user_token, min_role=Role.STAFF)

    # Convert request to domain object and create tag
    new_tag: Tag = tag_service.create_tag(
        CreateTagAdapter.to_create_tag_domain(request)
    )

    return ReadTagAdapter.to_get_tag_response(new_tag)


