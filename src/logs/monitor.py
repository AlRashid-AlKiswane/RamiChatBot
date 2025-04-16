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

    def check_cpu_usage(self):
        """Check CPU usage and log alerts if needed."""
        try:
            cpu_stage = psutil.cpu_percent(interval=1)
            log_info(f"CPU Usage: {cpu_stage}%")
            if cpu_stage > self.cpu_threshold:
                log_debug(f"High CPU Usage: {cpu_stage}%")
                alert = AlertManager().send_telegram_alert("High CPU Usage", f"CPU Usage: {cpu_stage}%")
        except Exception as e:
            log_error(f"Error checking CPU usage: {str(e)}")

    def check_memory_usage(self):
        """Check Memory usage and log alerts if needed."""
        memory = psutil.virtual_memory()
        log_info(f"Memory Usage: {memory.percent}%")
        if memory.percent > self.memory_threshold:
            log_debug(f"High Memory Usage: {memory.percent}%")
            alert = AlertManager().send_telegram_alert("High Memory Usage", f"Memory Usage: {memory.percent}%")

    def check_disk_usage(self):
        """Check Disk usage and log alerts if needed."""
        disk = psutil.disk_usage('/')
        log_info(f"Disk Usage: {disk.percent}%")
        if disk.percent > self.disk_threshold:
            log_debug(f"High Disk Usage: {disk.percent}%")
            alert = AlertManager().send_telegram_alert("High Disk Usage", f"Disk Usage: {disk.percent}%")

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
