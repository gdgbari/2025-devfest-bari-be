from typing import Annotated

from fastapi import HTTPException, status
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth
from pydantic import BaseModel, EmailStr

from domain.entities.user import User
from domain.entities.role import Role
from core.dependencies import get_auth_client, get_user_repository
from infrastructure.repositories.user_repository import UserRepository

class UserToken(BaseModel):
    """
    Class created from a validated token given from an authorization header
    """
    user_id: str
    sub: str
    uid: str
    email: EmailStr
    email_verified: bool
    auth_time: int
    iat: int
    exp: int
    iss: str
    aud: str
    firebase: dict

token_auth_scheme = HTTPBearer()

def _authorize_token(creds: HTTPAuthorizationCredentials = Depends(token_auth_scheme)) -> UserToken:
    """
    Verify firebase token ID, if valid gets back user data, otherwise throw HTTPException
    """
    # Initialize firebase auth client
    get_auth_client()
    # Get token from http credentials
    token = creds.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return UserToken.model_validate(decoded_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token not valid or expired: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def authorize(min_role: Role = Role.ATTENDEE):
    """
    Factory function that returns a dependency to check user role authorization.

    Usage:
        @router.get("/admin")
        def admin_endpoint(user: User = Depends(authorize(Role.STAFF))):
            ...

        @router.get("/profile")  # Default: Role.ATTENDEE
        def profile_endpoint(user: User = Depends(authorize())):
            ...

    Args:
        min_role: Minimum required role (default: Role.ATTENDEE)

    Returns:
        A dependency function that validates user authorization
    """
    def _authorize_user_with_role(user_token: UserToken = Depends(_authorize_token),
                                user_repository: UserRepository = Depends(get_user_repository)) -> User:
        """
        Verify user has minimum required role.
        Returns the full User object if authorized.
        """
        uid: str = user_token.uid
        user: User = user_repository.read(uid)
        if not user.role.is_authorized(min_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient privileges. Required: {min_role.value}, Current: {user.role.value}",
            )

        return user
    return _authorize_user_with_role
