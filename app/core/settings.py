from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    firebase_service_account_path: Optional[str] = None
    port: int = 8080
    debug: bool = False
    version: str = "1.0.0"
    sessionize_id: str

    class Config:
        env_file = "app/.env"


settings = Settings()
