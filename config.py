import os
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings - like Spring Boot's application.properties
    Uses Pydantic Settings for type-safe configuration management
    """

    # Environment
    debug: bool = Field(default=False, description="Enable debug mode")
    environment: str = Field(default="production", description="Environment name (dev, staging, production)")

    # Server configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8888, description="Server port")
    nthreads: int = Field(default_factory=lambda: os.cpu_count() or 1, description="Number of worker threads")

    # Application metadata
    version: str = Field(default="0.0.1", description="API version")
    title: str = Field(default="Devfest Bari Backend", description="API title")

    # Firebase configuration
    firebase_credentials_path: str = Field(
        default="./secrets/firebase-keys.json",
        description="Path to Firebase credentials JSON file"
    )

    # CORS configuration
    cors_origins: list[str] = Field(
        default=["*"],
        description="Allowed CORS origins (comma-separated in .env)"
    )

    class Config:
        # Automatically reads from .env file
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Allow parsing complex types from environment variables
        env_nested_delimiter = "__"
        # Parse JSON strings for lists
        json_loads = lambda v: v if isinstance(v, list) else [v]


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance (Singleton pattern)
    The @lru_cache decorator ensures only one instance is created
    """
    return Settings()


# Export for backwards compatibility
settings = get_settings()
DEBUG = settings.debug
VERSION = settings.version
NTHREADS = settings.nthreads

