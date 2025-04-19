import os
import json
from typing import List, Optional
from pydantic_settings import BaseSettings

# Define root_dir relative to this file
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

class Settings(BaseSettings):
    # ✅ Application Settings
    APP_NAME: str
    APP_VERSION: str
    DOC_LOCATION_SAVE: str
    CONFIG_DIR: str
    DATABASE_URL: str
    HUGGINGFACE_TOKIENS: str
    DEFAULT_SYSTEM_PROMPT: str
    # ✅ File Processing Settings
    FILE_ALLOWED_TYPES: list

    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int
    CHUNKS_OVERLAP: int

    # ✅ Logging Settings
    LOG_LEVEL: str
    LOG_FILE_PATH: str

    # ✅ Monitoring Settings
    CPU_THRESHOLD: int
    MEMORY_THRESHOLD: int
    MONITOR_INTERVAL: int
    DISK_THRESHOLD: int

    # ✅ Alert Settings (Telegram Bot)
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str

    class Config:
        env_file = os.path.join(root_dir, ".env")
        env_file_encoding = "utf-8"

# Singleton-style getter (FastAPI friendly)
from functools import lru_cache

@lru_cache()
def get_settings() -> Settings:
    return Settings()
