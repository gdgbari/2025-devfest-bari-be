from domain.entities.tag import Tag
from infrastructure.clients.firestore_client import FirestoreClient
from infrastructure.errors.firestore_errors import DocumentNotFoundError
from infrastructure.errors.tag_errors import (
    CreateTagError,
    ReadTagError,
    UpdateTagError,
    DeleteTagError
)


class TagsRepository:
    """
    Repository for managing all tag operations with Firestore
    """

    TAGS_COLLECTION: str = "tags"
    TAG_ID: str = "tag_id"

    def __init__(self, firestore_client: FirestoreClient):
        self.firestore_client = firestore_client

    def create(self, tag: Tag, tag_id: str = None) -> Tag:
        """
        Creates a tag in Firestore with specified or auto-generated document ID.
        """
        try:
            created_tag_id = self.firestore_client.create_doc(
                collection_name=self.TAGS_COLLECTION,
                doc_id=tag_id,
                doc_data=tag.to_firestore_data()
            )
            tag.tag_id = created_tag_id
            return tag
        except Exception as exception:
            if "ALREADY_EXISTS" in str(exception) or "already exists" in str(exception).lower():
                raise CreateTagError(message="Tag already exists", http_status=409)
            raise CreateTagError(message="Failed to create tag", http_status=400)

    def read(self, tag_id: str) -> Tag:
        """
        Reads a tag from Firestore.
        """
        try:
            tag_data_dict = self.firestore_client.read_doc(
                collection_name=self.TAGS_COLLECTION,
                doc_id=tag_id
            )
            return Tag.from_dict({self.TAG_ID: tag_id, **tag_data_dict})
        except DocumentNotFoundError:
            raise ReadTagError(message="Tag not found", http_status=404)
        except Exception:
            raise ReadTagError(message="Failed to read tag", http_status=400)

    def read_all(self) -> list[Tag]:
        """
        Reads all tags from Firestore.
        """
        try:
            tags = self.firestore_client.read_all_docs(
                collection_name=self.TAGS_COLLECTION,
                include_id=True,
                id_field_name=self.TAG_ID,
            )
            return [Tag.from_dict(tag) for tag in tags]
        except Exception:
            raise ReadTagError(message="Failed to read all tags", http_status=400)

    def update(self, tag_id: str, tag_update: dict) -> Tag:
        """
        Updates a tag in Firestore.
        """
        try:
            allowed_fields = {"points"}
            update_params = {
                k: v for k, v in tag_update.items()
                if v is not None and k in allowed_fields
            }

            if not update_params:
                # Nothing to update, just return current tag
                return self.read(tag_id)

            self.firestore_client.update_doc(
                collection_name=self.TAGS_COLLECTION,
                doc_id=tag_id,
                doc_data=update_params
            )
            return self.read(tag_id)
        except DocumentNotFoundError:
            raise UpdateTagError(message="Tag not found", http_status=404)
        except Exception:
            raise UpdateTagError(message="Failed to update tag", http_status=400)

    def delete(self, tag_id: str) -> None:
        """
        Deletes a tag from Firestore.
        """
        try:
            self.firestore_client.delete_doc(
                collection_name=self.TAGS_COLLECTION,
                doc_id=tag_id
            )
        except DocumentNotFoundError:
            raise DeleteTagError(message="Tag not found", http_status=404)
        except Exception:
            raise DeleteTagError(message="Failed to delete tag", http_status=400)

