"""
LLM provider enums.
"""

from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "OPENAI"
    COHERE = "COHERE"
