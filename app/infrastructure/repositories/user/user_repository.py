from infrastructure.clients.firestore_client import FirestoreClient
from domain.entities.user import User
from infrastructure.errors.user_errors import CreateUserError

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


    def create_user(self, user: User) -> User:
        """
        Creates a new user document in the Firestore 'users' collection.
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