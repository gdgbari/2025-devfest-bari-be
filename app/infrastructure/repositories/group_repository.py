from domain.entities.group import Group
from infrastructure.errors.firestore_errors import DocumentNotFoundError
from infrastructure.errors.group_errors import *
from infrastructure.repositories.firestore_repository import \
    FirestoreRepository


class GroupRepository:
    """
    Repository for managing all group operations with Firestore
    """

    def __init__(
        self,
        firestore_repository: FirestoreRepository
    ):
        self.firestore_repository = firestore_repository

    def create(self, group: Group) -> Group:
        """
        Creates a group in Firestore with auto-generated document ID.
        """
        try:
            gid = self.firestore_repository.create_group(group)
            group.gid = gid
            return group
        except Exception as exception:
            if "ALREADY_EXISTS" in str(exception) or "already exists" in str(exception).lower():
                raise CreateGroupError(message=f"Group already exists: {group.name}", http_status=409)
            raise CreateGroupError(message=f"Failed to create group {group.name}: {str(exception)}", http_status=400)

    def read(self, gid: str) -> Group:
        """
        Reads a group from Firestore.
        """
        try:
            return Group.from_dict(self.firestore_repository.read_group(gid))
        except DocumentNotFoundError:
            raise ReadGroupError(message=f"Group not found: {gid}", http_status=404)
        except Exception as exception:
            raise ReadGroupError(message=f"Failed to read group {gid}: {str(exception)}", http_status=400)

    def read_all(self) -> list[Group]:
        """
        Reads all groups from Firestore.
        """
        try:
            groups = self.firestore_repository.read_all_groups()
            return [Group.from_dict(group) for group in groups]
        except Exception as exception:
            raise ReadGroupError(message=f"Failed to read all groups: {str(exception)}", http_status=400)

    def update(self, gid: str, group_update: dict) -> Group:
        """
        Updates a group in Firestore.
        """
        try:
            # Only update non-None fields
            update_dict = {k: v for k, v in group_update.items() if v is not None}
            self.firestore_repository.update_group(gid, update_dict)
            # Read back the updated group
            group_dict = self.firestore_repository.read_group(gid)
            return Group.from_dict(group_dict)
        except DocumentNotFoundError:
            raise UpdateGroupError(message=f"Group not found: {gid}", http_status=404)
        except Exception as exception:
            raise UpdateGroupError(message=f"Failed to update group {gid}: {str(exception)}", http_status=400)

    def delete(self, gid: str) -> None:
        """
        Deletes a group from Firestore.
        """
        try:
            self.firestore_repository.delete_group(gid)
        except DocumentNotFoundError:
            raise DeleteGroupError(message=f"Group not found: {gid}", http_status=404)
        except Exception as exception:
            raise DeleteGroupError(message=f"Failed to delete group {gid}: {str(exception)}", http_status=400)

    def delete_all(self) -> None:
        """
        Deletes all groups from Firestore.
        """
        try:
            self.firestore_repository.delete_all_groups()
        except Exception as exception:
            raise DeleteGroupError(message=f"Failed to delete all groups: {str(exception)}", http_status=400)

