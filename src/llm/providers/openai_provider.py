"""
Concrete implementation of the OpenAI LLM provider.
"""

from enum import Enum
from typing import Optional, Dict, List
from openai import OpenAI
from llm.models.base import BaseLLMProvider
from llm.models.enums.inputs import InputType


class OpenAIMessageRoles(str, Enum):
    """Message roles specific to OpenAI."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class OpenAIProvider(BaseLLMProvider):
    """
    Concrete implementation of the OpenAI LLM provider.
    """

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        max_input_characters: int = 3000,
        default_max_output_tokens: int = 1024,
        default_temperature: float = 0.15,
        **kwargs
    ):
        super().__init__(
            max_input_characters,
            default_max_output_tokens,
            default_temperature,
        )
        self.api_key = api_key
        self.base_url = base_url
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url, **kwargs)
        self.enums = OpenAIMessageRoles

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
                "Invalid role: %s. Must be one of %s.", role, [e.value for e in self.enums]
            )
            role = self.enums.USER.value
        return {"role": role, "content": self.process_text(prompt)}

    def embed(
        self, text: str | List[str], input_type: Optional[InputType] = None
    ) -> List[float] | List[List[float]]:
        """
        Generate embeddings for the given text.

        Args:
            text (str | List[str]): The text or list of texts to generate embeddings for.
            input_type (Optional[InputType]): The type of input (e.g., "document", "query").

        Returns:
            List[float] | List[List[float]]: The generated embeddings.
        """
        if self.client is None:
            self.logger.error("OpenAI client is not initialized.")
            return []
        if self.embedding_model_id is None or self.embedding_size is None:
            self.logger.error("Embedding model ID or size is not set.")
            return []
        if isinstance(text, str):
            text = [text]
        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_model_id,
            dimensions=self.embedding_size,
            encoding_format="float",
        )
        if isinstance(text, str):
            return response.data[0].embedding
        return [item.embedding for item in response.data]

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
        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,  # type: ignore
            max_tokens=max_tokens or self.default_max_output_tokens,
            temperature=temperature or self.default_temperature,
        )
        if (
            response.choices is None
            or len(response.choices) == 0
            or response.choices[0].message is None
        ):
            self.logger.error("No response choices returned from OpenAI.")
            return None
        return response.choices[0].message.content
