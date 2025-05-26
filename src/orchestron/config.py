"""Config."""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import DATA_PATH


class Config(BaseSettings):
    """Configuration."""

    model_config = SettingsConfigDict(env_file=".env")

    db_url: str = f"sqlite:///{DATA_PATH.as_posix()}/dev.db"

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"


def get_config() -> Config:
    """Get config."""
    return Config()
