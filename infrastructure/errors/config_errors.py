from infrastructure.errors.base_error import BaseError

class ReadConfigError(BaseError):
    """Raised during config reading"""
    def __init__(self, message: str, http_status: int):
        super().__init__(message, status_code=http_status)

class CheckInNotOpenError(BaseError):
    """Raised when trying to check-in but check-in is not open"""
    def __init__(self, message: str = "Check-in is currently closed", http_status: int = 403):
        super().__init__(message, status_code=http_status)

