from infrastructure.clients.firestore_client import FirestoreClient
from infrastructure.errors.firestore_errors import DocumentNotFoundError
from infrastructure.errors.tag_errors import ReadTagError
from domain.entities.tag import Tag

class TagRepository:
    """
    Repository for managing all tag operations with Firestore
    """

    TAGS_COLLECTION: str = "tags"


    def __init__(self, firestore_client: FirestoreClient):
        self.firestore_client = firestore_client


    def find_by_tag_id(self, tag_id: str) -> Tag:
        """
        Retrieves a single tag document from the Firestore 'tags' collection.
        """
        try:
            tag_data_dict = self.firestore_client.read_doc(
                collection_name=self.TAGS_COLLECTION,
                doc_id=tag_id
            )
            tag_data_dict["tag_id"] = tag_id
            return Tag.from_dict(tag_data_dict)
        except DocumentNotFoundError:
            raise ReadTagError(message=f"Tag not found", http_status=404)
        except Exception:
            raise ReadTagError(message=f"Failed to read tag", http_status=400)


    def find_by_tag_ids(self, tag_ids: list[str]) -> list[Tag]:
        """
        Loads Tag objects from tags collection using tag_ids.
        If a tag doesn't exist, it's ignored.
        """
        if not tag_ids:
            return None

        tags = []
        for tag_id in tag_ids:
            try:
                tag = self.find_by_tag_id(tag_id)
                tags.append(tag)
            except Exception:
                continue

        return tags if tags else None
