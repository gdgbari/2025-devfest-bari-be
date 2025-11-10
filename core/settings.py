from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    firebase_service_account_path: str = "/app/secrets/service_account_key.json"
    version: str = "1.0.0"
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
