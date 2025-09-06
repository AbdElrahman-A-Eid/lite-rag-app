"""
Vector DB provider enums.
"""

from enum import Enum


class VectorDBProvider(str, Enum):
    """Supported Vector DB providers."""

    QDRANT = "QDRANT"
