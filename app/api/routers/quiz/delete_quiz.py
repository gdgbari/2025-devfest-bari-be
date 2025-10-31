from fastapi import APIRouter, Depends, status

from core.authorization import check_user_role, verify_id_token
from core.dependencies import QuizServiceDep

router = APIRouter(prefix="/quiz", tags=["Quiz"])


@router.delete(
    "/{quiz_id}",
    description="Delete quiz from Firestore by quiz ID",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Quiz deleted successfully"},
        400: {"description": "Bad request - Firestore operation failed"},
        401: {"description": "Unauthorized - Invalid or expired token"},
        403: {"description": "Forbidden - Insufficient privileges"},
        404: {"description": "Not found - Quiz not found in Firestore"},
        500: {"description": "Internal server error"},
    },
)
def delete_quiz(
    quiz_id: str,
    quiz_service: QuizServiceDep,
    user_token=Depends(verify_id_token),
) -> None:
    """Delete a quiz by ID"""

    # Check if user has staff role
    check_user_role(user_token)

    quiz_service.delete_quiz(quiz_id)

