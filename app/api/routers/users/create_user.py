from fastapi import APIRouter, status

from api.adapters.users.create_user_adapter import CreateUserAdapter
from api.schemas.users.create_user_schema import (CreateUserRequest,
                                                  CreateUserResponse)
from core.dependencies import UserServiceDep
from domain.entities.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    description="Endpoint for creating a new User in database",
    response_model=CreateUserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    request: CreateUserRequest,
    user_service: UserServiceDep,
) -> CreateUserResponse:

    new_user: User = user_service.create_user(
        CreateUserAdapter.to_create_user_domain(request)
    )
    return CreateUserAdapter.to_create_user_response(new_user)
