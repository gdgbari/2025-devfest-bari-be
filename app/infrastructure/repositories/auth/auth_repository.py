from domain.entities.user import User
from firebase_admin.auth import EmailAlreadyExistsError
from infrastructure.clients.firebase_auth_client import FirebaseAuthClient
from infrastructure.errors.auth_errors import AuthenticateUserError, UpdateUserAuthError, DeleteUserAuthError


class AuthRepository:
    """
    Repository to manage all the operations with firebase auth.
    """

    def __init__(
        self,
        auth_client: FirebaseAuthClient,
    ):
        self.auth_client = auth_client


    def create_user_auth(self, user: User) -> User:
        """
        Creates a new user in Firebase Authentication.
        """
        try:
            uid = self.auth_client.create_user(
                email=user.email,
                password=user.password,
                display_name=f"{user.name} {user.surname}".strip(),
            )
            user.uid = uid
            return user
        except EmailAlreadyExistsError:
            raise AuthenticateUserError(message=f"Email already exsiting", http_status=409)
        except Exception:
            raise AuthenticateUserError(message=f"Failed to authenticate the user", http_status=400)


    def update_user_auth(self, uid: str, user: User) -> User:
        """
        Updates authentication information for an existing user in Firebase Authentication.
        """
        try:
            user_record = self.auth_client.update_user(uid, email=user.email)
            return User.from_dict(user_record)
        except Exception:
            raise UpdateUserAuthError(message=f"Failed to update user authentication", http_status=400)


    def delete_user_auth(self, uid: str) -> None:
        """
        Deletes a user account from Firebase Authentication.
        """
        try:
            self.auth_client.delete_user(uid)
        except Exception:
            raise DeleteUserAuthError(message=f"Failed to delete user", http_status=400)