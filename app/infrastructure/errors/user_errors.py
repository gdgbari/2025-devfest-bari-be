from infrastructure.errors.base_error import BaseError

class ReserveNicknameError(BaseError):
    """Raised during nickname reservation"""
    def __init__(self, message: str, http_status: int):
        super().__init__(message, status_code=http_status)

class CreateUserError(BaseError):
    """Raised during user creation with firestore"""
    def __init__(self, message: str, http_status: int):
        super().__init__(message, status_code=http_status)

class DeleteUserError(BaseError):
    """Raised during user deletion"""
    def __init__(self, message: str, http_status: int):
        super().__init__(message, status_code=http_status)

class ReadUserError(BaseError):
    """Raised during user reading"""
    def __init__(self, message: str, http_status: int):
        super().__init__(message, status_code=http_status)

class UpdateUserError(BaseError):
    """Raised during user updating"""
    def __init__(self, message: str, http_status: int):
        super().__init__(message, status_code=http_status)
