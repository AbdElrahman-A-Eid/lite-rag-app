"""
Enumerations for response signals.
"""

from enum import Enum


class ResponseSignals(str, Enum):
    """Enumeration for response signals."""

    FILE_UPLOAD_FAILED = "File Upload Failed"
    NO_FILE_PROVIDED = "No File Provided"
    UNSUPPORTED_FILE_TYPE = "Unsupported File Type"
    FILE_TOO_LARGE = "File Too Large"
    FILE_VALIDATION_ERROR = "File Validation Error"
    DOCUMENT_PROCESSING_FAILED = "Document Processing Failed"
