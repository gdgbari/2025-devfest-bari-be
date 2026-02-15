from typing import List
from infrastructure.repositories.user.user_repository import UserRepository
from infrastructure.repositories.group.group_repository import GroupRepository
from domain.entities.user import User
from domain.entities.group import Group
from infrastructure.repositories.tag.tag_repository import TagRepository


class ReadUserService:
    """
    Service that manages all the operations related with the reading of users.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        group_repository: GroupRepository,
        tag_repository: TagRepository
    ):
        self.user_repository = user_repository
        self.group_repository = group_repository
        self.tag_repository = tag_repository


    def read_user(self, uid: str) -> User:
        """
        Reads a user from the database and returns it as a User object
        with tags and group loaded.
        """
        user_data = self.user_repository.find_by_uid(uid)

        group_ref = user_data.get("group_ref")
        group: Group = None
        if group_ref is not None and hasattr(group_ref, "id"):
            group = self.group_repository.find_by_gid(group_ref.id)

        tags = self.tag_repository.find_by_tag_ids(user_data.get("tags"))
        user: User = User.from_dict(user_data, group=group, tags=tags)
        return user


    def read_all_users(self) -> List[User]:
        """
        Reads all the users in the database and returns a list of User
        with tags and group loaded.
        """
        users: List[User] = []
        users_data = self.user_repository.find_all()

        for user_data in users_data:
            group_ref = user_data.get("group_ref")
            group: Group = None
            if group_ref is not None and hasattr(group_ref, "id"):
                group = self.group_repository.find_by_gid(group_ref.id)
            tags = self.tag_repository.find_by_tag_ids(user_data.get("tags"))
            user: User = User.from_dict(user_data, group=group, tags=tags)
            users.append(user)
        return users
