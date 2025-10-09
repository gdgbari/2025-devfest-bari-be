from typing import Annotated
from fastapi import APIRouter, status, Depends

from api.adapters.users.create_user_adapter import CreateUserAdapter
from api.schemas.users.create_user_schema import CreateUserRequest, CreateUserResponse
from domain.entities.user import User
from domain.services.user_service import UserService
from core.dependencies import get_user_service

router = APIRouter(prefix="/users", tags=["Users"])

@router.post(
    "",
    description="Endpoint for creating a new User in database",
    response_model=CreateUserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Bad request - invalid data or user ID not specified"},
        409: {"description": "Nickname already used - User already exists - email already in use or user data already exists"},
        500: {"description": "Internal server error"},
    },
)
def create_user(
    request: CreateUserRequest,
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> CreateUserResponse:

    new_user: User = user_service.create_user(
        CreateUserAdapter.to_create_user_domain(request)
    )
    return CreateUserAdapter.to_create_user_response(new_user)
