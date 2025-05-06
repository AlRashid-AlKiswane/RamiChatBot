from enum import Enum


class LLMsStatus(Enum):
    """
    Represents the status of retrieving LLM configuration.
    """
    SUCCESS = "Configuration retrieved successfully"
    ERROR = "Failed to retrieve configuration"
    NOT_FOUND = "Configuration not found"
    INVALID_FORMAT = "Configuration format is invalid"
