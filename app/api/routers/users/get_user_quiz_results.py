from fastapi import APIRouter, Depends, status
from api.schemas.users.user_quiz_result_schema import UserQuizResultListResponse, UserQuizResultResponse
from core.authorization import check_user_role, verify_id_token
from core.dependencies import UserServiceDep
from domain.entities.user import User
from domain.entities.role import Role

router = APIRouter(prefix="/users", tags=["Users"])

@router.get(
    "/{uid}/quiz-results",
    description="Get all quiz results for a specific user (Staff only)",
    response_model=UserQuizResultListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Quiz results retrieved successfully"},
        401: {"description": "Unauthorized - Invalid or expired token"},
        403: {"description": "Forbidden - Insufficient privileges"},
        404: {"description": "Not found - User not found"},
        500: {"description": "Internal server error"},
    },
)
def get_user_quiz_results(
    uid: str,
    user_service: UserServiceDep,
    user_token: User = Depends(verify_id_token),
) -> UserQuizResultListResponse:
    
    # Check if requester is at least STAFF
    check_user_role(user_token, min_role=Role.STAFF)

    results = user_service.get_user_quiz_results(uid)
    
    # Convert domain objects to schema objects
    response_results = [
        UserQuizResultResponse(
            score=r.score,
            max_score=r.max_score,
            quiz_title=r.quiz_title,
            submitted_at=r.submitted_at
        ) for r in results
    ]
    
    return UserQuizResultListResponse(results=response_results)
