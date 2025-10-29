from domain.entities.user import User
from domain.services.group_service import GroupService
from domain.services.user_service import UserService

class CheckInService:
    """"
    Service that manages all the operations related with the check in phase
    """


    def __init__(
        self,
        user_service: UserService,
        group_service: GroupService
    ):
        self.user_service = user_service
        self.group_service = group_service


    def check_in(self, uid: str) -> User:
        """
        Performs check-in assigning a group to the user to be checked in.
        """
        
        # Find group to be assigned
        selected_group = self.group_service.find_group_with_least_users()
        
        # Assign the group
        updated_user = self.user_service.assign_group_to_user(uid, selected_group.gid)
        
        # Raise up the counter for the group selected
        self.group_service.increment_user_count(selected_group.gid)

        return updated_user