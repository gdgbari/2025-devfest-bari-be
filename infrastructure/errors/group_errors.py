from infrastructure.errors.base_error import BaseError


class CreateGroupError(BaseError):
    """Raised during group creation"""
    def __init__(self, message: str, http_status: int):
        super().__init__(message, status_code=http_status)


class DeleteGroupError(BaseError):
    """Raised during group deletion"""
    def __init__(self, message: str, http_status: int):
        super().__init__(message, status_code=http_status)


class ReadGroupError(BaseError):
    """Raised during group reading"""
    def __init__(self, message: str, http_status: int):
        super().__init__(message, status_code=http_status)


class UpdateGroupError(BaseError):
    """Raised during group updating"""
    def __init__(self, message: str, http_status: int):
        super().__init__(message, status_code=http_status)

