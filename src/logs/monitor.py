"""System resource monitoring module.

This module provides functionality to monitor CPU, memory, disk, and GPU usage,
sending alerts when thresholds are exceeded.
"""
import logging
import os
import sys
import time
from typing import Dict, Union
import psutil


try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    # Add to Python path only if it's not already there
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)
    from src.logs import log_error
    from src.helpers.settings import Settings, get_settings
    from src.logs.alerts import AlertManager
    from src.logs.logger import log_debug


except ModuleNotFoundError as e:
    logging.error("Module not found: %s", e, exc_info=True)
except ImportError as e:
    logging.error("Import error: %s", e, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise


class SystemMonitor:
    """Monitor system resources and send alerts when thresholds are exceeded.

    Attributes:
        cpu_threshold: CPU usage threshold percentage
        memory_threshold: Memory usage threshold percentage
        disk_threshold: Disk usage threshold percentage
        gpu_threshold: GPU usage threshold percentage
        gpu_available: Boolean indicating GPU availability
    """

    def __init__(self):
        """Initialize SystemMonitor with settings from configuration."""
        self.app_settings: Settings = get_settings()

        self.cpu_threshold = self.app_settings.CPU_THRESHOLD
        self.memory_threshold = self.app_settings.MEMORY_THRESHOLD
        self.disk_threshold = self.app_settings.DISK_THRESHOLD
        self.gpu_threshold = self.app_settings.GPUs_THRESHOLD
        self.gpu_available = self.app_settings.GPU_AVAILABLE

    def check_cpu_usage(self) -> Dict[str, Union[float, str]]:
        """Check CPU usage and log alerts if needed.

        Returns:
            Dictionary containing CPU usage percentage or error message
        """
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            if cpu_usage > self.cpu_threshold:
                log_debug(f"High CPU Usage: {cpu_usage}%")
                AlertManager().send_telegram_alert(
                    "High CPU Usage", 
                    f"CPU Usage: {cpu_usage}%"
                )
            return {"cpu_usage": cpu_usage}
        except psutil.Error as err:
            log_error(f"Error checking CPU usage: {str(err)}")
            return {"error": str(err)}

    def check_memory_usage(self) -> Dict[str, Union[float, str]]:
        """Check Memory usage and log alerts if needed.

        Returns:
            Dictionary containing memory usage percentage or error message
        """
        try:
            memory = psutil.virtual_memory()
            if memory.percent > self.memory_threshold:
                log_debug(f"High Memory Usage: {memory.percent}%")
                AlertManager().send_telegram_alert(
                    "High Memory Usage",
                    f"Memory Usage: {memory.percent}%"
                )
            return {"memory_usage": memory.percent}
        except psutil.Error as err:
            log_error(f"Error checking Memory usage: {str(err)}")
            return {"error": str(err)}

    def check_disk_usage(self) -> Dict[str, Union[float, str]]:
        """Check Disk usage and log alerts if needed.

        Returns:
            Dictionary containing disk usage percentage or error message
        """
        try:
            disk = psutil.disk_usage('/')
            if disk.percent > self.disk_threshold:
                log_debug(f"High Disk Usage: {disk.percent}%")
                AlertManager().send_telegram_alert(
                    "High Disk Usage",
                    f"Disk Usage: {disk.percent}%"
                )
            return {"disk_usage": disk.percent}
        except psutil.Error as err:
            log_error(f"Error checking Disk usage: {str(err)}")
            return {"error": str(err)}

    def check_gpu_usage(self) -> Dict[str, Union[float, str]]:
        """Check GPU usage and log alerts if needed.

        Returns:
            Dictionary containing GPU usage percentage or error message
        """
        if not self.gpu_available:
            return {"gpu_usage": "GPU monitoring unavailable"}

        try:
            from pynvml import (  # pylint: disable=import-outside-toplevel
                nvmlDeviceGetHandleByIndex, nvmlDeviceGetUtilizationRates,
                nvmlInit)
            nvmlInit()
            handle = nvmlDeviceGetHandleByIndex(0)
            util = nvmlDeviceGetUtilizationRates(handle)
            gpu = util.gpu
            if gpu > self.gpu_threshold:
                log_debug(f"High GPU Usage: {gpu}%")
                AlertManager().send_telegram_alert(
                    "High GPU Usage",
                    f"GPU: {gpu}%"
                )
            return {"gpu_usage": gpu}
        except ImportError:
            log_error("pynvml not installed")
            return {"error": "pynvml not installed"}
        except Exception as err:  # pylint: disable=broad-except
            log_error(f"GPU error: {str(err)}")
            return {"error": str(err)}

    def start_monitoring(self) -> None:
        """Start continuous monitoring of system resources."""
        while True:
            self.check_cpu_usage()
            self.check_memory_usage()
            self.check_disk_usage()
            if self.gpu_available:
                self.check_gpu_usage()
            time.sleep(self.app_settings.MONITOR_INTERVAL)


if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.start_monitoring()
