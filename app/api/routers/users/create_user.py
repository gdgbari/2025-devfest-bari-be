from fastapi import APIRouter, status

from api.adapters.users.create_user_adapter import CreateUserAdapter
from api.schemas.users.create_user_schema import CreateUserRequest, CreateUserResponse
from domain.entities.user import User
from domain.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.post(
    "",
    response_model=CreateUserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Bad request - invalid data or user ID not specified"},
        409: {"description": "User already exists - email already in use or user data already exists"},
        500: {"description": "Internal server error"},
    },
)
def create_user(request: CreateUserRequest) -> CreateUserResponse:
    """Create a new user in Firebase Auth and Firestore"""
    new_user: User = UserService.create_user(
        CreateUserAdapter.to_create_user_domain(request)
    )
    return CreateUserAdapter.to_create_user_response(new_user)