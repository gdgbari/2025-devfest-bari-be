from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth
from pydantic import BaseModel, EmailStr

from core.dependencies import AuthClientDep
from domain.entities.role import Role


class UserToken(BaseModel):
    """
    Class created from a validated token given from an authorization header
    """
    user_id: str
    user_role: str
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


def verify_id_token(
    creds: HTTPAuthorizationCredentials = Depends(token_auth_scheme),
) -> UserToken:
    """
    Verify firebase token ID, if valid gets back user data, otherwise throw HTTPException.
    Also verifies that the user still exists in Firebase Auth.
    """
    authClientDep = AuthClientDep

    token = creds.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        user_token = UserToken.model_validate(decoded_token)
        auth.get_user(user_token.uid)
        return user_token
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not Authorized",
        )


def check_user_role(
    user_token: UserToken,
    min_role: Role = Role.STAFF,
    allow_owner: bool = False,
    uid: Optional[str] = None,
):
    if allow_owner and uid is not None:
        if user_token.uid == uid:
            return

    user_role = Role(user_token.user_role)
    if not user_role.is_authorized(min_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
