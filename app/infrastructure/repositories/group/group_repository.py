from infrastructure.clients.firestore_client import FirestoreClient
from infrastructure.errors.firestore_errors import DocumentNotFoundError
from infrastructure.errors.group_errors import ReadGroupError
from domain.entities.group import Group

class GroupRepository:
    """
    Repository for managing all group operations with Firestore
    """

    GROUP_COLLECTION: str = "groups"


    def __init__(self, firestore_client: FirestoreClient):
        self.firestore_client = firestore_client


    def find_by_gid(self, gid: str) -> Group:
        """
        Retrieves a single group document from the Firestore 'groups' collection.
        """
        try:
            group_data_dict = self.firestore_client.read_doc(
                collection_name=self.GROUP_COLLECTION,
                doc_id=gid
            )
            group_data_dict["gid"] = gid
            return Group.from_dict(group_data_dict)
        except DocumentNotFoundError:
            raise ReadGroupError(message=f"Group not found", http_status=404)
        except Exception:
            raise ReadGroupError(message=f"Failed to read group", http_status=400)
