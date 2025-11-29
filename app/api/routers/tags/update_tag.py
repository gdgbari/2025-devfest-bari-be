from fastapi import APIRouter, Depends, status

from api.adapters.tags.update_tag_adapter import UpdateTagAdapter
from api.schemas.tags.update_tag_schema import UpdateTagRequest
from api.schemas.tags.read_tag_schema import GetTagResponse
from api.adapters.tags.read_tag_adapter import ReadTagAdapter
from core.authorization import check_user_role, verify_id_token
from core.dependencies import TagServiceDep
from domain.entities.tag import Tag
from domain.entities.user import User

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.put(
    "/{tag_id}",
    description="Update tag information in Firestore by tag ID",
    response_model=GetTagResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Tag updated successfully"},
        400: {"description": "Bad request - Invalid data or Firestore operation failed"},
        401: {"description": "Unauthorized - Invalid or expired token"},
        403: {"description": "Forbidden - Insufficient privileges"},
        404: {"description": "Not found - Tag not found in Firestore"},
        500: {"description": "Internal server error"},
    },
)
def update_tag(
    tag_id: str,
    tag_update: UpdateTagRequest,
    tag_service: TagServiceDep,
    user_token: User = Depends(verify_id_token),
) -> GetTagResponse:
    """Update a tag"""

    # Check if user has staff role
    check_user_role(user_token)

    # Convert request to update dict and update tag
    updated_tag: Tag = tag_service.update_tag(
        tag_id, tag_update.model_dump()
    )

    return UpdateTagAdapter.to_update_response(updated_tag)
