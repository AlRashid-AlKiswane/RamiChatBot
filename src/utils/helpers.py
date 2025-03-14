import os
from pydantic_settings import BaseSettings
from typing import List

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

class Settings(BaseSettings):
    # ✅ Application Settings
    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str

    # ✅ File Processing Settings
    FILE_ALLOWED_TYPES: List[str]  # Explicitly define list type
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int

    # ✅ Database Settings
    MONGODB_URL: str
    MONGODB_DATABASE: str

    # ✅ Logging Settings
    LOG_LEVEL: str
    LOG_FILE_PATH: str

    # ✅ Monitoring Settings
    CPU_THRESHOLD: int
    MEMORY_THRESHOLD: int
    MONITOR_INTERVAL: int  # Interval in seconds
    DISK_THRESHOLD: int

    # ✅ Alert Settings (Telgram Bot)

    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str

    class Config:
        env_file = os.path.join(root_dir, ".env")
        env_file_encoding = "utf-8"

def get_settings():
    return Settings()
