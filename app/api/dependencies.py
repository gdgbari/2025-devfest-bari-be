from typing import Annotated
from fastapi import Depends

from infrastructure.repositories.auth_repository import AuthRepository
from infrastructure.repositories.user_repository import UserRepository
from domain.services.user_service import UserService

def get_auth_repository() -> AuthRepository:
    """Dependency to get AuthRepository instance"""
    return AuthRepository()

def get_user_repository() -> UserRepository:
    """Dependency to get UserRepository instance"""
    return UserRepository()

def get_user_service(
    auth_repository: Annotated[AuthRepository, Depends(get_auth_repository)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserService:
    """Dependency to get UserService with injected repositories"""
    return UserService(auth_repository, user_repository)