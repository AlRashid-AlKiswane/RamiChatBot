"""
This module provides functions for loading and parsing the most recent YAML file 
from the configuration directory.
"""

import logging
import os
import sys
from typing import Optional, Dict, Any
import yaml

try:
    # Setup import path
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    # Add to Python path only if it's not already there
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from src.logs import log_error, log_info, log_debug
    from src.helpers import get_settings
    from src.enums import YMLFileEnums
except ImportError as ie:
    logging.error("Import Error setup error: %s", ie, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise

DIRECTORY = get_settings().CONFIG_DIR

def load_last_yaml(file_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Load the content of the latest modified YAML file in the config directory,
    or a specific file if 'file_path' is provided.

    Args:
        file_path (Optional[str]): Specific path to YAML file.

    Returns:
        Optional[Dict[str, Any]]: Parsed YAML content as a dictionary or None if error.
    """
    try:
        if file_path:
            target_file = file_path
        else:
            yaml_files = [f for f in os.listdir(DIRECTORY) if f.endswith((".yaml", ".yml"))]

            if not yaml_files:
                log_debug(YMLFileEnums.NO_YAML_FILES_FOUND.value)
                return None

            # Sort files by last modified time
            yaml_files.sort(key=lambda f: os.path.getmtime(os.path.join(DIRECTORY, f)))
            target_file = os.path.join(DIRECTORY, yaml_files[-1])

        # Load the YAML content
        with open(target_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        log_info(f"{YMLFileEnums.YAML_LOAD_SUCCESS.value}: {target_file}")
        return data

    except (FileNotFoundError, yaml.YAMLError) as e:
        log_error(f"{YMLFileEnums.YAML_LOAD_ERROR.value}: {e}")
        return None
