from infrastructure.repositories.auth_repository import AuthRepository
from infrastructure.repositories.firestore_repository import FirestoreRepository
from domain.entities.user import User

class UserRepository:
    """
    Repository for managing all user operations
    """

    def __init__(
        self,
        auth_repository: AuthRepository,
        firestore_repository: FirestoreRepository
    ):
        self.auth_repository = auth_repository
        self.firestore_repository = firestore_repository

    def create(self, user: User) -> User:
        uid = self.auth_repository.create(user)
        # Set UID for Firestore
        user.uid = uid
        # Create user data in Firestore
        self.firestore_repository.create(user)
        # Return new user
        return user
    
    def delete(self, uid: str) -> None:
        """
        Deletes a user from Firebase Auth, then from Firestore.
        Returns None.
        """
        if uid is not None:
            self.auth_repository.delete(uid)
            self.firestore_repository.delete(uid)

    def delete_all(self) -> None:
        """
        Deletes all users from Firebase Auth, then from Firestore.
        Returns None.
        """
        self.auth_repository.delete_all()
        self.firestore_repository.delete_all()

    def read(self, uid: str) -> User:
        """
        Reads a user from Firestore and returns it as a response schema.
        """
        return User.from_dict(self.firestore_repository.read(uid))
    
    def read_all(self) -> list[User]:
        """
        Reads all users from Firestore and returns them as a list of response schemas.
        """
        users: list[dict] = self.firestore_repository.read_all()
        return [User.from_dict(user) for user in users]
    
    def update(self, user_update: dict, current_user: User) -> User:
        """
        Update a current user with the update information and then
        return the user updated
        """
        if user_update["email"]:
            # Update in Firebase Auth
            self.auth_repository.update(current_user.uid, user_update)

        # Update in Firestore
        self.firestore_repository.update(current_user.uid, user_update)

        return User(
            uid=current_user.uid,
            email=user_update["email"] if user_update["email"] is not None else current_user.email,
            name=user_update["name"] if user_update["name"] is not None else current_user.name,
            surname=user_update["surname"] if user_update["surname"] is not None else current_user.surname,
            nickname=current_user.nickname,
        )

