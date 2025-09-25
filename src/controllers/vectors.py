"""
Controllers for managing Vector operations.
"""

from typing import List, Optional
from uuid import UUID

from config import Settings
from controllers.base import BaseController
from llm.models.base import LLMProviderInterface
from llm.models.enums.inputs import InputType
from models.chunk import DocumentChunk
from models.vector import RetrievedDocumentChunk
from vectordb.models import VectorDBProviderInterface


class VectorController(BaseController):
    """
    Controller for managing Vector operations.
    """

    def __init__(
        self,
        settings: Settings,
        vectordb_client: VectorDBProviderInterface,
        embedding_model: LLMProviderInterface,
    ):
        """Initialize the VectorController.

        Args:
            settings (Settings): The application settings.
            vectordb_client (VectorDBProviderInterface): The vector database client.
            embedding_model (LLMProviderInterface): The LLM model to use for generating embeddings.
        """
        super().__init__(settings)
        self.vectordb_client = vectordb_client
        self.embedding_model = embedding_model
        self.logger.info("VectorController initialized")

    def _construct_index_name(self, project_id: UUID, embedding_size: int) -> str:
        """Construct the index name based on the project ID and embedding size.

        Args:
            project_id (UUID): The project ID.
            embedding_size (int): The size of the embeddings.

        Returns:
            str: The constructed index name.
        """
        return f"index_{embedding_size}_{str(project_id)}"

    async def create_index(self, project_id: UUID, replace: bool = False):
        """Create a new index for the given project ID.

        Args:
            project_id (UUID): The project ID.
            replace (bool): Whether to replace the existing index if it exists.
        """
        index_name = self._construct_index_name(
            project_id, self.embedding_model.embedding_size_
        )
        self.logger.info("Creating index: %s", index_name)

        await self.vectordb_client.create_index(
            index_name, dimensions=self.embedding_model.embedding_size_, replace=replace
        )

    async def get_index_info(self, project_id: UUID):
        """Get the index info for the given project ID.

        Args:
            project_id (UUID): The project ID.

        Returns:
            The index for the project ID.
        """
        index_name = self._construct_index_name(
            project_id, self.embedding_model.embedding_size_
        )
        self.logger.info("Getting index info: %s", index_name)

        return await self.vectordb_client.get_index_info(index_name)

    def _normalize_vectors(self, vectors: List) -> List[List[float]]:
        """Normalize the vectors to ensure it is a list of lists.

        Args:
            vectors (List): The vectors to normalize.

        Returns:
            List[List[float]]: The normalized vectors.
        """
        if vectors and isinstance(vectors[0], float):
            return [vectors]
        return vectors

    async def query_vectors(
        self,
        project_id: UUID,
        query: str,
        top_k: int,
        threshold: Optional[float] = None,
    ) -> List[RetrievedDocumentChunk]:
        """Query the vectors for the project ID.

        Args:
            project_id (UUID): The project ID.
            query (str): The query string.
            top_k (int): The number of top results to return.
            threshold (Optional[float], optional): Minimum similarity score to consider. \
                Defaults to None.

        Returns:
            List[RetrievedDocumentChunk]: The list of the retrieved document chunks \
                relevant to the query.
        """
        index_name = self._construct_index_name(
            project_id, self.embedding_model.embedding_size_
        )
        self.logger.info("Querying vectors for project: '%s'...", str(project_id))

        query_vector = await self.embedding_model.embed(
            [query], input_type=InputType.QUERY
        )
        normalized_query_vector = self._normalize_vectors(query_vector)[0]
        relevant_vectors = await self.vectordb_client.query_vectors(
            index_name,
            query_vector=normalized_query_vector,
            top_k=top_k,
            threshold=threshold,
        )
        return relevant_vectors

    async def index_vectors(
        self, project_id: UUID, chunks: List[DocumentChunk], reset: bool
    ) -> bool:
        """Index the given vectors for the project ID.

        Args:
            project_id (UUID): The project ID.
            chunks (List[DocumentChunk]): The document chunks to index.
            reset (bool): Whether to reset the index before adding new vectors.

        Returns:
            bool: True if indexing was successful, False otherwise.
        """
        index_name = self._construct_index_name(
            project_id, self.embedding_model.embedding_size_
        )
        self.logger.info(
            "Indexing %d vectors for project: '%s'...", len(chunks), str(project_id)
        )

        await self.create_index(project_id, replace=reset)

        texts = [chunk.content for chunk in chunks]
        metadatas = [chunk.metadata_ for chunk in chunks]
        for metadata, chunk in zip(metadatas, chunks):
            metadata["chunk_asset"] = str(chunk.asset_id)
            metadata["chunk_order"] = chunk.order
        vectors = []
        for i in range(0, len(texts), 64):
            batch_texts = texts[i : i + 64]
            batch_vectors = await self.embedding_model.embed(
                batch_texts, input_type=InputType.DOCUMENT
            )
            vectors.extend(self._normalize_vectors(batch_vectors))
        normalized_vectors = self._normalize_vectors(vectors)

        return await self.vectordb_client.insert_vectors(
            index_name,
            texts=texts,
            vectors=normalized_vectors,
            metadata=metadatas,
        )

    async def delete_index(self, project_id: UUID):
        """Delete the index for the given project ID.

        Args:
            project_id (UUID): The project ID.
        """
        index_name = self._construct_index_name(
            project_id, self.embedding_model.embedding_size_
        )
        self.logger.info("Deleting index: %s", index_name)

        await self.vectordb_client.delete_index(index_name)
