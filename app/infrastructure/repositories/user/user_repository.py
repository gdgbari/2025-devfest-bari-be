from infrastructure.clients.firestore_client import FirestoreClient
from domain.entities.user import User
from infrastructure.errors.user_errors import CreateUserError, DeleteUserError, ReadUserError
from infrastructure.errors.firestore_errors import *


class UserRepository:
    """
    Class for all the repository operations for user collection.
    """

    USERS_COLLECTION: str = "users"


    def __init__(
        self,
        firestore_client: FirestoreClient
    ):
        self.firestore_client = firestore_client


    def save(self, user: User) -> User:
        """
        Saves a new user document in the Firestore 'users' collection.
        """
        try:
            self.firestore_client.create_doc(
                collection_name=self.USERS_COLLECTION, doc_id=user.uid, doc_data=user.to_firestore_data()
            )
            return user
        except Exception as exception:
            if "ALREADY_EXISTS" in str(exception) or "already exists" in str(exception).lower():
                raise CreateUserError(message=f"User already existing", http_status=409)
            raise CreateUserError(message=f"Failed to create user", http_status=400)


    def delete(self, uid: str) -> None:
        """
        Deletes a user from the Firestore 'users' collection.
        """
        try:
            self.firestore_client.delete_doc(collection_name=self.USERS_COLLECTION, doc_id=uid)
        except DocumentNotFoundError:
            raise DeleteUserError(message=f"User was not found", http_status=404)
        except Exception:
            raise DeleteUserError(message=f"Failed to delete user", http_status=400)


    def find_by_uid(self, uid: str) -> dict:
        """
        Retrieves a single user document from the Firestore 'users' collection.

        This method fetches user profile data (email, name, surname, nickname) from Firestore
        using the Firebase Auth UID as the document ID. The UID is included in the returned
        dictionary for convenience.

        Raises:
            ReadUserError: If user retrieval fails. Specific scenarios:
                - HTTP 404: User document with this UID does not exist in Firestore
                - HTTP 400: Invalid UID format or other Firestore operation errors
        """
        try:
            user_data_dict = self.firestore_client.read_doc(
                collection_name=self.USERS_COLLECTION,
                doc_id=uid
            )
            user_data_dict["group_ref"] = user_data_dict.get("group")
            user_data_dict["group"] = None
            user_data_dict["uid"] = uid
            return user_data_dict
        except DocumentNotFoundError:
            raise ReadUserError(message=f"User was not found", http_status=404)
        except Exception:
            raise ReadUserError(message=f"Failed to read user", http_status=400)
