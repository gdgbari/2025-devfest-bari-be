import random
from firebase_admin import firestore
from google.cloud.firestore import Transaction

from domain.entities.group import Group
from infrastructure.errors.firestore_errors import DocumentNotFoundError
from infrastructure.errors.group_errors import *
from infrastructure.clients.firestore_client import FirestoreClient


class GroupRepository:
    """
    Repository for managing all group operations with Firestore
    """

    GROUP_COLLECTION: str = "groups"
    GROUP_ID: str = "gid"
    GROUP_NAME: str = "name"
    GROUP_COLOR: str = "color"
    GROUP_IMAGE_URL: str = "image_url"
    GROUP_USER_COUNT: str = "userCount"

    def __init__(
        self,
        firestore_client: FirestoreClient
    ):
        self.firestore_client = firestore_client

    def create(self, group: Group) -> Group:
        """
        Creates a group in Firestore with auto-generated document ID.
        """
        try:
            gid = self.firestore_client.create_doc(
                collection_name=self.GROUP_COLLECTION, doc_id=None, doc_data=group.to_firestore_data()
            )
            group.gid = gid
            return group
        except Exception as exception:
            if "ALREADY_EXISTS" in str(exception) or "already exists" in str(exception).lower():
                raise CreateGroupError(message=f"Group already exists", http_status=409)
            raise CreateGroupError(message=f"Failed to create group", http_status=400)

    def read(self, gid: str) -> Group:
        """
        Reads a group from Firestore.
        """
        try:
            group_data_dict = self.firestore_client.read_doc(collection_name=self.GROUP_COLLECTION, doc_id=gid)
            return Group.from_dict({self.GROUP_ID: gid, **group_data_dict})
        except DocumentNotFoundError:
            raise ReadGroupError(message=f"Group not found", http_status=404)
        except Exception as exception:
            raise ReadGroupError(message=f"Failed to read group", http_status=400)

    def read_all(self) -> list[Group]:
        """
        Reads all groups from Firestore.
        """
        try:
            groups = self.firestore_client.read_all_docs(
                collection_name=self.GROUP_COLLECTION,
                include_id=True,
                id_field_name=self.GROUP_ID,
            )
            return [Group.from_dict(group) for group in groups]
        except Exception as exception:
            raise ReadGroupError(message=f"Failed to read all groups", http_status=400)

    def update(self, gid: str, group_update: dict) -> Group:
        """
        Updates a group in Firestore.
        """
        try:
            allowed_fields = {self.GROUP_NAME, self.GROUP_COLOR, self.GROUP_IMAGE_URL}
            update_params = {
                k: v for k, v in group_update.items()
                if v is not None and k in allowed_fields
            }

            if not update_params:
                # Nothing to update, just return current group
                return self.read(gid)

            self.firestore_client.update_doc(
                self.GROUP_COLLECTION,
                doc_id=gid,
                doc_data=update_params
            )
            return self.read(gid)
        except DocumentNotFoundError:
            raise UpdateGroupError(message=f"Group not found", http_status=404)
        except Exception as exception:
            raise UpdateGroupError(message=f"Failed to update group", http_status=400)

    def delete(self, gid: str) -> None:
        """
        Deletes a group from Firestore.
        """
        try:
            self.firestore_client.delete_doc(collection_name=self.GROUP_COLLECTION, doc_id=gid)
        except DocumentNotFoundError:
            raise DeleteGroupError(message=f"Group not found", http_status=404)
        except Exception:
            raise DeleteGroupError(message=f"Failed to delete group", http_status=400)

    def delete_all(self) -> None:
        """
        Deletes all groups from Firestore.
        """
        try:
            self.firestore_client.delete_all_docs(self.GROUP_COLLECTION)
        except Exception:
            raise DeleteGroupError(message=f"Failed to delete all groups", http_status=400)

    def decrement_user_count(self, gid: str) -> None:
        """
        Decrements the user_count field for a group.
        """
        try:
            group_doc = self.firestore_client.db.collection(self.GROUP_COLLECTION).document(gid)
            group_doc.update({self.GROUP_USER_COUNT: firestore.Increment(-1)})
        except Exception:
            raise UpdateGroupError(message=f"Failed to decrement user count", http_status=400)

    def increment_group_counter(self) -> str:
        groups_ref = self.firestore_client.db.collection(self.GROUP_COLLECTION)

        @firestore.transactional
        def update_in_transaction(transaction):
            groups_data = []

            for doc in groups_ref.stream():
                if doc.exists:
                    data = doc.to_dict()
                    data['gid'] = doc.id
                    groups_data.append(data)

            if not groups_data:
                raise ReadGroupError(message="No groups available", http_status=404)

            # Find the minimum userCount among all groups
            min_count = min(g.get(self.GROUP_USER_COUNT, 0) or 0 for g in groups_data)

            # Get all groups that have this minimum count
            min_groups = [g for g in groups_data if (g.get(self.GROUP_USER_COUNT, 0) or 0) == min_count]

            # If multiple groups have same count, pick one randomly for better distribution
            selected_group = random.choice(min_groups)
            selected_gid = selected_group['gid']

            # Increment the counter of the selected group atomically
            group_doc_ref = groups_ref.document(selected_gid)

            # Read current value from the data we already have
            current_count = selected_group.get(self.GROUP_USER_COUNT, 0) or 0

            # Update with the new value using transaction
            transaction.update(group_doc_ref, {
                self.GROUP_USER_COUNT: current_count + 1
            })

            return selected_gid

        try:
            # Execute the transaction
            transaction = self.firestore_client.db.transaction()
            return update_in_transaction(transaction)
        except Exception:
            raise UpdateGroupError(message=f"Failed to select group", http_status=400)
