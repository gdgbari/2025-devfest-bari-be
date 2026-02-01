from infrastructure.repositories.auth.auth_repository import AuthRepository
from domain.entities.user import User
from infrastructure.errors.auth_errors import AuthenticateUserError
from infrastructure.errors.user_errors import CreateUserError
from infrastructure.repositories.nickname.nickname_repository import NicknameRepository
from infrastructure.repositories.user.user_repository import UserRepository


class CreateUserService:
    """"
    Service that manages all the operations related with the creation of a user
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
        auth_repository: AuthRepository,
        nickname_repository: NicknameRepository,
        user_repository: UserRepository,
        leaderboard_repository: LeaderboardRepository
    ):
        self.auth_repository = auth_repository
        self.nickname_repository = nickname_repository
        self.user_repository = user_repository
        self.leaderboard_repository = leaderboard_repository


    def create(self, user: User) -> User:
        """
        Create a user with unique nickname, then in firebase auth, in firestore, and leaderboard entry.
        If any exception happens at any step there is a rollback, in a way to keep consistent data.
        """
        try:
            # Reserve a nickname in the nicknames collection to check univocity
            self.nickname_repository.reserve_nickname(user.nickname)
            # Create user in authentication
            user = self.auth_repository.create_user_auth(user)
            # Create user data in Firestore
            self.user_repository.create_user(user)
            # Create leaderboard entry
            self.leaderboard_repository.create_user_entry(user.uid, user.nickname)
            # Return new user
            return user
        except AuthenticateUserError as e:
            self._handle_auth_error(user)
            raise e
        except CreateUserError as e:
            self._handle_create_error(user)
            raise e


    def _handle_auth_error(self, user: User) -> None:
        """
        Rollback if auth repository had an error
        """
        self.firestore_repository.delete_nickname(user.nickname)


    def _handle_create_error(self, user: User) -> None:
        self.firestore_repository.delete_nickname(user.nickname)
        if hasattr(user, 'uid') and user.uid:
            self.auth_repository.delete_user_auth(user.uid)
            # Try to delete leaderboard entry if it was created
            self.leaderboard_repository.delete_user_entry(user.uid)