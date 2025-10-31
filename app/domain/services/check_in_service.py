from domain.entities.user import User
from domain.services.group_service import GroupService
from domain.services.user_service import UserService
from domain.services.config_service import ConfigService
from infrastructure.errors.config_errors import CheckInNotOpenError

class CheckInService:
    """"
    Service that manages all the operations related with the check in phase
    """


    def __init__(
        self,
        user_service: UserService,
        group_service: GroupService,
        config_service: ConfigService
    ):
        self.user_service = user_service
        self.group_service = group_service
        self.config_service = config_service


    def check_in(self, uid: str) -> User:
        """
        Performs check-in assigning a group to the user to be checked in.

        Raises:
            CheckInNotOpenError: If check-in is currently closed
        """

        # Check if check-in is open
        if not self.config_service.is_check_in_open():
            raise CheckInNotOpenError()

        # Atomically find group and increment counter to prevent race conditions
        selected_gid = self.group_service.increment_group_counter()

        # Assign the group to the user and update custom claims
        updated_user = self.user_service.assign_group_to_user(uid, selected_gid)

        return updated_user
