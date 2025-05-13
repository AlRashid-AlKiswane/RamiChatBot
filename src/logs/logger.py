"""Logger module for centralized logging with alerting capabilities."""

import logging
import os
import sys
import traceback
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.logs.alerts import AlertManager  # Only used during type checking

# Setup project root
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(root_dir)

# Setup log directory and file
LOG_DIR = os.path.join(root_dir, "log")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Configure logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("RamiChatBot")


def log_info(message: str) -> None:
    """Logs informational messages."""
    logger.info(message)


def log_debug(message: str) -> None:
    """Logs debug messages."""
    logger.debug(message)


def log_error(message: str) -> None:
    """Logs error messages and sends alert via AlertManager."""
    tb = traceback.format_exc()
    full_message = f"{message}\nTraceback:\n{tb}" if "NoneType: None" not in tb else message
    logger.error(full_message)

    # Lazy import to prevent circular dependency
    from src.logs.alerts import AlertManager
    alert = AlertManager()
    alert.send_telegram_alert("Error Alert", full_message)


# Example usage
if __name__ == "__main__":
    log_info("Application started.")
    log_debug("This is a debug message.")
    log_error("This is a test error alert.")
