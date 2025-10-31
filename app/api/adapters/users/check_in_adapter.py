from api.schemas.users.check_in_schema import CheckInResponse
from domain.entities.user import User

class CheckInAdapter:
    """
    Adapter for converting User domain object to CheckInResponse
    """
    
    @staticmethod
    def to_response(user: User) -> CheckInResponse:
        return CheckInResponse(
            group=user.group,
        )