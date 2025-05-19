"""
Configuration settings for the application using environment variables.

This module defines all application settings using Pydantic's BaseSettings,
which automatically reads from environment variables or a .env file.
"""

from functools import lru_cache
import logging
import os
import sys
from pydantic_settings import BaseSettings



try:
    # Setup project root
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)
except ModuleNotFoundError as e:
    logging.error("Module not found: %s", e, exc_info=True)
except ImportError as e:
    logging.error("Import error: %s", e, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise

class Settings(BaseSettings):
    """Application settings configuration using environment variables.

    Attributes:
        APP_NAME: Name of the application
        APP_VERSION: Version of the application
        DOC_LOCATION_SAVE: Directory to save documents
        CONFIG_DIR: Configuration directory path
        DATABASE_URL: Database connection URL
        EMBEDDING_MODEL: Name of the embedding model
        HUGGINGFACE_TOKIENS: HuggingFace API tokens
        DEFAULT_SYSTEM_PROMPT: Default system prompt for the application
        ENABLE_MEMORY: Flag to enable memory features
        FILE_ALLOWED_TYPES: List of allowed file types
        FILE_MAX_SIZE: Maximum file size allowed
        FILE_DEFAULT_CHUNK_SIZE: Default chunk size for file processing
        CHUNKS_OVERLAP: Overlap between chunks
        GPU_AVAILABLE: Flag indicating GPU availability
        LOG_LEVEL: Logging level
        CPU_THRESHOLD: CPU usage threshold for monitoring
        MEMORY_THRESHOLD: Memory usage threshold for monitoring
        MONITOR_INTERVAL: Monitoring interval in seconds
        DISK_THRESHOLD: Disk usage threshold for monitoring
        GPUs_THRESHOLD: GPU usage threshold for monitoring
        TELEGRAM_BOT_TOKEN: Telegram bot token for alerts
        TELEGRAM_CHAT_ID: Telegram chat ID for alerts
    """

    # Application Settings
    APP_NAME: str
    APP_VERSION: str
    SECRET_KEY: str

    DOC_LOCATION_SAVE: str
    CONFIG_DIR: str
    DATABASE_URL: str
    EMBEDDING_MODEL: str

    HUGGINGFACE_TOKIENS: str
    DEFAULT_SYSTEM_PROMPT: str
    ENABLE_MEMORY: bool

    # File Processing Settings
    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int
    CHUNKS_OVERLAP: int

    GPU_AVAILABLE: bool

    # Logging Settings
    LOG_LEVEL: str

    # Monitoring Settings
    CPU_THRESHOLD: int
    MEMORY_THRESHOLD: int
    MONITOR_INTERVAL: int
    DISK_THRESHOLD: int
    GPUs_THRESHOLD: int

    # Alert Settings (Telegram Bot)
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str

    # pylint: disable=too-few-public-methods
    class Config:
        """Pydantic configuration for settings."""
        env_file = os.path.join(MAIN_DIR, ".env")
        env_file_encoding = "utf-8"

        def __str__(self) -> str:
            return "Pydantic configuration settings"


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings.

    Returns:
        Settings: The application settings instance
    """
    return Settings()


if __name__ == "__main__":
    app_setting: Settings = get_settings()
    print(app_setting.DATABASE_URL)
