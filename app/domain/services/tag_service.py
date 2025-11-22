from domain.entities.tag import Tag
from infrastructure.repositories.tags_repository import TagsRepository


class TagService:
    """
    Service that manages all operations related to tags
    """

    def __init__(self, tags_repository: TagsRepository):
        self.tags_repository = tags_repository

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

