"""
Configuration settings for Lite-RAG-App
"""

import logging
from pathlib import Path
from typing import Optional, List
from logging.handlers import RotatingFileHandler
from pydantic import Field, AnyUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from models.enums import LogLevel
from llm.models.enums import LLMProvider


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
    files_supported_types: List[str]
    files_max_size_mb: int = Field(ge=0, default=20)
    files_default_chunk_size_kb: int = Field(ge=0, default=512)

    mongo_uri: AnyUrl
    mongo_db_name: str

    generation_backend: str
    embedding_backend: str

    generation_model_id: str
    embedding_model_id: str
    embedding_dimensions: int = Field(ge=1)

    generation_default_max_tokens: int = Field(ge=1, default=1024)
    generation_default_temperature: float = Field(ge=0.0, le=2.0, default=0.15)
    default_input_max_characters: int = Field(ge=1, default=3000)

    openai_api_key: str
    openai_api_base_url: Optional[str] = Field(default=None)

    cohere_api_key: str
    cohere_api_base_url: Optional[str] = Field(default=None)

    model_config = SettingsConfigDict(env_file=".env", env_prefix="RAG_")

    @field_validator("generation_backend", "embedding_backend")
    def validate_llm_provider(self, v):
        """Validate LLM provider.

        Args:
            v (str): The LLM provider to validate.

        Raises:
            ValueError: If the LLM provider is not supported.

        Returns:
            str: The validated LLM provider.
        """
        if v not in LLMProvider.__members__:
            raise ValueError(f"Invalid LLM provider: {v}")
        return v


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
