from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="app/.env")

    firebase_service_account_path: Optional[str] = None
    port: int = 8080
    debug: bool = False
    version: str = "1.0.0"
    sessionize_id: str


settings = Settings()
