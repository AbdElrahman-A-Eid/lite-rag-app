"""
Common base models for the application.
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


class ResponseSignals(str, Enum):
    """Enumeration for response signals."""

    FILE_UPLOAD_FAILED = "File Upload Failed"
    NO_FILE_PROVIDED = "No File Provided"
    UNSUPPORTED_FILE_TYPE = "Unsupported File Type"
    FILE_TOO_LARGE = "File Too Large"
    FILE_VALIDATION_ERROR = "File Validation Error"
