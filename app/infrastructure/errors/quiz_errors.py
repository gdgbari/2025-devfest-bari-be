from infrastructure.errors.base_error import BaseError


class CreateQuizError(BaseError):
    """Raised during quiz creation"""
    def __init__(self, message: str, http_status: int):
        super().__init__(message, status_code=http_status)


class DeleteQuizError(BaseError):
    """Raised during quiz deletion"""
    def __init__(self, message: str, http_status: int):
        super().__init__(message, status_code=http_status)


class ReadQuizError(BaseError):
    """Raised during quiz reading"""
    def __init__(self, message: str, http_status: int):
        super().__init__(message, status_code=http_status)


class UpdateQuizError(BaseError):
    """Raised during quiz updating"""
    def __init__(self, message: str, http_status: int):
        super().__init__(message, status_code=http_status)

