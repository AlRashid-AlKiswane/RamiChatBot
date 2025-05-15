"""
System Health Monitoring API Routes

Provides endpoints for monitoring system resources including:
- CPU usage
- Memory utilization
- Disk space
- GPU metrics (when available)
"""

import logging
import sys
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

# Setup import path and logging
try:
    from src.utils import setup_main_path
    MAIN_DIR = setup_main_path(levels_up=2)
    sys.path.append(MAIN_DIR)

    from src.logs import log_error, SystemMonitor

except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise

monitor_router = APIRouter()
monitor = SystemMonitor()

@monitor_router.get("/health/cpu", summary="Get current CPU utilization percentage")
def get_cpu_usage() -> float:
    """Retrieve current CPU usage percentage.
    
    Returns:
        float: Current CPU usage percentage (0-100)
        
    Raises:
        JSONResponse: 500 error if monitoring fails
    """
    try:
        if (usage := monitor.check_cpu_usage().get("cpu_usage")) is None:
            raise ValueError("CPU monitoring data unavailable")
        return usage
    except ValueError as e:
        log_error(f"CPU monitoring error: {e}")
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)}
        )
    except Exception as e:  # pylint: disable=broad-except
        log_error(f"Unexpected CPU monitoring error: {e}")
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "CPU monitoring service unavailable"}
        )

@monitor_router.get("/health/memory", summary="Get current memory utilization percentage")
def get_memory_usage() -> float:
    """Retrieve current memory usage percentage.
    
    Returns:
        float: Current memory usage percentage (0-100)
        
    Raises:
        JSONResponse: 500 error if monitoring fails
    """
    try:
        if (usage := monitor.check_memory_usage().get("memory_usage")) is None:
            raise ValueError("Memory monitoring data unavailable")
        return usage
    except ValueError as e:
        log_error(f"Memory monitoring error: {e}")
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)}
        )
    except Exception as e:  # pylint: disable=broad-except
        log_error(f"Unexpected memory monitoring error: {e}")
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Memory monitoring service unavailable"}
        )

@monitor_router.get("/health/disk", summary="Get current disk utilization percentage")
def get_disk_usage() -> float:
    """Retrieve current disk usage percentage.
    
    Returns:
        float: Current disk usage percentage (0-100)
        
    Raises:
        JSONResponse: 500 error if monitoring fails
    """
    try:
        if (usage := monitor.check_disk_usage().get("disk_usage")) is None:
            raise ValueError("Disk monitoring data unavailable")
        return usage
    except ValueError as e:
        log_error(f"Disk monitoring error: {e}")
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)}
        )
    except Exception as e:  # pylint: disable=broad-except
        log_error(f"Unexpected disk monitoring error: {e}")
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Disk monitoring service unavailable"}
        )

@monitor_router.get("/health/gpu", summary="Get current GPU utilization if available")
def get_gpu_usage():
    """Retrieve current GPU usage percentage if supported.
    
    Returns:
        Union[float, JSONResponse]: 
            - GPU usage percentage (0-100) if available
            - JSON response if unsupported
            
    Raises:
        JSONResponse: 500 error if monitoring fails
    """
    try:
        if (usage := monitor.check_gpu_usage().get("gpu_usage")) is None or isinstance(usage, str):
            raise NotImplementedError("GPU monitoring unavailable")
        return usage
    except NotImplementedError:
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={"message": "GPU monitoring not supported"}
        )
    except Exception as e:  # pylint: disable=broad-except
        log_error(f"GPU monitoring error: {e}")
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "GPU monitoring service unavailable"}
        )
