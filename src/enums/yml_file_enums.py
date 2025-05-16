"""
Enum definitions related to YAML file handling and loading statuses.
"""

from enum import Enum


class YMLFileEnums(Enum):
    """
    Enum for standardized messages related to YAML file operations.
    """

    NO_YAML_FILES_FOUND = (
        "No YAML files found. Please enter your configuration models via the llms_config route."
    )
    YAML_LOAD_SUCCESS = "Loaded YAML successfully."
    YAML_LOAD_ERROR = "Error loading YAML."
