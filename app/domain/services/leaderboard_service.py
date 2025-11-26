from infrastructure.repositories.leaderboard_repository import LeaderboardRepository
from domain.entities.user import User

class LeaderboardService:

    def __init__(
        self,
        leaderboard_repository: LeaderboardRepository
    ):
        self.leaderboard_repository = leaderboard_repository


    def add_points(self, user: User, score: int) -> None:
        """
        Updates leaderboard scores for user and group atomically.

        Args:
            user (User): The user to add points to
            score (int): The points to add
        """
        self.leaderboard_repository.increment_user_score(user.uid, score)

        if user.group and user.group.get("gid"):
            group_id = user.group.get("gid")
            self.leaderboard_repository.increment_group_score(group_id, score)
