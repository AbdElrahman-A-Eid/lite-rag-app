"""
Enumeration of MongoDB collection names.
"""

from enum import Enum


class CollectionNames(str, Enum):
    """Enumeration of MongoDB collection names."""

    PROJECTS = "projects"
    CHUNKS = "chunks"
