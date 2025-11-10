import random

from domain.entities.group import Group
from infrastructure.repositories.group_repository import GroupRepository


class GroupService:
    """
    Service that manages all the operations related with a group
    """

    def __init__(
        self,
        group_repository: GroupRepository
    ):
        self.group_repository = group_repository

    def create_group(self, group: Group) -> Group:
        """
        Creates a group in database.
        """
        return self.group_repository.create(group)

    def read_group(self, gid: str) -> Group:
        """
        Reads a group from database.
        """
        return self.group_repository.read(gid)

    def read_all_groups(self) -> list[Group]:
        """
        Reads all groups in database.
        """
        return self.group_repository.read_all()

    def update_group(self, gid: str, group_update: dict) -> Group:
        """
        Recover a group from gid in database and then updates it.
        """
        current_group: Group = self.read_group(gid)
        return self.group_repository.update(gid, group_update)

    def delete_group(self, gid: str) -> None:
        """
        Deletes a group from the database.
        """
        self.group_repository.delete(gid)

    def delete_all_groups(self) -> None:
        """
        Deletes all groups from database.
        """
        self.group_repository.delete_all()

    def decrement_user_count(self, gid: str) -> None:
        """
        Decrements the user count for a group.
        """
        self.group_repository.decrement_user_count(gid)

    def increment_group_counter(self) -> str:
        """
        Increment group counter of the group with least users
        """
        return self.group_repository.increment_group_counter()

