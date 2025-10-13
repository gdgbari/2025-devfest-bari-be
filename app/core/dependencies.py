from typing import Annotated
from functools import lru_cache
from fastapi import Depends

from infrastructure.repositories.firebase_auth_repository import FirebaseAuthRepository
from infrastructure.clients.firebase_auth_client import FirebaseAuthClient
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.clients.firestore_client import FirestoreClient
from infrastructure.repositories.firestore_repository import FirestoreRepository
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
) -> FirebaseAuthRepository:
    """Dependency to get AuthRepository instance"""
    return FirebaseAuthRepository(auth_client)

def get_firestore_repository(
    firestore_client: Annotated[FirestoreClient, Depends(get_firestore_client)]
) -> FirestoreRepository:
    """Dependency to get UserRepository instance"""
    return FirestoreRepository(firestore_client)

def get_user_repository(
    auth_repository: Annotated[FirebaseAuthRepository, Depends(get_auth_repository)],
    firestore_repository: Annotated[FirestoreRepository, Depends(get_firestore_repository)]
) -> UserRepository:
    """Dependency to get UserRepository instance"""
    return UserRepository(auth_repository, firestore_repository)

def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserService:
    """Dependency to get UserService with injected repositories"""
    return UserService(user_repository)
