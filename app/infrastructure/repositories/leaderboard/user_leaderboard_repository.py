import time

from infrastructure.clients.firestore_client import FirestoreClient
from infrastructure.errors.user_errors import CreateUserError
from domain.entities.user import User


class UserLeaderboardRepository:

    LEADERBOARD_USER_COLLECTION: str = "leaderboard_users"
    DEFAULT_GROUP_COLOR: str = "black"


    def __init__(self, firestore_client: FirestoreClient):
        self.firestore_client = firestore_client

    def create_user_entry(self, user: User) -> None:
        """
        Creates a leaderboard entry for a new user.
        """
        try:
            leaderboard_data = {
                "group_color": self.DEFAULT_GROUP_COLOR,
                "nickname": user.nickname,
                "score": 0,
                "updated_at": self._get_timestamp()
            }
            self.firestore_client.create_doc(
                collection_name=self.LEADERBOARD_USER_COLLECTION,
                doc_id=user.uid,
                doc_data=leaderboard_data
            )
        except Exception:
            raise CreateUserError(f"Failed to create leaderboard entry", http_status=400)
        
    def _get_timestamp(self) -> int:
        """
        Returns the current timestamp in milliseconds.
        """
        return int(time.time() * 1000)