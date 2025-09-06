"""
Base classes for all LLM providers.
"""

import logging
from typing import Optional, List, Dict
from abc import ABC, abstractmethod


class LLMProviderInterface(ABC):
    """
    Interface for all LLM provider classes to implement.
    """

    @abstractmethod
    def set_embedding_model(self, model_id: str, embedding_size: int):
        """Set the embedding model to use for generating embeddings.

        Args:
            model_id (str): The ID of the model to use.
            embedding_size (int): The size of the embeddings to generate.
        """

    @abstractmethod
    def embed(
        self, text: str | List[str], input_type: Optional[str] = None
    ) -> List[float] | List[List[float]]:
        """
        Generate embeddings for the given text.

        Args:
            text (str | List[str]): The text or list of texts to generate embeddings for.
            input_type (Optional[str]): The type of input (e.g., "text", "image").

        Returns:
            List[float] | List[List[float]]: The generated embeddings.
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
    def set_generation_model(self, model_id: str):
        """Set the generation model to use for responses.

        Args:
            model_id (str): The ID of the model to use.
        """

    @abstractmethod
    def generate(
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

    def set_generation_model(self, model_id: str):
        """Set the generation model to use for responses.

        Args:
            model_id (str): The ID of the model to use.
        """
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        """Set the embedding model to use for generating embeddings.

        Args:
            model_id (str): The ID of the model to use.
            embedding_size (int): The size of the embeddings to generate.
        """
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
