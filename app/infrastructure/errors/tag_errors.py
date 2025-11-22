from infrastructure.errors.base_error import BaseError


class CreateTagError(BaseError):
    """Raised during tag creation"""
    def __init__(self, message: str, http_status: int):
        super().__init__(message, status_code=http_status)


class ReadTagError(BaseError):
    """Raised during tag reading"""
    def __init__(self, message: str, http_status: int):
        super().__init__(message, status_code=http_status)


class UpdateTagError(BaseError):
    """Raised during tag updating"""
    def __init__(self, message: str, http_status: int):
        super().__init__(message, status_code=http_status)


class DeleteTagError(BaseError):
    """Raised during tag deletion"""
    def __init__(self, message: str, http_status: int):
        super().__init__(message, status_code=http_status)

