from fastapi import APIRouter, status

from api.adapters.users.create_user_adapter import CreateUserAdapter
from api.schemas.users.create_user_schema import (CreateUserRequest,
                                                  CreateUserResponse)
from core.dependencies import CreateUserServiceDep
from domain.entities.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    description="Endpoint for creating a new User in database",
    response_model=CreateUserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Bad request - Invalid user data or Firebase operation failed"},
        409: {"description": "Conflict - Email or nickname already exists"},
        500: {"description": "Internal server error"},
    },
)
def create_user(
    request: CreateUserRequest,
    create_user_service: CreateUserServiceDep,
) -> CreateUserResponse:

    new_user: User = create_user_service.create(
        CreateUserAdapter.to_create_user_domain(request)
    )
    return CreateUserAdapter.to_create_user_response(new_user)
