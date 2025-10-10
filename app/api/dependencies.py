from typing import Annotated
from functools import lru_cache
from fastapi import Depends

from infrastructure.repositories.auth_repository import AuthRepository
from infrastructure.clients.firebase_auth_client import FirebaseAuthClient
from infrastructure.clients.firestore_client import FirestoreClient
from infrastructure.repositories.user_repository import UserRepository
from domain.services.user_service import UserService

@lru_cache()
def get_auth_client() -> FirebaseAuthClient:
    """
    Dependency to get FirebaseAuthClient singleton instance.
    The lru_cache decorator ensures only one instance is created.
    """
    return FirebaseAuthClient()

@lru_cache()
def get_firestore_client() -> FirestoreClient:
    """
    Dependency to get FirestoreClient singleton instance.
    The lru_cache decorator ensures only one instance is created.
    """
    return FirestoreClient()

def get_auth_repository(
    auth_client: Annotated[FirebaseAuthClient, Depends(get_auth_client)]
) -> AuthRepository:
    """Dependency to get AuthRepository instance"""
    return AuthRepository(auth_client)

def get_user_repository(
    firestore_client: Annotated[FirestoreClient, Depends(get_firestore_client)]
) -> UserRepository:
    """Dependency to get UserRepository instance"""
    return UserRepository(firestore_client)

def get_user_service(
    auth_repository: Annotated[AuthRepository, Depends(get_auth_repository)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserService:
    """Dependency to get UserService with injected repositories"""
    return UserService(auth_repository, user_repository)
