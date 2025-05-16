"""
Enum definitions for standard API response messages used across the system.
"""

from enum import Enum

class HelloResponse(Enum):
    """
    Enum for standardized API response messages.
    """

    APIRUN = "The APIs Work Successfully...."
    APIBREAK = "Something's wrong, check the logs file."
