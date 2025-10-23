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
