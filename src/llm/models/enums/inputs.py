"""
Input Types enums.
"""

from enum import Enum


class InputType(str, Enum):
    """Input types for LLM embedding requests."""

    DOCUMENT = "document"
    QUERY = "query"
