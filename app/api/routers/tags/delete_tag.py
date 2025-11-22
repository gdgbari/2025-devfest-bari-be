from fastapi import APIRouter, Depends, status

from core.authorization import check_user_role, verify_id_token
from core.dependencies import TagServiceDep

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.delete(
    "/{tag_id}",
    description="Delete tag from Firestore",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Tag deleted successfully"},
        400: {"description": "Bad request - Firestore operation failed"},
        401: {"description": "Unauthorized - Invalid or expired token"},
        403: {"description": "Forbidden - Insufficient privileges"},
        404: {"description": "Not found - Tag not found in Firestore"},
        500: {"description": "Internal server error"},
    },
)
def delete_tag(
    tag_id: str,
    tag_service: TagServiceDep,
    user_token=Depends(verify_id_token),
) -> None:
    """Delete a tag"""

    # Check if user has staff role
    check_user_role(user_token)

    tag_service.delete_tag(tag_id)

