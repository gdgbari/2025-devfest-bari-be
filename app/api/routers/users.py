from fastapi import APIRouter, status

from api.adapters.user_adapters import UserAdapters
from api.schemas.user_schemas import *
from domain.entities.user import User
from domain.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Bad request - invalid data or user ID not specified"},
        409: {"description": "User already exists - email already in use or user data already exists"},
        500: {"description": "Internal server error"},
    },
)
def create_user(user_schema: UserCreateSchema) -> UserResponseSchema:
    """Create a new user in Firebase Auth and Firestore"""
    new_user: User = UserService.create_user(
        UserAdapters.create_schema_to_domain(user_schema)
    )
    return UserAdapters.domain_to_response_schema(new_user)


@router.get(
    "",
    response_model=UserListResponseSchema,
    responses={
        500: {"description": "Internal server error"}
    },
)
def read_all_users() -> UserListResponseSchema:
    """Get all users from Firebase Auth and Firestore"""
    users: list[User] = UserService.read_all_users()
    return UserAdapters.domain_list_to_list_response_schema(users)


@router.get(
    "/{uid}",
    response_model=UserResponseSchema,
    responses={
        404: {"description": "User not found - either in Firebase Auth or Firestore"},
        500: {"description": "Internal server error"},
    },
)
def read_user(uid: str) -> UserResponseSchema:
    """Get user by UID from Firebase Auth and Firestore"""
    user: User = UserService.read_user(uid)
    return UserAdapters.domain_to_response_schema(user)


@router.put(
    "/{uid}",
    response_model=UserResponseSchema,
    responses={
        400: {"description": "Bad request - invalid data or no data to update"},
        404: {"description": "User not found - either in Firebase Auth or Firestore"},
        500: {"description": "Internal server error"},
    },
)
def update_user(uid: str, user_update: UserUpdateSchema) -> UserResponseSchema:
    """Update user information in Firebase Auth and Firestore"""
    updated_user: User = UserService.update_user(uid, user_update.model_dump())
    return UserAdapters.domain_to_response_schema(updated_user)


@router.delete(
    "/{uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "User not found - either in Firebase Auth or Firestore"},
        500: {"description": "Internal server error"},
    },
)
def delete_user(uid: str) -> None:
    """Delete user from Firebase Auth and Firestore"""
    UserService.delete_user(uid)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        500: {"description": "Internal server error"}
    },
)
def delete_all_users() -> None:
    """Delete all users from Firebase Auth and Firestore (use with caution!)"""
    UserService.delete_all_users()
