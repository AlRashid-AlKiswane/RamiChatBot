import time, os, sys, psutil

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(root_dir)

from logs import log_error, log_info, log_debug
from config.setting import get_settings, Settings
from logs import AlertManager


class SystemMonitor:
    def __init__(self):
        self.app_settings: Settings = get_settings()

        self.cpu_threshold = self.app_settings.CPU_THRESHOLD
        self.memory_threshold = self.app_settings.MEMORY_THRESHOLD
        self.disk_threshold = self.app_settings.DISK_THRESHOLD
        self.gpu_threshold = self.app_settings.GPUs_THRESHOLD
        self.GPU_AVAILABLE = self.app_settings.GPU_AVAILABLE

    def check_cpu_usage(self):
        """Check CPU usage and log alerts if needed."""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            log_info(f"CPU Usage: {cpu_usage}%")
            if cpu_usage > self.cpu_threshold:
                log_debug(f"High CPU Usage: {cpu_usage}%")
                AlertManager().send_telegram_alert("High CPU Usage", f"CPU Usage: {cpu_usage}%")
            return {"cpu_usage": cpu_usage}
        except Exception as e:
            log_error(f"Error checking CPU usage: {str(e)}")
            return {"error": str(e)}

    def check_memory_usage(self):
        """Check Memory usage and log alerts if needed."""
        try:
            memory = psutil.virtual_memory()
            log_info(f"Memory Usage: {memory.percent}%")
            if memory.percent > self.memory_threshold:
                log_debug(f"High Memory Usage: {memory.percent}%")
                AlertManager().send_telegram_alert("High Memory Usage", f"Memory Usage: {memory.percent}%")
            return {"memory_usage": memory.percent}
        except Exception as e:
            log_error(f"Error checking Memory usage: {str(e)}")
            return {"error": str(e)}

    def check_disk_usage(self):
        """Check Disk usage and log alerts if needed."""
        try:
            disk = psutil.disk_usage('/')
            log_info(f"Disk Usage: {disk.percent}%")
            if disk.percent > self.disk_threshold:
                log_debug(f"High Disk Usage: {disk.percent}%")
                AlertManager().send_telegram_alert("High Disk Usage", f"Disk Usage: {disk.percent}%")
            return {"disk_usage": disk.percent}
        except Exception as e:
            log_error(f"Error checking Disk usage: {str(e)}")
            return {"error": str(e)}

    def check_gpu_usage(self):
        """Check GPU usage and log alerts if needed."""
        try:
            if not self.GPU_AVAILABLE:
                return {"gpu_usage": "GPU monitoring unavailable"}
            try:
                from pynvml import (
                    nvmlInit,
                    nvmlDeviceGetHandleByIndex,
                    nvmlDeviceGetUtilizationRates
                )
                nvmlInit()
            except ImportError as e:
                log_error("pynvml not installed")
                return {"error": "pynvml not installed"}

            handle = nvmlDeviceGetHandleByIndex(0)
            util = nvmlDeviceGetUtilizationRates(handle)
            gpu = util.gpu
            log_info(f"GPU Usage: {gpu}%")
            if gpu > self.gpu_threshold:
                log_debug(f"High GPU Usage: {gpu}%")
                AlertManager().send_telegram_alert("High GPU Usage", f"GPU: {gpu}%")
            return {"gpu_usage": gpu}
        except Exception as e:
            log_error(f"GPU error: {str(e)}")
            return {"error": str(e)}

    def start_monitoring(self):
        """Start monitoring system resources."""
        while True:
            self.check_cpu_usage()
            self.check_memory_usage()
            self.check_disk_usage()
            time.sleep(self.app_settings.MONITOR_INTERVAL)


# Example usage
if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.start_monitoring()