from domain.entities.user import User
from infrastructure.repositories.user_repository import UserRepository
from domain.services.group_service import GroupService

class UserService:
    """"
    Service that manages all the operations related with a user
    """


    def __init__(
        self,
        user_repository: UserRepository,
        group_service: GroupService
    ):
        self.user_repository = user_repository
        self.group_service = group_service


    def create_user(self, user: User) -> User:
        """
        Creates a user in database.
        """
        return self.user_repository.create(user)


    def read_user(self, uid: str) -> User:
        """
        Reads a user from database.
        """
        return self.user_repository.read(uid)


    def read_all_users(self) -> list[User]:
        """
        Reads all users in database.
        """
        return self.user_repository.read_all()


    def update_user(self, uid: str, user_update: dict) -> User:
        """
        Recover a user from uid in database and the updates it.
        """
        current_user: User = self.read_user(uid)
        return self.user_repository.update(user_update=user_update, current_user=current_user)


    def delete_user(self, uid: str) -> None:
        """
        Deletes a user from the database.
        """
        user = self.read_user(uid)

        # Decrement group counter if user has a group assigned
        if user.group:
            group_id = user.group.get("gid")
            if group_id:
                self.group_service.decrement_user_count(group_id)

        self.user_repository.delete(uid, user.nickname)


    def delete_all_users(self) -> None:
        """
        Deletes all users from database.
        """
        self.user_repository.delete_all()

        # Reset all group counters
        self.group_service.reset_all_user_counts()


    def assign_group_to_user(self, uid: str, gid: str) -> User:
        """
        Assigns a specific group to a user.
        """
        return self.user_repository.assign_group(uid, gid)
