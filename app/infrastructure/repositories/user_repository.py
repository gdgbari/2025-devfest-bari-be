from typing import Optional, List
from infrastructure.repositories.firebase_auth_repository import FirebaseAuthRepository
from infrastructure.repositories.firestore_repository import FirestoreRepository
from infrastructure.repositories.leaderboard_repository import LeaderboardRepository
from domain.entities.user import User
from domain.entities.quiz_result import QuizResult
from domain.entities.quiz_start_time import QuizStartTime
from infrastructure.errors.user_errors import *
from infrastructure.errors.auth_errors import *
from infrastructure.errors.firestore_errors import DocumentNotFoundError

class UserRepository:
    """
    Repository for managing all user operations coordinating firebase auth and firestore
    """

    # Collection names
    QUIZ_RESULTS_COLLECTION: str = "quiz_results"
    QUIZ_START_TIMES_COLLECTION: str = "quiz_start_times"

    # User field names
    USER_EMAIL: str = "email"
    USER_NAME: str = "name"
    USER_SURNAME: str = "surname"

    def __init__(
        self,
        auth_repository: FirebaseAuthRepository,
        firestore_repository: FirestoreRepository,
        leaderboard_repository: LeaderboardRepository
    ):
        self.auth_repository = auth_repository
        self.firestore_repository = firestore_repository
        self.leaderboard_repository = leaderboard_repository


    def create(self, user: User) -> User:
        """
        Create a user with unique nickname, then in firebase auth, in firestore, and leaderboard entry.
        If any exception happens at any step there is a rollback, in a way to keep consistent data.
        """
        try:
            # Reserve a nickname in the nicknames collection to check univocity
            self.firestore_repository.reserve_nickname(user.nickname)
            # Create user in authentication
            uid = self.auth_repository.create_user_authentication(user)
            # Set UID for Firestore
            user.uid = uid
            # Create user data in Firestore
            self.firestore_repository.create_user(user)
            # Create leaderboard entry
            self.leaderboard_repository.create_user_entry(uid, user.nickname)
            # Return new user
            return user
        except AuthenticateUserError as e:
            self.firestore_repository.delete_nickname(user.nickname)
            raise e
        except CreateUserError as e:
            self.firestore_repository.delete_nickname(user.nickname)
            if hasattr(user, 'uid') and user.uid:
                self.auth_repository.delete_auth(user.uid)
                # Try to delete leaderboard entry if it was created
                self.leaderboard_repository.delete_user_entry(user.uid)
            raise e


    def delete(self, uid: str, nickname: str) -> None:
        """
        Deletes a user from Firebase Auth, Firestore, and leaderboard.
        Returns None.
        """
        self.firestore_repository.delete_nickname(nickname)
        self.auth_repository.delete_auth(uid)
        self.firestore_repository.delete_user(uid)
        # Delete leaderboard entry if present
        self.leaderboard_repository.delete_user_entry(uid)


    def read(self, uid: str) -> User:
        """
        Reads a user from Firestore and returns it as a response schema.
        Note: Tags are not loaded. Use UserService.read_user() to get tags.
        """
        return User.from_dict(self.firestore_repository.read_user(uid), tags=None)

    def read_raw(self, uid: str) -> dict:
        """
        Reads a user from Firestore and returns raw dict.
        Used when tags need to be loaded separately.
        """
        return self.firestore_repository.read_user(uid)

    def read_all(self) -> list[User]:
        """
        Reads all users from Firestore and returns them as a list of response schemas.
        Note: Tags are not loaded. Use UserService.read_all_users() to get tags.
        """
        users: list[dict] = self.firestore_repository.read_all_users()
        return [User.from_dict(user, tags=None) for user in users]

    def read_all_raw(self) -> list[dict]:
        """
        Reads all users from Firestore and returns raw dicts.
        Used when tags need to be loaded separately.
        """
        return self.firestore_repository.read_all_users()


    def update(self, user_update: dict, current_user: User) -> User:
        """
        Update a current user with the update information and then
        return the user updated. If email is present in the updated fields is gonna
        update also the authentication
        """
        if user_update[self.USER_EMAIL]:
            # Update in Firebase Auth
            self.auth_repository.update_user_auth(current_user.uid, user_update)

        # Update in Firestore
        self.firestore_repository.update_user(current_user.uid, user_update)

        return User(
            uid=current_user.uid,
            email=user_update[self.USER_EMAIL] if user_update[self.USER_EMAIL] is not None else current_user.email,
            name=user_update[self.USER_NAME] if user_update[self.USER_NAME] is not None else current_user.name,
            surname=user_update[self.USER_SURNAME] if user_update[self.USER_SURNAME] is not None else current_user.surname,
            nickname=current_user.nickname,
            role=current_user.role,
            group=current_user.group
        )


    def assign_group(self, uid: str, gid: str) -> User:
        """
        Assigns a group to a user.
        """
        self.firestore_repository.assign_group_to_user(uid, gid)
        self.auth_repository.update_custom_claims(uid=uid, claims={"checked_in": True})

        return self.read(uid)

    def add_tags(self, uid: str, tags: List[str]) -> User:
        """
        Adds tags to user's tags list.
        Returns updated user.
        """
        self.firestore_repository.add_tags_to_user(uid, tags)
        return self.read(uid)


    def get_quiz_result(self, uid: str, quiz_id: str) -> Optional[QuizResult]:
        """
        Get quiz result for a user if it exists.
        Returns None if not found.
        """
        try:
            data = self.firestore_repository.read_from_subcollection(
                document_id=uid,
                subcollection=self.QUIZ_RESULTS_COLLECTION,
                subdocument_id=quiz_id
            )
            return QuizResult.from_dict(data)
        except DocumentNotFoundError:
            return None


    def save_quiz_result(self, uid: str, quiz_id: str, result: QuizResult) -> None:
        """
        Save quiz result to user's quiz_results subcollection.
        """
        self.firestore_repository.write_to_subcollection(
            document_id=uid,
            subcollection=self.QUIZ_RESULTS_COLLECTION,
            subdocument_id=quiz_id,
            data=result.to_firestore_data()
        )


    def get_quiz_start_time(self, uid: str, quiz_id: str) -> Optional[QuizStartTime]:
        """
        Get quiz start time for a user if it exists.
        Returns None if not found.
        """
        try:
            data = self.firestore_repository.read_from_subcollection(
                document_id=uid,
                subcollection=self.QUIZ_START_TIMES_COLLECTION,
                subdocument_id=quiz_id
            )
            return QuizStartTime.from_dict(data)
        except DocumentNotFoundError:
            return None


    def save_quiz_start_time(self, uid: str, quiz_id: str, start_time: QuizStartTime) -> None:
        """
        Save quiz start time to user's quiz_start_times subcollection.
        """
        self.firestore_repository.write_to_subcollection(
            document_id=uid,
            subcollection=self.QUIZ_START_TIMES_COLLECTION,
            subdocument_id=quiz_id,
            data=start_time.to_firestore_data()
        )
