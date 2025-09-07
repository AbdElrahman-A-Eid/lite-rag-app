"""
Concrete implementation of Vector DB Provider using Qdrant.
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    CollectionDescription,
    ScoredPoint,
)
from vectordb.models import VectorDBProviderInterface
from vectordb.models.enums import SimilarityMetric

DISTANCE_MAPPING = {
    SimilarityMetric.COSINE: Distance.COSINE,
    SimilarityMetric.EUCLIDEAN: Distance.EUCLID,
    SimilarityMetric.DOT_PRODUCT: Distance.DOT,
    SimilarityMetric.MANHATTAN: Distance.MANHATTAN,
}


class QdrantProvider(VectorDBProviderInterface):
    """
    Concrete implementation of Vector DB Provider using Qdrant.
    """

    def __init__(self, path: Path, distance_metric: SimilarityMetric):
        """Initialize the QdrantProvider.

        Args:
            path (Path): The path to the Qdrant database.
            distance_metric (SimilarityMetric): The distance metric to use for vector similarity.
        """
        self.client: Optional[AsyncQdrantClient] = None
        self.path = path
        self.distance_metric = DISTANCE_MAPPING[distance_metric]
        self.logger = logging.getLogger(self.__class__.__name__)

    async def connect(self):
        """Connect to the Qdrant service."""
        self.logger.info("Connecting to Qdrant...")
        self.client = AsyncQdrantClient(path=self.path)
        info = await self.client.info()
        self.logger.info("Connected to Qdrant at %s.", self.path)
        self.logger.info("Qdrant info: %s", info)

    async def disconnect(self):
        """Disconnect from the Qdrant service."""
        self.logger.info("Disconnecting from Qdrant...")
        self.client = None
        self.logger.info("Disconnected from Qdrant.")

    async def index_exists(self, index_name: str) -> bool:
        """Check if an index exists in the Vector DB.

        Args:
            index_name (str): The name of the index to check.

        Returns:
            bool: True if the index exists, False otherwise.
        """
        if not self.client:
            self.logger.error("Qdrant client is not initialized.")
            return False
        return await self.client.collection_exists(collection_name=index_name)

    async def create_index(
        self, index_name: str, dimensions: int, replace: bool = False
    ):
        """Create a new index in the Vector DB.

        Args:
            index_name (str): The name of the index to create.
            dimensions (int): The dimensionality of the vectors to be stored.
            replace (bool): Whether to replace the index if it exists.
        """
        self.logger.info(
            "Creating index '%s' with dimensions %d...", index_name, dimensions
        )
        if not self.client:
            self.logger.error("Qdrant client is not initialized.")
            return
        if await self.index_exists(index_name):
            if not replace:
                self.logger.error(
                    "Index '%s' already exists. Skipping index creation...", index_name
                )
                return
            self.logger.info("Replacing existing index '%s'...", index_name)
            await self.client.delete_collection(collection_name=index_name)
        await self.client.create_collection(
            collection_name=index_name,
            vectors_config=VectorParams(size=dimensions, distance=self.distance_metric),
        )
        self.logger.info("Index '%s' created successfully.", index_name)

    async def delete_index(self, index_name: str):
        """Delete an index from the Vector DB.

        Args:
            index_name (str): The name of the index to delete.
        """
        self.logger.info("Deleting index '%s'...", index_name)
        if not self.client:
            self.logger.error("Qdrant client is not initialized.")
            return
        if await self.index_exists(index_name):
            await self.client.delete_collection(collection_name=index_name)
            self.logger.info("Index '%s' deleted successfully.", index_name)
        else:
            self.logger.warning("Index '%s' does not exist.", index_name)

    async def list_indexes(self) -> List[CollectionDescription]:
        """List all indexes in the Vector DB.

        Returns:
            List[CollectionDescription]: A list of indexes available in the vector database.
        """
        if not self.client:
            self.logger.error("Qdrant client is not initialized.")
            return []
        collections = await self.client.get_collections()
        return [collection for collection in collections.collections]

    async def get_index_info(self, index_name: str) -> Optional[Dict]:
        """Get information about a specific index.

        Args:
            index_name (str): The name of the index to get information about.

        Returns:
            Optional[Dict]: A dictionary containing index information, or None if the \
                index does not exist.
        """
        if not self.client:
            self.logger.error("Qdrant client is not initialized.")
            return None
        if not await self.index_exists(index_name):
            self.logger.error("Index '%s' does not exist.", index_name)
            return None
        collection = await self.client.get_collection(collection_name=index_name)
        return collection.model_dump()

    async def insert_vector(
        self,
        index_name: str,
        text: str,
        vector: List[float],
        metadata: Optional[Dict] = None,
        record_id: Optional[str] = None,
    ) -> None:
        """Insert a vector into the specified index.

        Args:
            index_name (str): The name of the index to insert the vector into.
            text (str): The text associated with the vector.
            vector (List[float]): The vector data to insert.
            metadata (Optional[Dict], optional): Metadata to associate with the vector. \
                Defaults to None.
            record_id (Optional[str], optional): The ID of the record to insert. Defaults to None.
        """
        if not self.client:
            self.logger.error("Qdrant client is not initialized.")
            return
        if not await self.index_exists(index_name):
            self.logger.error("Index '%s' does not exist.", index_name)
            return

        try:
            self.client.upload_collection(
                collection_name=index_name,
                vectors=[vector],
                payload=[
                    {
                        "text": text,
                        "metadata": metadata,
                    }
                ],
                wait=True,
            )
        except Exception as e:
            self.logger.error(
                "Error inserting vector into index '%s': %s",
                index_name,
                e,
                exc_info=True,
            )

    async def insert_vectors(
        self,
        index_name: str,
        texts: List[str],
        vectors: List[List[float]],
        metadata: Optional[List[Dict]] = None,
        record_ids: Optional[List[str]] = None,
        batch_size: int = 64,
    ):
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
        """
        if not self.client:
            self.logger.error("Qdrant client is not initialized.")
            return
        if not await self.index_exists(index_name):
            self.logger.error("Index '%s' does not exist.", index_name)
            return
        if metadata and len(metadata) != len(vectors):
            self.logger.error(
                "Length of metadata (%d) does not match length of vectors (%d).",
                len(metadata),
                len(vectors),
            )
            return
        if len(texts) != len(vectors):
            self.logger.error(
                "Length of texts (%d) does not match length of vectors (%d).",
                len(texts),
                len(vectors),
            )
            return
        try:
            self.client.upload_collection(
                collection_name=index_name,
                vectors=vectors,
                payload=[
                    {
                        "text": text,
                        "metadata": metadata,
                    }
                    for text, metadata in zip(texts, metadata or [{}] * len(texts))
                ],
                batch_size=batch_size,
                wait=True,
            )
        except Exception as e:
            self.logger.error(
                "Error inserting vectors into index '%s': %s",
                index_name,
                e,
                exc_info=True,
            )

    async def query_vectors(
        self, index_name: str, query_vector: List[float], top_k: int
    ) -> List[ScoredPoint]:
        """Query the specified index for similar vectors.

        Args:
            index_name (str): The name of the index to query.
            query_vector (List[float]): The vector to query against.
            top_k (int): The number of top similar vectors to return.

        Returns:
            List[ScoredPoint]: A list of the most similar vectors.
        """
        if not self.client:
            self.logger.error("Qdrant client is not initialized.")
            return []
        if not await self.index_exists(index_name):
            self.logger.error("Index '%s' does not exist.", index_name)
            return []
        try:
            results = await self.client.search(
                collection_name=index_name,
                query_vector=query_vector,
                top_k=top_k,
            )
            return results
        except Exception as e:
            self.logger.error(
                "Error querying vectors from index '%s': %s",
                index_name,
                e,
                exc_info=True,
            )
            return []
