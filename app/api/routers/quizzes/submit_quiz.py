from fastapi import APIRouter, Depends, status

from api.schemas.quizzes.submit_quiz_schema import (
    SubmitQuizRequest,
    SubmitQuizResponse,
)
from core.authorization import check_user_checked_in, check_user_role, verify_id_token
from core.dependencies import QuizServiceDep
from domain.entities.role import Role

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


@router.post(
    "/{quiz_id}/submit",
    description="Submit quiz answers and get score",
    response_model=SubmitQuizResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Quiz submitted successfully, score calculated"},
        400: {"description": "Bad request - Invalid answer list or missing start time"},
        401: {"description": "Unauthorized - Invalid or expired token"},
        403: {"description": "Forbidden - User not checked in or insufficient privileges"},
        404: {"description": "Not found - Quiz not found or start time not found"},
        408: {"description": "Request Timeout - Quiz time expired"},
        409: {"description": "Conflict - Quiz already submitted"},
        423: {"description": "Locked - Quiz is not open"},
        500: {"description": "Internal server error"},
    },
)
def submit_quiz(
    quiz_id: str,
    request: SubmitQuizRequest,
    quiz_service: QuizServiceDep,
    user_token=Depends(verify_id_token),
) -> SubmitQuizResponse:
    """
    Submit quiz answers and get the score.

    Requirements:
    - User must be at least ATTENDEE role
    - User must have checked in
    - Quiz must be open
    - User must not have already submitted this quiz
    - Answer list length must match question count
    - Timer must not have expired (30s grace period)
    """

    # Check if user has at least attendee role
    check_user_role(user_token, min_role=Role.ATTENDEE)

    # Check if user has checked in
    check_user_checked_in(user_token, is_checked_in=True)

    # Convert list of answers to dictionary {question_id: answer_id}
    answers_dict = {item.question_id: item.answer_id for item in request.answers}

    # Submit quiz and calculate score
    score, max_score = quiz_service.submit_quiz(
        quiz_id,
        answers_dict,
        user_token.user_id
    )

    return SubmitQuizResponse(score=score, max_score=max_score)

