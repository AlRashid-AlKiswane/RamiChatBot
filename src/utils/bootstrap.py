"""Utility functions for path setup and safe module imports.

This module provides helper functions for:
- Setting up Python path to include parent directories
- Safely importing modules with proper error handling
"""

import os
import sys
import logging
from typing import Optional

from fsspec import Callback

def setup_main_path(levels_up: int = 1) -> str:
    """Add the specified number of parent directories to Python path.
    
    Args:
        levels_up: Number of parent directory levels to go up (default: 1)
        
    Returns:
        str: Absolute path to the main directory that was added
    """
    main_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * levels_up))
    sys.path.append(main_dir)
    return main_dir

def safe_import(module_path: str, alias: Optional[str] = None):
    try:
        module = __import__(module_path, fromlist=["*"])
        if alias:
            globals()[alias] = module
        return module
    except ModuleNotFoundError as e:
        logging.error("Module not found: %s", e, exc_info=True)
    except ImportError as e:
        logging.error("Import error: %s", e, exc_info=True)
    except Exception as e:
        logging.critical("Unexpected setup error: %s", e, exc_info=True)
        raise
    return Callback