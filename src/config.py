"""
Configuration settings for Lite-RAG-App
"""
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings definitions utilizing Pydantic
    """
    app_name: str
    app_version: str

    model_config = SettingsConfigDict(env_file=".env", env_prefix="RAG_")

settings = Settings() # type: ignore[call-arg]
