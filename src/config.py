"""
Configuration settings for Lite-RAG-App
"""

import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from pydantic import Field, AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from models.enums import LogLevel


class Settings(BaseSettings):
    """
    Application settings definitions utilizing Pydantic
    """

    app_name: str
    app_version: str

    log_dir: Path
    log_file_level: LogLevel
    log_console_level: LogLevel

    files_dir: Path
    files_supported_types: list[str]
    files_max_size_mb: int = Field(ge=0, default=20)
    files_default_chunk_size_kb: int = Field(ge=0, default=512)

    mongo_uri: AnyUrl
    mongo_db_name: str

    model_config = SettingsConfigDict(env_file=".env", env_prefix="RAG_")


settings = Settings()  # type: ignore[call-arg]


def setup_logging():
    """Configures Application logging."""
    log_folder = settings.log_dir
    log_folder.mkdir(parents=True, exist_ok=True)
    log_file_path = log_folder / "app.log"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=5 * 1024 * 1024, backupCount=5
    )
    file_handler.setLevel(settings.log_file_level.to_logging_level())

    console_handler = logging.StreamHandler()
    console_handler.setLevel(settings.log_console_level.to_logging_level())

    formatter = logging.Formatter(
        "%(asctime)s - %(name)-15s - %(levelname)-8s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


setup_logging()
