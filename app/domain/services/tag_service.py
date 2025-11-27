from domain.entities.tag import Tag
from infrastructure.repositories.tags_repository import TagsRepository
from domain.services.user_service import UserService
from domain.services.leaderboard_service import LeaderboardService
from infrastructure.errors.tag_errors import AssignTagError


class TagService:
    """
    Service that manages all operations related to tags
    """

    def __init__(
        self,
        tags_repository: TagsRepository,
        user_service: UserService = None,
        leaderboard_service: LeaderboardService = None
    ):
        self.tags_repository = tags_repository
        self.user_service = user_service
        self.leaderboard_service = leaderboard_service

    def create_tag(self, tag: Tag, tag_id: str = None) -> Tag:
        """
        Creates a tag in database.
        """
        return self.tags_repository.create(tag, tag_id)

    def read_tag(self, tag_id: str) -> Tag:
        """
        Reads a tag from database.
        """
        return self.tags_repository.read(tag_id)

    def read_all_tags(self) -> list[Tag]:
        """
        Reads all tags from database.
        """
        return self.tags_repository.read_all()

    def update_tag(self, tag_id: str, tag_update: dict) -> Tag:
        """
        Updates a tag in database.
        """
        return self.tags_repository.update(tag_id, tag_update)

    def delete_tag(self, tag_id: str) -> None:
        """
        Deletes a tag from database.
        """
        self.tags_repository.delete(tag_id)

    def _assign_tag_to_user_internal(self, tag: Tag, uid: str) -> tuple[str, int]:
        """
        Internal method to assign a tag to a user.
        Handles the common logic of verifying, adding tag, and updating leaderboard.

        Args:
            tag: The Tag object to assign
            uid: User ID to assign the tag to

        Returns:
            tuple[str, int]: (tag_id, points)

        Raises:
            AssignTagError: if tag is already assigned or operation fails
        """
        tag_id = tag.tag_id

        if not tag_id:
            raise AssignTagError(
                message="Tag has no ID",
                http_status=500
            )

        # Get user's current tags
        user = self.user_service.read_user(uid)
        user_tag_ids = [t.tag_id for t in user.tags] if user.tags else []

        # Verify tag is not already assigned
        if tag_id in user_tag_ids:
            raise AssignTagError(
                message=f"Tag {tag_id} is already assigned to user",
                http_status=409
            )

        # Add tag to user's tags list
        updated_user = self.user_service.add_tags(uid, [tag_id])

        # Update leaderboard scores atomically
        if tag.points > 0:
            self.leaderboard_service.add_points(updated_user, tag.points)

        return tag.points

    def assign_tag_to_user(self, tag_id: str, uid: str) -> int:
        """
        Assigns a tag to a user by tag_id:
        1. Reading the tag from database
        2. Verifying the tag is not already assigned to the user
        3. Adding the tag to user's tags list
        4. Updating leaderboard scores (user and group)

        Raises:
            AssignTagError: if tag is already assigned or operation fails
        """
        # Read tag from database
        tag = self.tags_repository.read(tag_id)

        # Use internal method to handle assignment
        return self._assign_tag_to_user_internal(tag, uid)

    def assign_tag_by_secret(self, secret: str, uid: str) -> tuple[str, int]:
        """
        Assigns a tag to a user by secret:
        1. Reading all tags and finding the one with matching secret
        2. Verifying the tag is not already assigned to the user
        3. Adding the tag to user's tags list
        4. Updating leaderboard scores (user and group)

        Returns:
            tuple[str, int]: (tag_id, points)

        Raises:
            AssignTagError: if tag not found, already assigned, or operation fails
        """
        # Read all tags and find the one with matching secret
        all_tags = self.tags_repository.read_all()
        matching_tags = [tag for tag in all_tags if tag.secret == secret]

        if not matching_tags:
            raise AssignTagError(
                message="Tag not found with the provided secret",
                http_status=404
            )

        if len(matching_tags) > 1:
            raise AssignTagError(
                message="Multiple tags found with the same secret",
                http_status=400
            )

        tag = matching_tags[0]

        # Use internal method to handle assignment
        return self._assign_tag_to_user_internal(tag, uid)
