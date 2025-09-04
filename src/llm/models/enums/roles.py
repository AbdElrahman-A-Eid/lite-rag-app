"""
Message role enums.
"""

from enum import Enum


class MessageRole(str, Enum):
    """Message roles for LLM conversations."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
