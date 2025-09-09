"""
Factory class for creating LLM Provider instances.
"""

import logging
from typing import Optional
from config import Settings
from llm.models.base import LLMProviderInterface
from llm.models.enums.providers import LLMProvider
from llm.providers.cohere_provider import CohereProvider
from llm.providers.openai_provider import OpenAIProvider


class LLMProviderFactory:
    """
    Factory class for creating LLM Provider instances.
    """

    def __init__(self, config: Settings):
        self.settings = config
        self.api_key: str
        self.base_url: Optional[str] = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def create(self, provider_type: str, **kwargs) -> Optional[LLMProviderInterface]:
        """
        Create a new LLM Provider instance.

        Args:
            provider_type (LLMProvider): The type of LLM Provider to create.
            **kwargs: Additional arguments to pass to the provider's constructor.

        Returns:
            LLMProviderInterface: The created LLM Provider instance.
        """
        if provider_type.upper() == LLMProvider.OPENAI.value:
            self.api_key = self.settings.openai_api_key
            self.base_url = self.settings.openai_api_base_url
            openai_provider = OpenAIProvider(
                api_key=self.api_key,
                base_url=self.base_url,
                max_input_characters=self.settings.default_input_max_characters,
                default_max_output_tokens=self.settings.generation_default_max_tokens,
                default_temperature=self.settings.generation_default_temperature,
                **kwargs,
            )
            return openai_provider
        elif provider_type.upper() == LLMProvider.COHERE.value:
            self.api_key = self.settings.cohere_api_key
            self.base_url = self.settings.cohere_api_base_url
            cohere_provider = CohereProvider(
                api_key=self.api_key,
                base_url=self.base_url,
                max_input_characters=self.settings.default_input_max_characters,
                default_max_output_tokens=self.settings.generation_default_max_tokens,
                default_temperature=self.settings.generation_default_temperature,
                **kwargs,
            )
            return cohere_provider
        self.logger.error("Unsupported LLM provider type: %s", provider_type)
        return None
