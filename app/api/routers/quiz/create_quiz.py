from fastapi import APIRouter, Depends, status

from api.adapters.quiz.create_quiz_adapter import CreateQuizAdapter
from api.schemas.quiz.create_quiz_schema import CreateQuizRequest, CreateQuizResponse
from core.authorization import check_user_role, verify_id_token
from core.dependencies import QuizServiceDep
from domain.entities.quiz import Quiz

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


@router.post(
    "",
    description="Endpoint for creating a new Quiz in database",
    response_model=CreateQuizResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Quiz created successfully"},
        400: {"description": "Bad request - Invalid quiz data or Firestore operation failed"},
        401: {"description": "Unauthorized - Invalid or expired token"},
        403: {"description": "Forbidden - Insufficient privileges"},
        500: {"description": "Internal server error"},
    },
)
def create_quiz(
    request: CreateQuizRequest,
    quiz_service: QuizServiceDep,
    user_token=Depends(verify_id_token),
) -> CreateQuizResponse:
    """Create a new quiz"""

    # Check if user has staff role
    check_user_role(user_token)

    # Convert request to domain object and create quiz
    new_quiz: Quiz = quiz_service.create_quiz(
        CreateQuizAdapter.to_create_quiz_domain(request)
    )

    return CreateQuizAdapter.to_create_quiz_response(new_quiz)

