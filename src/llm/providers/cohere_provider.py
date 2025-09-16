"""
Concrete implementation of the Cohere LLM provider.
"""

from enum import Enum
from typing import Dict, List, Optional

from cohere import AsyncClientV2

from llm.models.base import BaseLLMProvider
from llm.models.enums.inputs import InputType

INPUT_TYPES_MAPPING = {
    InputType.DOCUMENT: "search_document",
    InputType.QUERY: "search_query",
}


class CohereMessageRoles(str, Enum):
    """Message roles specific to Cohere."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class CohereProvider(BaseLLMProvider):
    """
    Concrete implementation of the Cohere LLM provider.
    """

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        max_input_characters: int = 3000,
        default_max_output_tokens: int = 1024,
        default_temperature: float = 0.15,
        **kwargs,
    ):
        super().__init__(
            max_input_characters,
            default_max_output_tokens,
            default_temperature,
        )
        self.api_key = api_key
        self.base_url = base_url if base_url else None
        self.client = AsyncClientV2(
            api_key=self.api_key, base_url=self.base_url, **kwargs
        )
        self.enums = CohereMessageRoles
        self.available_models: List[str] = []

    @property
    async def models_(self) -> List[str]:
        """
        List available models from the API.

        Returns:
            List[str]: A list of available model IDs if successful, an empty list otherwise.
        """
        if self.client is None:
            self.logger.error("Cohere client is not initialized.")
        elif not self.available_models:
            self.logger.info("Fetching available models from Cohere...")
            try:
                response = await self.client.models.list(page_size=1000)
                if response.models is None:
                    self.logger.error("No models returned from Cohere.")
                else:
                    model_ids = [
                        model.name
                        for model in response.models
                        if model.name and not model.is_deprecated
                    ]
                    self.available_models = model_ids
            except Exception as e:
                self.logger.error(
                    "Error listing models from Cohere: %s", str(e), exc_info=True
                )
        self.logger.info("Available models: %s", self.available_models)
        return self.available_models

    def process_text(self, text: str) -> str:
        """
        Process the input text for the LLM.

        Args:
            text (str): The text to process.

        Returns:
           str: The processed text.
        """
        if len(text) > self.max_input_characters:
            self.logger.warning(
                "Input exceeds max character limit (%d/%d); truncating...",
                len(text),
                self.max_input_characters,
            )
            text = text[: self.max_input_characters]
        return text.strip()

    def construct_prompt(self, prompt: str, role: str) -> Dict[str, str]:
        """
        Construct the prompt for the LLM based on the user input and role.

        Args:
            prompt (str): The user input prompt.
            role (str): The role of the user (e.g., "user", "system").

        Returns:
            Dict[str, str]: The constructed prompt.
        """
        if role not in (e.value for e in self.enums):
            self.logger.error(
                "Invalid role: %s. Must be one of %s.",
                role,
                [e.value for e in self.enums],
            )
            role = self.enums.USER.value
        return {"role": role, "content": self.process_text(prompt)}

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
        if self.client is None:
            self.logger.error("OpenAI client is not initialized.")
            return []
        if self.embedding_model_id is None or self.embedding_size is None:
            self.logger.error("Embedding model ID or size is not set.")
            return []
        if input_type is None:
            self.logger.error("Input type is not set.")
            return []
        if input_type.value not in INPUT_TYPES_MAPPING:
            self.logger.error(
                "Invalid input type: %s. Must be one of %s.",
                input_type,
                InputType.__members__,
            )
            return []
        response = await self.client.embed(
            texts=texts,
            model=self.embedding_model_id,
            input_type=INPUT_TYPES_MAPPING[input_type],
            output_dimension=self.embedding_size,
            embedding_types=["float"],
        )
        if response.embeddings.float_ is None:
            self.logger.error("No embeddings returned from Cohere.")
            return []
        return response.embeddings.float_

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
            max_tokens (int): The maximum number of tokens to generate.
            Optional (the global default is used if None).
            temperature (float): The temperature to use for sampling.
            Optional (the global default is used if None).

        Returns:
            Optional[str]: The generated response if available.
        """
        if self.client is None:
            self.logger.error("OpenAI client is not initialized.")
            return None
        if self.generation_model_id is None:
            self.logger.error("Generation model ID is not set.")
            return None
        if chat_history is None:
            chat_history = []
        chat_history.append(self.construct_prompt(prompt, self.enums.USER.value))
        response = await self.client.chat(
            model=self.generation_model_id,
            messages=chat_history,  # type: ignore
            max_tokens=max_tokens or self.default_max_output_tokens,
            temperature=temperature or self.default_temperature,
        )
        if (
            response.message is None
            or response.message.content is None
            or len(response.message.content) == 0
            or response.message.content[0] is None
        ):
            self.logger.error("No response choices returned from OpenAI.")
            return None
        content_item = response.message.content[0]
        if hasattr(content_item, "text"):
            return str(content_item.text)
        elif hasattr(content_item, "thought"):
            return str(content_item.thought)
        else:
            self.logger.error("Unknown content item type in response.")
            return None
