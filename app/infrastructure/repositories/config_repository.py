from domain.entities.config import Config
from infrastructure.clients.firestore_client import FirestoreClient
from infrastructure.errors.config_errors import ReadConfigError
from infrastructure.errors.firestore_errors import DocumentNotFoundError


class ConfigRepository:
    """
    Repository for managing application configuration in Firestore
    """

    CONFIG_COLLECTION: str = "remote_config"
    CONFIG_DOC_ID: str = "config"

    CHECK_IN_OPEN: str = "check_in_open"
    LEADERBOARD_OPEN: str = "leaderboard_open"
    INFO_TITLE: str = "info_title"
    INFO_CONTENT: str = "info_content"
    WINNER_ROOM: str = "winner_room"
    WINNER_TIME: str = "winner_time"

    def __init__(self, firestore_client: FirestoreClient):
        self.firestore_client = firestore_client

    def read_config(self) -> Config:
        """
        Read the application configuration from Firestore

        Returns:
            Config: The application configuration

        Raises:
            ReadConfigError: If reading the config fails
        """
        try:
            config_data = self.firestore_client.read_doc(
                collection_name=self.CONFIG_COLLECTION,
                doc_id=self.CONFIG_DOC_ID
            )

            return Config(
                check_in_open=config_data.get(self.CHECK_IN_OPEN, False),
                leaderboard_open=config_data.get(self.LEADERBOARD_OPEN, False),
                info_title=config_data.get(self.INFO_TITLE),
                info_content=config_data.get(self.INFO_CONTENT),
                winner_room=config_data.get(self.WINNER_ROOM),
                winner_time=config_data.get(self.WINNER_TIME)
            )
        except DocumentNotFoundError:
            raise ReadConfigError(message="Configuration not found", http_status=404)
        except Exception as e:
            raise ReadConfigError(message=f"Failed to read configuration", http_status=500)

