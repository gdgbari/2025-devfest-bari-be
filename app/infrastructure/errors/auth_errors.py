from fastapi import status

from infrastructure.errors.base_error import BaseError

class AuthenticateUserError(BaseError):
    """Raised during authentication of the user"""
    def __init__(self, message: str, http_status: int):
        super().__init__(message, status_code=http_status)

class DeleteUserAuthError(BaseError):
    """Raised during deletion of the authentication of a user"""
    def __init__(self, message: str, http_status: int):
        super().__init__(message, status_code=http_status)

class UpdateUserAuthError(BaseError):
    """Raised during updating the authentication of a user"""
    def __init__(self, message: str, http_status: int):
        super().__init__(message, status_code=http_status)

class UnauthorizedError(BaseError):
    """Raised during authorization of a user"""
    def __init__(self):
        super().__init__("Not Authorized", status_code=status.HTTP_401_UNAUTHORIZED)

class ForbiddenError(BaseError):
    """Raised during authorization of a user if he has insufficient permissions"""
    def __init__(self):
        super().__init__("Insufficient permissions", status_code=status.HTTP_403_FORBIDDEN)
