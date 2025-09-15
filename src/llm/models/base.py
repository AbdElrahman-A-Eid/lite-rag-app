"""
Base classes for all LLM providers.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from llm.models.enums.inputs import InputType


class LLMProviderInterface(ABC):
    """
    Interface for all LLM provider classes to implement.
    """

    @abstractmethod
    async def set_embedding_model(self, model_id: str, embedding_size: Optional[int]):
        """Set the embedding model to use for generating embeddings.

        Args:
            model_id (str): The ID of the model to use.
            embedding_size (Optional[int]): The size of the embeddings to generate. \
                If None, use model default.
        """

    @property
    @abstractmethod
    def embedding_size_(self) -> int:
        """Get the configured embedding size.

        Returns:
            int: The embedding size.
        """

    @property
    @abstractmethod
    async def models_(self) -> List[str]:
        """
        List available models from the API.

        Returns:
            List[str]: A list of available model IDs if successful, an empty list otherwise.
        """

    @abstractmethod
    async def embed(
        self, texts: List[str], input_type: Optional[InputType] = None
    ) -> List[List[float]]:
        """
        Generate embeddings for the given text.

        Args:
            texts (List[str]): The text or list of texts to generate embeddings for.
            input_type (Optional[InputType]): The type of input (e.g., "document", "query").

        Returns:
            List[List[float]]: The generated embeddings.
        """

    @abstractmethod
    def construct_prompt(self, prompt: str, role: str) -> Dict[str, str]:
        """
        Construct the prompt for the LLM based on the user input and role.

        Args:
            prompt (str): The user input prompt.
            role (str): The role of the user (e.g., "user", "system").

        Returns:
            Dict[str, str]: The constructed prompt.
        """

    @abstractmethod
    async def set_generation_model(self, model_id: str):
        """Set the generation model to use for responses.

        Args:
            model_id (str): The ID of the model to use.
        """

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> Optional[str]:
        """
        Generate a response from the LLM based on the provided prompt.

        Args:
            prompt (str): The prompt to generate a response for.
            chat_history (List[Dict[str,str]]): The chat history to include in the response.
            max_tokens (int): The maximum number of tokens to generate. \
                Optional (the global default is used if None).
            temperature (float): The temperature to use for sampling. \
                Optional (the global default is used if None).

        Returns:
            Optional[str]: The generated response if available.
        """


class BaseLLMProvider(LLMProviderInterface):
    """
    Base class for all LLM providers.
    """

    def __init__(
        self,
        max_input_characters: int = 3000,
        default_max_output_tokens: int = 1024,
        default_temperature: float = 0.15,
    ):
        self.api_key: Optional[str] = None
        self.base_url: Optional[str] = None

        self.max_input_characters = max_input_characters
        self.default_max_output_tokens = default_max_output_tokens
        self.default_temperature = default_temperature

        self.embedding_model_id: Optional[str] = None
        self.embedding_size: Optional[int] = None

        self.generation_model_id: Optional[str] = None

        self.logger = logging.getLogger(self.__class__.__name__)

    async def set_generation_model(self, model_id: str):
        """Set the generation model to use for responses.

        Args:
            model_id (str): The ID of the model to use.
        """
        available_models = await self.models_
        if available_models is None or (model_id not in available_models):
            self.logger.error(
                "Model ID %s is not available. Available models: %s",
                model_id,
                available_models,
            )
            return
        self.generation_model_id = model_id

    async def set_embedding_model(self, model_id: str, embedding_size: Optional[int]):
        """Set the embedding model to use for generating embeddings.

        Args:
            model_id (str): The ID of the model to use.
            embedding_size (Optional[int]): The size of the embeddings to generate. \
                If None, use model default.
        """
        available_models = await self.models_
        if available_models is None or model_id not in available_models:
            self.logger.error(
                "Model ID %s is not available. Available models: %s",
                model_id,
                available_models,
            )
            return
        self.embedding_model_id = model_id
        if embedding_size is None:
            self.logger.info(
                "Embedding size not provided. Using model default for %s.", model_id
            )
            self.embedding_size = len(
                (await self.embed(texts=["test"], input_type=InputType.DOCUMENT))[0]
            )
            self.logger.info(
                "Inferred embedding size for model %s is %d.",
                model_id,
                self.embedding_size,
            )
        else:
            self.embedding_size = embedding_size

    @property
    def embedding_size_(self) -> int:
        """Get the configured embedding size.

        Returns:
            int: The embedding size.
        """
        if self.embedding_size is None:
            raise ValueError("Embedding model is not set.")
        return self.embedding_size
