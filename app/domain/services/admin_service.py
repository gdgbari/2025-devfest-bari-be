from infrastructure.repositories.user_repository import UserRepository
from infrastructure.repositories.leaderboard_repository import LeaderboardRepository

class AdminService:
    """
    Service for administration tasks.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        leaderboard_repository: LeaderboardRepository
    ):
        self.user_repository = user_repository
        self.leaderboard_repository = leaderboard_repository

    def reset_all_data(self) -> None:
        """
        Resets all data:
        - Leaderboard scores (users and groups)
        - User tags
        - User quiz results
        - User quiz start times
        """
        # 1. Reset leaderboard scores
        self.leaderboard_repository.reset_all_scores()

        # 2. Get all users
        users = self.user_repository.read_all_raw()

        # 3. Iterate users and clear data
        for user in users:
            uid = user["uid"]
            
            # Clear tags
            self.user_repository.clear_tags(uid)
            
            # Clear quiz results
            self.user_repository.clear_quiz_results(uid)
            
            # Clear quiz start times
            self.user_repository.clear_quiz_start_times(uid)
