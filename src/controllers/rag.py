"""
Controllers for managing RAG operations.
"""

from typing import List, Optional
import re

from config import Settings
from controllers.base import BaseController
from llm.models.base import LLMProviderInterface
from llm.models.enums.roles import MessageRole
from models.vector import RetrievedDocumentChunk


class RAGController(BaseController):
    """
    Controller for managing RAG operations.
    """

    def __init__(
        self,
        settings: Settings,
        generation_model: LLMProviderInterface,
    ):
        """Initialize the RAGController.

        Args:
            generation_model (LLMProviderInterface): The LLM model to use for generating \
                RAG responses.
        """
        super().__init__(settings)
        self.generation_model = generation_model
        self.logger.info("RAGController initialized")

    def generate_response(
        self,
        query: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
    ) -> Optional[str]:
        """Generate a response using RAG.

        Args:
            query (str): The input query.
            system_message (str, optional): The system message to include in the response.

        Returns:
            Optional[str]: The generated response if available.
        """
        system_message_dict = None
        if not system_message:
            self.logger.warning("No system message provided for RAG generation.")
        else:
            system_message_dict = [
                self.generation_model.construct_prompt(
                    prompt=system_message,
                    role=MessageRole.SYSTEM.value,
                )
            ]

        response = self.generation_model.generate(
            prompt=query,
            chat_history=system_message_dict,
            max_tokens=max_output_tokens,
            temperature=temperature,
        )

        return response

    def extract_citations(
        self, response: str, context_entries: List[RetrievedDocumentChunk]
    ) -> List[RetrievedDocumentChunk]:
        """Extract citations from the generated response.

        Extracts citations in the format [reference: index] where index is an integer (1-based)
        and maps them back to context entries. Supports flexible formats.

        Args:
            response (str): The generated response.
            context_entries (List[RetrievedDocumentChunk]): The context entries used \
                in the RAG request.

        Returns:
            List[RetrievedDocumentChunk]: A list of extracted citations.
        """
        citation_patterns = [
            r"\[reference:\s*(\d+(?:\s*,\s*\d+)*)\]",  # [reference: 1] or [reference: 1, 2, 3]
            r"\[ref:\s*(\d+(?:\s*,\s*\d+)*)\]",  # [ref: 1] or [ref: 1, 2]
            r"\[source:\s*(\d+(?:\s*,\s*\d+)*)\]",  # [source: 1] or [source: 1, 2]
            r"\[doc:\s*(\d+(?:\s*,\s*\d+)*)\]",  # [doc: 1] or [doc: 1, 2]
            r"\[(\d+(?:\s*,\s*\d+)*)\]",  # [1] or [1, 2, 3]
            r"\[references:\s*(\d+(?:\s*,\s*\d+)*)\]",  # [references: 1, 2]
            r"\[sources:\s*(\d+(?:\s*,\s*\d+)*)\]",  # [sources: 1, 2]
            r"\[docs:\s*(\d+(?:\s*,\s*\d+)*)\]",  # [docs: 1, 2]
        ]

        # Extract all cited indices from the response
        cited_indices = set()
        citation_positions = []

        for pattern in citation_patterns:
            for match in re.finditer(pattern, response, re.IGNORECASE):
                indices_str = match.group(1).strip()
                position = match.start()

                # Parse comma-separated indices
                for index_str in indices_str.split(","):
                    try:
                        index = int(index_str.strip())
                        if index > 0:  # Only accept positive indices
                            cited_indices.add(index)
                            citation_positions.append((index, position))
                            self.logger.debug(
                                "Found citation for index: %d at position %d",
                                index,
                                position,
                            )
                    except ValueError:
                        self.logger.warning(
                            "Invalid citation index: %s", index_str.strip()
                        )
                        continue

        # Sort by position to maintain order of appearance in text
        citation_positions.sort(key=lambda x: x[1])

        # Map indices to context entries (convert 1-based to 0-based indexing)
        index_to_entry = {}
        for i, entry in enumerate(context_entries):
            one_based_index = i + 1
            index_to_entry[one_based_index] = entry

        # Extract cited entries in order of appearance
        seen_indices = set()
        ordered_citations = []

        for index, position in citation_positions:
            if index in index_to_entry and index not in seen_indices:
                entry = index_to_entry[index]
                ordered_citations.append(entry)
                seen_indices.add(index)
                self.logger.debug("Mapped citation index %d to context entry", index)
            elif index not in index_to_entry:
                self.logger.warning(
                    "Citation index %d is out of range (only %d context entries available)",
                    index,
                    len(context_entries),
                )

        # Add any remaining cited indices that weren't processed yet
        for index in sorted(cited_indices):
            if index in index_to_entry and index not in seen_indices:
                entry = index_to_entry[index]
                ordered_citations.append(entry)
                seen_indices.add(index)

        self.logger.info("Extracted %d citations from response", len(ordered_citations))
        return ordered_citations
