import time

from firebase_admin import firestore

from infrastructure.clients.firestore_client import FirestoreClient
from infrastructure.errors.firestore_errors import DocumentNotFoundError
from infrastructure.errors.user_errors import CreateUserError
from infrastructure.errors.quiz_errors import IncrementScoreError


class LeaderboardRepository:
    """
    Repository for managing leaderboard entries in Firestore
    """

    LEADERBOARD_USER_COLLECTION: str = "leaderboard_users"
    LEADERBOARD_GROUP_COLLECTION: str = "leaderboard_groups"

    DEFAULT_GROUP_COLOR: str = "black"

    def __init__(self, firestore_client: FirestoreClient):
        self.firestore_client = firestore_client


    def _get_timestamp(self) -> int:
        """
        Returns the current timestamp in milliseconds.
        """
        return int(time.time() * 1000)


    def create_user_entry(self, uid: str, nickname: str) -> None:
        """
        Creates a leaderboard entry for a new user.
        """
        try:
            leaderboard_data = {
                "group_color": self.DEFAULT_GROUP_COLOR,
                "nickname": nickname,
                "score": 0,
                "updated_at": self._get_timestamp()
            }
            self.firestore_client.create_doc(
                collection_name=self.LEADERBOARD_USER_COLLECTION,
                doc_id=uid,
                doc_data=leaderboard_data
            )
        except Exception as e:
            raise CreateUserError(f"Failed to create leaderboard entry", http_status=400)


    def delete_user_entry(self, uid: str) -> None:
        """
        Deletes a leaderboard entry for a user.
        """
        try:
            self.firestore_client.delete_doc(
                collection_name=self.LEADERBOARD_USER_COLLECTION,
                doc_id=uid
            )
        except DocumentNotFoundError:
            # Ignore if entry doesn't exist (already deleted or never created)
            pass
        except Exception:
            # Ignore other errors during rollback
            pass


    def update_user_group_color(self, uid: str, group_color: str) -> None:
        """
        Updates the group_color for a user in the leaderboard.
        """
        try:
            update_data = {
                "group_color": group_color,
                "updated_at": self._get_timestamp()
            }
            self.firestore_client.update_doc(
                collection_name=self.LEADERBOARD_USER_COLLECTION,
                doc_id=uid,
                doc_data=update_data
            )
        except DocumentNotFoundError:
            # Ignore if entry doesn't exist (user might not have leaderboard entry)
            pass
        except Exception as e:
            raise CreateUserError(f"Failed to update user group color", http_status=400)


    def create_group_entry(self, group_id: str, group_name: str, group_color: str) -> None:
        """
        Creates a leaderboard entry for a group if it doesn't already exist.
        """
        try:
            # Check if entry already exists
            try:
                self.firestore_client.read_doc(
                    collection_name=self.LEADERBOARD_GROUP_COLLECTION,
                    doc_id=group_id
                )
                # Entry exists, skip creation
                return
            except DocumentNotFoundError:
                # Entry doesn't exist, create it
                pass

            leaderboard_data = {
                "color": group_color,
                "name": group_name,
                "score": 0,
                "updated_at": self._get_timestamp()
            }
            self.firestore_client.create_doc(
                collection_name=self.LEADERBOARD_GROUP_COLLECTION,
                doc_id=group_id,
                doc_data=leaderboard_data
            )
        except Exception as e:
            raise CreateUserError(f"Failed to create group leaderboard entry", http_status=400)

    def increment_user_score(self, uid: str, points: int) -> None:
        """
        Atomically increments the score for a user in the leaderboard.
        Uses Firestore Increment to ensure atomicity and handle concurrency.

        Args:
            uid (str): The user's UID (document ID)
            points (int): The points to add (can be positive or negative)
        """
        try:
            user_doc = self.firestore_client.db.collection(self.LEADERBOARD_USER_COLLECTION).document(uid)
            user_doc.update({
                "score": firestore.Increment(points),
                "updated_at": self._get_timestamp()
            })
        except Exception as e:
            raise IncrementScoreError(f"Failed to increment user score", http_status=400)

    def increment_group_score(self, group_id: str, points: int) -> None:
        """
        Atomically increments the score for a group in the leaderboard.
        Uses Firestore Increment to ensure atomicity and handle concurrency.

        Args:
            group_id (str): The group's ID (document ID)
            points (int): The points to add (can be positive or negative)
        """
        try:
            group_doc = self.firestore_client.db.collection(self.LEADERBOARD_GROUP_COLLECTION).document(group_id)
            group_doc.update({
                "score": firestore.Increment(points),
                "updated_at": self._get_timestamp()
            })
        except Exception as e:
            raise IncrementScoreError(f"Failed to increment group score", http_status=400)

