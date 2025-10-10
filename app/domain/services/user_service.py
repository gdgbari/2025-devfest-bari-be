from domain.entities.user import User
from infrastructure.repositories.auth_repository import AuthRepository
from infrastructure.repositories.user_repository import UserRepository

class UserService:
    @staticmethod
    def create_user(user: User) -> User:
        """
        Creates a user in Firebase Auth, then in Firestore.
        Returns the created user as a response schema.
        """
        try:
            # Create user in Firebase Auth
            uid = AuthRepository.create_user(user)
            # Set UID for Firestore
            user.uid = uid
            # Create user data in Firestore
            UserRepository.create_user(user)
            # Return new user
            return user
        except:
            # Rollback
            if user.uid is not None:
                AuthRepository.delete_user(user.uid)
                UserRepository.delete_user(user.uid)

    @staticmethod
    def read_user(uid: str) -> User:
        """
        Reads a user from Firestore and returns it as a response schema.
        """
        return User.from_dict(UserRepository.read_user(uid))

    @staticmethod
    def read_all_users() -> list[User]:
        """
        Reads all users from Firestore and returns them as a list of response schemas.
        """
        users: list[dict] = UserRepository.read_all_users()
        return [User.from_dict(user) for user in users]

    @staticmethod
    def update_user(uid: str, user_update: dict) -> User:
        """
        Updates a user in Firebase Auth, then in Firestore.
        Returns the updated user as a response schema.
        """
        current_user: User = User.from_dict(UserRepository.read_user(uid))
        
        if user_update["email"]:
            # Update in Firebase Auth
            AuthRepository.update_user(uid, user_update)

        # Update in Firestore
        UserRepository.update_user(uid, user_update)

        return User(
            uid=current_user.uid,
            email=current_user.email,
            name=user_update["name"] if user_update["name"] is not None else current_user.name,
            surname=user_update["surname"] if user_update["surname"] is not None else current_user.surname,
            nickname=current_user.nickname,
        )

    @staticmethod
    def delete_user(uid: str) -> None:
        """
        Deletes a user from Firebase Auth, then from Firestore.
        Returns None.
        """
        AuthRepository.delete_user(uid)
        UserRepository.delete_user(uid)

    @staticmethod
    def delete_all_users() -> None:
        """
        Deletes all users from Firebase Auth, then from Firestore.
        Returns None.
        """
        AuthRepository.delete_all_users()
        UserRepository.delete_all_users()
