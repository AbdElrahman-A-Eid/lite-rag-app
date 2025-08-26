"""
Enumerations for document-related operations.
"""

from enum import Enum


class DocumentFileType(str, Enum):
    """Enumeration for document file types."""

    PDF = ".pdf"
    TXT = ".txt"
