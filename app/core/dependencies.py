from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from domain.services.user_service import UserService
from infrastructure.clients.firebase_auth_client import FirebaseAuthClient
from infrastructure.clients.firestore_client import FirestoreClient
from infrastructure.repositories.firebase_auth_repository import \
    FirebaseAuthRepository
from infrastructure.repositories.firestore_repository import \
    FirestoreRepository
from infrastructure.repositories.user_repository import UserRepository


@lru_cache()
def get_auth_client() -> FirebaseAuthClient:
    """
    Dependency to get FirebaseAuthClient singleton instance.
    The lru_cache decorator ensures only one instance is created.
    """
    return FirebaseAuthClient()

AuthClientDep = Annotated[FirebaseAuthClient, Depends(get_auth_client)]

@lru_cache()
def get_firestore_client() -> FirestoreClient:
    """
    Dependency to get FirestoreClient singleton instance.
    The lru_cache decorator ensures only one instance is created.
    """
    return FirestoreClient()

FirestoreClientDep = Annotated[FirestoreClient, Depends(get_firestore_client)]

def get_auth_repository(
    auth_client: AuthClientDep
) -> FirebaseAuthRepository:
    """Dependency to get AuthRepository instance"""
    return FirebaseAuthRepository(auth_client)

AuthRepositoryDep = Annotated[FirebaseAuthRepository, Depends(get_auth_repository)]

def get_firestore_repository(
    firestore_client: FirestoreClientDep
) -> FirestoreRepository:
    """Dependency to get UserRepository instance"""
    return FirestoreRepository(firestore_client)

FirestoreRepositoryDep = Annotated[FirebaseAuthRepository, Depends(get_firestore_repository)]

def get_user_repository(
    auth_repository: AuthRepositoryDep,
    firestore_repository: FirestoreRepositoryDep
) -> UserRepository:
    """Dependency to get UserRepository instance"""
    return UserRepository(auth_repository, firestore_repository)

UserRepositoryDep = Annotated[UserService, Depends(get_user_repository)]

def get_user_service(
    user_repository: UserRepositoryDep
) -> UserService:
    """Dependency to get UserService with injected repositories"""
    return UserService(user_repository)

UserServiceDep = Annotated[UserService, Depends(get_user_service)]