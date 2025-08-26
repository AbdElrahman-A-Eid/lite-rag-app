"""
Enumerations for log levels.
"""

import logging
from enum import Enum


class LogLevel(str, Enum):
    """Enumeration for log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"
    NOTSET = "NOTSET"

    def to_logging_level(self) -> int:
        """Converts a LogLevel to its corresponding logging level.

        Returns:
            int: The corresponding logging level.
        """
        return {
            self.DEBUG: logging.DEBUG,
            self.INFO: logging.INFO,
            self.WARN: logging.WARN,
            self.WARNING: logging.WARNING,
            self.ERROR: logging.ERROR,
            self.CRITICAL: logging.CRITICAL,
            self.FATAL: logging.FATAL,
            self.NOTSET: logging.NOTSET,
        }.get(self, logging.NOTSET)
