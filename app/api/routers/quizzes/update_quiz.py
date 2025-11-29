from fastapi import APIRouter, Depends, status

from api.adapters.quizzes.update_quiz_adapter import UpdateQuizAdapter
from api.schemas.quizzes.update_quiz_schema import UpdateQuizRequest
from api.schemas.quizzes.read_quiz_schema import GetQuizResponse
from api.adapters.quizzes.read_quiz_adapter import ReadQuizAdapter
from core.authorization import check_user_role, verify_id_token
from core.dependencies import QuizServiceDep
from domain.entities.quiz import Quiz
from domain.entities.user import User

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


@router.put(
    "/{quiz_id}",
    description="Update quiz information in Firestore by quiz ID",
    response_model=GetQuizResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Quiz updated successfully"},
        400: {"description": "Bad request - Invalid data or Firestore operation failed"},
        401: {"description": "Unauthorized - Invalid or expired token"},
        403: {"description": "Forbidden - Insufficient privileges"},
        404: {"description": "Not found - Quiz not found in Firestore"},
        500: {"description": "Internal server error"},
    },
)
def update_quiz(
    quiz_id: str,
    quiz_update: UpdateQuizRequest,
    quiz_service: QuizServiceDep,
    user_token: User = Depends(verify_id_token),
) -> GetQuizResponse:
    """
    Update a quiz.
    """
    check_user_role(user_token)

    updated_quiz: Quiz = quiz_service.update_quiz(quiz_id, quiz_update.model_dump(exclude_unset=True))
    return ReadQuizAdapter.to_get_quiz_response(updated_quiz)
