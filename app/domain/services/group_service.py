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

    def increment_user_count(self, gid: str) -> None:
        """
        Increments the user count for a group.
        """
        self.group_repository.increment_user_count(gid)

    def find_group_with_least_users(self) -> Group:
        """
        Finds the group with the least number of users for partially round-robin assignment.
        If the groups have the same amount of users, the group is selected random
        """
        groups = self.read_all_groups()
        if not groups:
            raise Exception("No groups available for assignment")

        # Find minimum user count
        min_count = min(g.user_count if g.user_count is not None else 0 for g in groups)
        
        # Filter groups with minimum
        min_groups = [g for g in groups if (g.user_count if g.user_count is not None else 0) == min_count]
        
        # Random choice between them
        return random.choice(min_groups)

