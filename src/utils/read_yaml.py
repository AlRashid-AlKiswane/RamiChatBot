import os
import sys
import yaml
from typing import Optional, Dict, Any
from pathlib import Path

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_error, log_info, log_debug
    from config import Settings, get_settings
    from enums import YMLFileEnums
except Exception as e:
    raise ImportError(f"[IMPORT ERROR] {__file__}: {e}")

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
    

    except Exception as e:
        log_error(f"{YMLFileEnums.YAML_LOAD_ERROR.value}: {e}")
        return None
