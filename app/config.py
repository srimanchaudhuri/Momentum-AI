"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation and environment variable loading."""

    DB_URL: str
    DB_NAME: str = "momentum_db"
    APP_NAME: str = "Momentum AI"
    DEBUG: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
