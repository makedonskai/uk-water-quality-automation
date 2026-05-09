"""Centralised configuration. Read from environment variables with sane defaults."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ea_api_base_url: str = "https://environment.data.gov.uk/flood-monitoring"
    ea_api_timeout_seconds: float = 10.0
    ea_api_max_retries: int = 3
    database_url: str = "sqlite:///./water.db"
    log_level: str = "INFO"


settings = Settings()
