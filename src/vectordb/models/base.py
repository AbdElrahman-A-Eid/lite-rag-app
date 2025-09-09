"""
Base classes for all Vector DB providers.
"""

from typing import Optional, List, Dict
from abc import ABC, abstractmethod
from models.vector import RetrievedDocumentChunk


class VectorDBProviderInterface(ABC):
    """
    Interface for all Vector DB provider classes to implement.
    """

    @abstractmethod
    async def connect(self):
        """Connect to the Vector DB service."""

    @abstractmethod
    async def disconnect(self):
        """Disconnect from the Vector DB service."""

    @abstractmethod
    async def create_index(
        self, index_name: str, dimensions: int, replace: bool = False
    ):
        """Create a new index in the Vector DB.

        Args:
            index_name (str): The name of the index to create.
            dimensions (int): The dimensionality of the vectors to be stored.
            replace (bool): Whether to replace the index if it exists.
        """

    @abstractmethod
    async def delete_index(self, index_name: str):
        """Delete an index from the Vector DB.

        Args:
            index_name (str): The name of the index to delete.
        """

    @abstractmethod
    async def index_exists(self, index_name: str) -> bool:
        """Check if an index exists in the Vector DB.

        Args:
            index_name (str): The name of the index to check.

        Returns:
            bool: True if the index exists, False otherwise.
        """

    @abstractmethod
    async def list_indexes(self) -> List:
        """List all indexes in the Vector DB.

        Returns:
            List: A list of indexes available in the vector database.
        """

    @abstractmethod
    async def get_index_info(self, index_name: str) -> Optional[Dict]:
        """Get information about a specific index.

        Args:
            index_name (str): The name of the index to get information about.

        Returns:
            Optional[Dict]: A dictionary containing index information, or None if the \
                index does not exist.
        """

    @abstractmethod
    async def insert_vector(
        self,
        index_name: str,
        text: str,
        vector: List[float],
        metadata: Optional[Dict] = None,
        record_id: Optional[str] = None,
    ):
        """Insert a vector into the specified index.

        Args:
            index_name (str): The name of the index to insert the vector into.
            text (str): The text associated with the vector.
            vector (List[float]): The vector data to insert.
            metadata (Optional[Dict], optional): Metadata to associate with the vector. \
                Defaults to None.
            record_id (Optional[str], optional): The ID of the record to insert. Defaults to None.
        """

    @abstractmethod
    async def insert_vectors(
        self,
        index_name: str,
        texts: List[str],
        vectors: List[List[float]],
        metadata: Optional[List[Dict]] = None,
        record_ids: Optional[List[str]] = None,
        batch_size: int = 64,
    ) -> bool:
        """Insert vectors into the specified index.

        Args:
            index_name (str): The name of the index to insert vectors into.
            texts (List[str]): A list of texts associated with the vectors.
            vectors (List[List[float]]): A list of vectors to insert.
            metadata (Optional[List[Dict]], optional): A list of metadata dictionaries to \
                associate with the vectors. Defaults to None.
            record_ids (Optional[List[str]], optional): A list of record IDs to insert. \
                Defaults to None.
            batch_size (int, optional): The number of vectors to insert per batch. \
                Defaults to 64.

        Returns:
            bool: True if the vectors were inserted successfully, False otherwise.
        """

    @abstractmethod
    async def query_vectors(
        self,
        index_name: str,
        query_vector: List[float],
        top_k: int,
        threshold: Optional[float] = None,
    ) -> List[RetrievedDocumentChunk]:
        """Query the specified index for similar vectors.

        Args:
            index_name (str): The name of the index to query.
            query_vector (List[float]): The vector to query against.
            top_k (int): The number of top similar vectors to return.
            threshold (Optional[float], optional): Minimum similarity score to consider. \
                Defaults to None.

        Returns:
            List[RetrievedDocumentChunk]: A list of the most similar vectors.
        """
