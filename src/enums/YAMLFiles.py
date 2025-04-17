from enum import Enum


class YMLFileEnums(Enum):
    NO_YAML_FILES_FOUND = "No YAML fiels found. Please Enter your configration mdoels by llms_config route"
    YAML_LOAD_SUCCESS = "Load YAML sucessfully."
    YAML_LOAD_ERROR = "Error loading YAML."