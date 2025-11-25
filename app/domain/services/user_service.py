from typing import List, Optional
from domain.entities.user import User
from domain.entities.tag import Tag
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.repositories.tags_repository import TagsRepository
from domain.services.group_service import GroupService

class UserService:
    """"
    Service that manages all the operations related with a user
    """


    def __init__(
        self,
        user_repository: UserRepository,
        group_service: GroupService,
        tags_repository: TagsRepository
    ):
        self.user_repository = user_repository
        self.group_service = group_service
        self.tags_repository = tags_repository


    def create_user(self, user: User) -> User:
        """
        Creates a user in database.
        """
        return self.user_repository.create(user)


    def read_user(self, uid: str) -> User:
        """
        Reads a user from database and loads associated tags.
        """
        user_data = self.user_repository.read_raw(uid)
        tags = self._load_user_tags(user_data.get("tags"))
        return User.from_dict(user_data, tags=tags)


    def read_all_users(self) -> list[User]:
        """
        Reads all users in database and loads associated tags.
        """
        users_data = self.user_repository.read_all_raw()
        users = []
        for user_data in users_data:
            tags = self._load_user_tags(user_data.get("tags"))
            users.append(User.from_dict(user_data, tags=tags))
        return users


    def update_user(self, uid: str, user_update: dict) -> User:
        """
        Recover a user from uid in database and the updates it.
        """
        current_user: User = self.read_user(uid)
        return self.user_repository.update(user_update=user_update, current_user=current_user)


    def delete_user(self, uid: str) -> None:
        """
        Deletes a user from the database.
        """
        user = self.read_user(uid)

        # Decrement group counter if user has a group assigned
        if user.group:
            group_id = user.group.get("gid")
            if group_id:
                self.group_service.decrement_user_count(group_id)

        self.user_repository.delete(uid, user.nickname)


    def assign_group_to_user(self, uid: str, gid: str) -> User:
        """
        Assigns a specific group to a user.
        """
        self.user_repository.assign_group(uid, gid)
        return self.read_user(uid)

    def _load_user_tags(self, tag_ids: Optional[List[str]]) -> Optional[List[Tag]]:
        """
        Loads Tag objects from tags collection using tag_ids.
        If a tag doesn't exist, it's ignored.

        Args:
            tag_ids: List of tag documentIds (e.g., ["session_1", "session_2"])

        Returns:
            List of Tag objects, or None if no tags
        """
        if not tag_ids:
            return None

        tags = []
        for tag_id in tag_ids:
            try:
                tag = self.tags_repository.read(tag_id)
                tags.append(tag)
            except Exception:
                # If tag doesn't exist, skip it
                continue

        return tags if tags else None
