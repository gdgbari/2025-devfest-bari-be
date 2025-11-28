from fastapi import APIRouter, Depends, status

from api.adapters.tags.create_tag_adapter import CreateTagAdapter
from api.schemas.tags.create_tag_schema import CreateTagRequest, CreateTagResponse
from core.authorization import check_user_role, verify_id_token
from core.dependencies import TagServiceDep
from domain.entities.tag import Tag

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.post(
    "",
    description="Endpoint for creating a new Tag in database",
    response_model=CreateTagResponse,
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
    user_token=Depends(verify_id_token),
) -> CreateTagResponse:
    """Create a new tag"""

    # Check if user has staff role
    check_user_role(user_token)

    # Convert request to domain object and create tag
    new_tag: Tag = tag_service.create_tag(
        CreateTagAdapter.to_create_tag_domain(request)
    )

    return CreateTagAdapter.to_create_tag_response(new_tag)

