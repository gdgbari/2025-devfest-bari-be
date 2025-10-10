from domain.entities.user import User
from infrastructure.repositories.auth_repository import AuthRepository
from infrastructure.repositories.user_repository import UserRepository

class UserService:
    """"
    Service that manages all the interaction related with a user
    """

    def __init__(
        self, 
        auth_repository: AuthRepository,
        user_repository: UserRepository
    ):
        self.auth_repository = auth_repository
        self.user_repository = user_repository

    def create_user(self, user: User) -> User:
        """
        Creates a user in Firebase Auth, then in Firestore.
        Returns the created user as a response schema.
        """
        try:
            # Create user in Firebase Auth
            uid = self.auth_repository.create_user(user)
            # Set UID for Firestore
            user.uid = uid
            # Create user data in Firestore
            self.user_repository.create_user(user)
            # Return new user
            return user
        except:
            # Rollback
            self.delete_user(user.uid)

    def read_user(self, uid: str) -> User:
        """
        Reads a user from Firestore and returns it as a response schema.
        """
        return User.from_dict(self.user_repository.read_user(uid))

    def read_all_users(self) -> list[User]:
        """
        Reads all users from Firestore and returns them as a list of response schemas.
        """
        users: list[dict] = self.user_repository.read_all_users()
        return [User.from_dict(user) for user in users]

    def update_user(self, uid: str, user_update: dict) -> User:
        """
        Updates a user in Firebase Auth, then in Firestore.
        Returns the updated user as a response schema.
        """
        current_user: User = self.read_user(uid)
        
        if user_update["email"]:
            # Update in Firebase Auth
            self.auth_repository.update_user(uid, user_update)

        # Update in Firestore
        self.user_repository.update_user(uid, user_update)

        return User(
            uid=current_user.uid,
            email=current_user.email,
            name=user_update["name"] if user_update["name"] is not None else current_user.name,
            surname=user_update["surname"] if user_update["surname"] is not None else current_user.surname,
            nickname=current_user.nickname,
        )
    
    def delete_user(self, uid: str) -> None:
        """
        Deletes a user from Firebase Auth, then from Firestore.
        Returns None.
        """
        if uid is not None:
            self.auth_repository.delete_user(uid)
            self.user_repository.delete_user(uid)

    def delete_all_users(self) -> None:
        """
        Deletes all users from Firebase Auth, then from Firestore.
        Returns None.
        """
        self.auth_repository.delete_all_users()
        self.user_repository.delete_all_users()
