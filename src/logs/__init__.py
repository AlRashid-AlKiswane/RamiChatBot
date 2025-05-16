"""
logs package

This package provides logging, alerting, and system monitoring utilities
for the application.

Modules:
- alerts: Defines the `AlertManager` class used for sending system alerts.
- logger: Contains logging utility functions including `log_info`, `log_error`,
  `log_debug`, and `log_warning` for consistent logging across the project.
- monitor: Provides the `SystemMonitor` class for tracking system resource usage,
  performance metrics, or operational health.

Usage:
Import this package to initialize logging, send alerts, or perform health checks.

Example:
    from logs import log_info, AlertManager, SystemMonitor
    log_info("System started.")
    monitor = SystemMonitor()
    alert = AlertManager()
"""

from .alerts import AlertManager
from .logger import log_error, log_info, log_debug, log_warning
from .monitor import SystemMonitor
