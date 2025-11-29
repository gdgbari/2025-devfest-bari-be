from typing import Optional

from core.dependencies import UserRepositoryDep
from domain.entities.role import Role
from domain.entities.user import User
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth
from infrastructure.errors.auth_errors import ForbiddenError, UnauthorizedError
from infrastructure.errors.user_errors import ReadUserError


token_auth_scheme = HTTPBearer()


def verify_id_token(
    user_repository: UserRepositoryDep,
    creds: HTTPAuthorizationCredentials = Depends(token_auth_scheme),
) -> User:
    """
    Verify firebase token ID, if valid gets back user data from Firestore, otherwise throw HTTPException.
    """

    token = creds.credentials
    try:
        decoded_token = auth.verify_id_token(token, check_revoked=True)
        uid = decoded_token.get("uid")
        
        # Fetch user from Firestore
        # We use read_raw because we might not need tags for authorization, 
        # but User.from_dict expects a dict. 
        # Actually, user_repository.read(uid) returns a User object (without tags).
        # That should be enough for authorization checks (role, checked_in).
        try:
            user = user_repository.read(uid)
            return user
        except Exception:
            # If user not found in Firestore (e.g. during creation or inconsistency)
            # we might want to handle it. But for now, if not in Firestore, unauthorized.
            raise UnauthorizedError

    except HTTPException:
        raise
    except Exception:
        raise UnauthorizedError


def check_user_role(
    user: User,
    min_role: Role = Role.STAFF,
    allow_owner: bool = False,
    uid: Optional[str] = None,
):
    if allow_owner and uid is not None:
        if user.uid == uid:
            return

    if user.role is None:
         raise ForbiddenError

    if not user.role.is_authorized(min_role):
        raise ForbiddenError


def check_user_checked_in(
    user: User,
    is_checked_in: bool = True
):
    """"
    Check if the user has already performed the check-in,
    requiring a check-in already performed or not.
    """
    if is_checked_in != user.checked_in:
        raise ForbiddenError
