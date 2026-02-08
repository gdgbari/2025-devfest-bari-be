from infrastructure.repositories.auth.auth_repository import AuthRepository
from domain.entities.user import User
from infrastructure.errors.auth_errors import AuthenticateUserError
from infrastructure.errors.user_errors import CreateUserError
from infrastructure.errors.leaderboard_errors import CreateLeaderboardUserEntryError
from infrastructure.repositories.nickname.nickname_repository import NicknameRepository
from infrastructure.repositories.user.user_repository import UserRepository
from infrastructure.repositories.leaderboard.user_leaderboard_repository import UserLeaderboardRepository


class CreateUserService:
    """"
    Service that manages all the operations related with the creation of a user
    """

    def __init__(
        self,
        auth_repository: AuthRepository,
        nickname_repository: NicknameRepository,
        user_repository: UserRepository,
        user_leaderboard_repository: UserLeaderboardRepository
    ):
        self.auth_repository = auth_repository
        self.nickname_repository = nickname_repository
        self.user_repository = user_repository
        self.user_leaderboard_repository = user_leaderboard_repository


    def create(self, user: User) -> User:
        """
        Create a user with unique nickname, then in firebase auth, in firestore, and leaderboard entry.
        If any exception happens at any step there is a rollback, in a way to keep consistent data.
        """
        try:
            # Reserve a nickname in the nicknames collection to check univocity
            self.nickname_repository.save(user.nickname)
            # Create user in authentication
            user = self.auth_repository.save(user)
            # Create user data in Firestore
            self.user_repository.save(user)
            # Create leaderboard user entry
            self.user_leaderboard_repository.save(user)
            # Return the updated user
            return user
        except AuthenticateUserError as e:
            self._handle_auth_error(user)
            raise e
        except CreateUserError as e:
            self._handle_create_error(user)
            raise e
        except CreateLeaderboardUserEntryError as e:
            self._handle_leaderboard_error(user)
            raise e


    def _handle_auth_error(self, user: User) -> None:
        """
        Rollback if auth repository had an error
        """
        self.nickname_repository.delete(user.nickname)


    def _handle_create_error(self, user: User) -> None:
        """
        Rollback if user repository had an error
        """
        self._handle_auth_error(user)
        if hasattr(user, 'uid') and user.uid:
            self.auth_repository.delete(user.uid)

    
    def _handle_leaderboard_error(self, user: User) -> None:
        """
        Rollback if user leaderboard repository had an error
        """
        self._handle_create_error(user)
        self.user_repository.delete(user.uid)

