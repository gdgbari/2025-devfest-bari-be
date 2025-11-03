from fastapi import APIRouter, Depends, status

from api.adapters.quizzes.read_quiz_adapter import ReadQuizAdapter
from api.schemas.quizzes.read_quiz_schema import (
    GetQuizResponse,
    GetQuizListWithCorrectResponse,
)
from core.authorization import check_user_role, verify_id_token
from core.dependencies import QuizServiceDep
from domain.entities.quiz import Quiz
from domain.entities.role import Role

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


@router.get(
    "",
    description="Get all quizzes from Firestore with correct answers (staff only)",
    response_model=GetQuizListWithCorrectResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "List of quizzes retrieved successfully with correct answers"},
        400: {"description": "Bad request - Firestore operation failed"},
        401: {"description": "Unauthorized - Invalid or expired token"},
        403: {"description": "Forbidden - Insufficient privileges"},
        500: {"description": "Internal server error"},
    },
)
def read_all_quizzes(
    quiz_service: QuizServiceDep,
    user_token=Depends(verify_id_token),
) -> GetQuizListWithCorrectResponse:
    """Get all quizzes with correct answers. Staff only - returns all quizzes regardless of is_open status."""

    # Check if user has staff role
    check_user_role(user_token, min_role=Role.STAFF)

    # Read all quizzes from database
    quizzes: list[Quiz] = quiz_service.read_all_quizzes()

    # Convert to response INCLUDING correct answers (staff only)
    return ReadQuizAdapter.to_get_quizzes_with_correct_response(quizzes)


@router.get(
    "/{quiz_id}",
    description="Get quiz by ID from Firestore (attendees can read only open quizzes)",
    response_model=GetQuizResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Quiz retrieved successfully"},
        400: {"description": "Bad request - Firestore operation failed"},
        401: {"description": "Unauthorized - Invalid or expired token"},
        403: {"description": "Forbidden - Quiz is not open"},
        404: {"description": "Not found - Quiz not found in Firestore"},
        500: {"description": "Internal server error"},
    },
)
def read_quiz(
    quiz_id: str,
    quiz_service: QuizServiceDep,
    user_token=Depends(verify_id_token),
) -> GetQuizResponse:
    """Get a quiz by ID. Only open quizzes can be read by attendees."""

    # Check if user has at least attendee role
    check_user_role(user_token, min_role=Role.ATTENDEE)

    # Read quiz from database (service checks if quiz is open)
    quiz: Quiz = quiz_service.read_quiz(quiz_id)

    # Convert to response without exposing answers
    return ReadQuizAdapter.to_get_quiz_response(quiz)

