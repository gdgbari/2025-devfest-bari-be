from infrastructure.clients.firestore_client import FirestoreClient
from infrastructure.errors.user_errors import ReserveNicknameError
from infrastructure.errors.firestore_errors import *
from infrastructure.errors.user_errors import DeleteUserError


class NicknameRepository:
    """
    Class responsible for all the operations related with nickname table
    """

    NICKNAMES_COLLECTION: str = "nicknames"

    def __init__(
        self,
        firestore_client: FirestoreClient
    ):
        self.firestore_client = firestore_client


    def save(self, nickname: str) -> None:
        """
        Saves a nickname by creating a document in the Firestore 'nicknames' collection.

        The nickname is normalized (lowercase, no whitespace) for storage in the nicknames
        collection to ensure uniqueness, but the original nickname is preserved in the users collection.

        This method ensures nickname uniqueness across the application by attempting to create
        a document with the normalized nickname as the document ID.
        """
        try:
            self.firestore_client.create_doc(
                self.NICKNAMES_COLLECTION, 
                doc_id=self._normalize_nickname(nickname)
            )
        except Exception as exception:
            if "ALREADY_EXISTS" in str(exception) or "already exists" in str(exception).lower():
                raise ReserveNicknameError(message=f"Nickname already existing", http_status=409)
            raise ReserveNicknameError(message=f"Failed to create nickname", http_status=400)
        

    def _normalize_nickname(self, nickname: str) -> str:
        """
        Converts to lowercase and removes whitespace.
        """
        return nickname.lower().replace(" ", "")
    

    def delete_nickname(self, nickname: str) -> None:
        """
        Deletes a nickname reservation from the Firestore 'nicknames' collection.
        """
        try:
            self.firestore_client.delete_doc(
                collection_name=self.NICKNAMES_COLLECTION, 
                doc_id=self._normalize_nickname(nickname)
            )
        except DocumentNotFoundError:
            raise DeleteUserError(message=f"Nickname not found", http_status=404)
        except Exception:
            raise DeleteUserError(message=f"Failed to delete nickname", http_status=400)