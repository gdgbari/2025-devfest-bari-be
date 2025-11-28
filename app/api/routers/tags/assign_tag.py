from fastapi import APIRouter, Depends, status

from api.adapters.tags.assign_tag_adapter import AssignTagAdapter
from api.schemas.tags.assign_tag_schema import (
    AssignTagRequest,
    AssignTagBySecretRequest,
    AssignTagResponse,
    AssignTagBySecretResponse
)
from core.authorization import check_user_role, verify_id_token
from core.dependencies import TagServiceDep

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.post(
    "/assign",
    description="Assign a tag to a user",
    response_model=AssignTagResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Tag assigned successfully"},
        400: {"description": "Bad request - Invalid tag or user data"},
        401: {"description": "Unauthorized - Invalid or expired token"},
        403: {"description": "Forbidden - Insufficient privileges"},
        404: {"description": "Not found - Tag or user not found"},
        409: {"description": "Conflict - Tag already assigned to user"},
        500: {"description": "Internal server error"},
    },
)
def assign_tag(
    request: AssignTagRequest,
    tag_service: TagServiceDep,
    user_token=Depends(verify_id_token),
) -> AssignTagResponse:
    """
    Assign a tag to a user.
    Adds the tag to user's tags list and updates leaderboard scores.
    """
    # Check if user has staff role
    check_user_role(user_token)

    # Assign tag to user
    points = tag_service.assign_tag_to_user(request.tag_id, request.uid)

    return AssignTagAdapter.to_assign_tag_response(request.tag_id, request.uid, points)


@router.post(
    "/assign-secret",
    description="Assign a tag to the logged-in user by secret",
    response_model=AssignTagBySecretResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Tag redeemed and assigned successfully"},
        400: {"description": "Bad request - Invalid secret, multiple tags found, or user data"},
        401: {"description": "Unauthorized - Invalid or expired token"},
        404: {"description": "Not found - Tag with provided secret not found"},
        409: {"description": "Conflict - Tag already assigned to user"},
        500: {"description": "Internal server error"},
    },
)
def assign_tag_by_secret(
    request: AssignTagBySecretRequest,
    tag_service: TagServiceDep,
    user_token=Depends(verify_id_token),
) -> AssignTagResponse:
    """
    Assign a tag to the logged-in user by secret.
    Finds the tag by secret (using read_all and filtering), adds it to user's tags list
    and updates leaderboard scores.
    """
    # Get the user ID from the authenticated token
    uid = user_token.uid

    # Redeem tag by secret for the logged-in user
    points = tag_service.assign_tag_by_secret(request.secret, uid)

    return AssignTagAdapter.to_assign_tag_by_secret_response(request.secret, uid, points)

