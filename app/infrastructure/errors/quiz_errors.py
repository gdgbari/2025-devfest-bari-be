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


class QuizAlreadySubmittedError(BaseError):
    """Raised when user tries to submit a quiz they already submitted"""
    def __init__(self, message: str = "Quiz already submitted", http_status: int = 409):
        super().__init__(message, status_code=http_status)


class QuizTimeUpError(BaseError):
    """Raised when quiz time has expired"""
    def __init__(self, message: str = "Quiz time is up", http_status: int = 408):
        super().__init__(message, status_code=http_status)


class QuizStartTimeNotFoundError(BaseError):
    """Raised when quiz start time is not found for user"""
    def __init__(self, message: str = "Quiz start time not found", http_status: int = 404):
        super().__init__(message, status_code=http_status)


class InvalidAnswerListError(BaseError):
    """Raised when answer list length doesn't match questions"""
    def __init__(self, message: str, http_status: int = 400):
        super().__init__(message, status_code=http_status)


class IncrementScoreError(BaseError):
    """Raised when incrementing leaderboard scores fails"""
    def __init__(self, message: str = "Failed to increment score", http_status: int = 400):
        super().__init__(message, status_code=http_status)

