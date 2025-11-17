from domain.entities.config import Config
from infrastructure.repositories.config_repository import ConfigRepository


class ConfigService:
    """
    Service for managing application configuration
    """

    def __init__(self, config_repository: ConfigRepository):
        self.config_repository = config_repository

    def is_check_in_open(self) -> bool:
        """
        Check if check-in is currently open

        Returns:
            bool: True if check-in is open, False otherwise
        """
        config = self.config_repository.read_config()
        return config.check_in_open

