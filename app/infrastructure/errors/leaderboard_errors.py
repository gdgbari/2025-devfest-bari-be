from infrastructure.errors.base_error import BaseError

class CreateLeaderboardUserEntryError(BaseError):
    """Raised during leaderboard user creation with firestore"""
    def __init__(self, message: str, http_status: int):
        super().__init__(message, status_code=http_status)