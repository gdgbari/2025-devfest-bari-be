from domain.entities.user import User
from infrastructure.repositories.user_repository import UserRepository

class UserService:
    """"
    Service that manages all the operations related with a user
    """


    def __init__(
        self,
        user_repository: UserRepository
    ):
        self.user_repository = user_repository


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
        self.user_repository.delete(uid, user.nickname)


    def delete_all_users(self) -> None:
        """
        Deletes all users from database.
        """
        self.user_repository.delete_all()


    def assign_group_to_user(self, uid: str, gid: str) -> User:
        """
        Assigns a specific group to a user.
        """
        return self.user_repository.assign_group(uid, gid)
