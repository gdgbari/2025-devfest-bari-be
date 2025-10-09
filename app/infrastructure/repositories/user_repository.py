from infrastructure.repositories.firebase_auth_repository import FirebaseAuthRepository
from infrastructure.repositories.firestore_repository import FirestoreRepository
from domain.entities.user import User
from infrastructure.errors.user_errors import *
from infrastructure.errors.auth_errors import *

class UserRepository:
    """
    Repository for managing all user operations coordinating firebase auth and firestore
    """


    def __init__(
        self,
        auth_repository: FirebaseAuthRepository,
        firestore_repository: FirestoreRepository
    ):
        self.auth_repository = auth_repository
        self.firestore_repository = firestore_repository


    def create(self, user: User) -> User:
        """
        Create a user with unique nickname, then in firebase auth and in the end in firestore.
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
            # Return new user
            return user
        except AuthenticateUserError as e:
            self.firestore_repository.delete_nickname(user.nickname)
            raise e
        except CreateUserError as e:
            self.firestore_repository.delete_nickname(user.nickname)
            self.auth_repository.delete_auth(user.uid)
            raise e


    def delete(self, uid: str, nickname: str) -> None:
        """
        Deletes a user from Firebase Auth, then from Firestore.
        Returns None.
        """
        self.firestore_repository.delete_nickname(nickname)
        self.auth_repository.delete_auth(uid)
        self.firestore_repository.delete_user(uid)


    def delete_all(self) -> None:
        """
        Deletes all users from Firebase Auth, then from Firestore.
        Returns None.
        """
        self.firestore_repository.delete_all_nicknames()
        self.auth_repository.delete_all()
        self.firestore_repository.delete_all_users()


    def read(self, uid: str) -> User:
        """
        Reads a user from Firestore and returns it as a response schema.
        """
        return User.from_dict(self.firestore_repository.read_user(uid))


    def read_all(self) -> list[User]:
        """
        Reads all users from Firestore and returns them as a list of response schemas.
        """
        users: list[dict] = self.firestore_repository.read_all_users()
        return [User.from_dict(user) for user in users]


    def update(self, user_update: dict, current_user: User) -> User:
        """
        Update a current user with the update information and then
        return the user updated. If email is present in the updated fields is gonna
        update also the authentication
        """
        if user_update["email"]:
            # Update in Firebase Auth
            self.auth_repository.update_user_auth(current_user.uid, user_update)

        # Update in Firestore
        self.firestore_repository.update_user(current_user.uid, user_update)

        return User(
            uid=current_user.uid,
            email=user_update["email"] if user_update["email"] is not None else current_user.email,
            name=user_update["name"] if user_update["name"] is not None else current_user.name,
            surname=user_update["surname"] if user_update["surname"] is not None else current_user.surname,
            nickname=current_user.nickname,
            role=current_user.role,
            group=current_user.group
        )

