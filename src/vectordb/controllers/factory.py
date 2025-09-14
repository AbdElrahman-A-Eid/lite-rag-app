"""
Factory class for creating Vector DB Provider instances.
"""

import logging
from typing import Optional

from config import Settings
from vectordb.models import VectorDBProviderInterface
from vectordb.models.enums import SimilarityMetric, VectorDBProvider
from vectordb.providers import QdrantProvider


class VectorDBProviderFactory:
    """
    Factory class for creating Vector DB Provider instances.
    """

    def __init__(self, config: Settings):
        self.settings = config
        self.logger = logging.getLogger(self.__class__.__name__)

    def create(self, provider: str) -> Optional[VectorDBProviderInterface]:
        """Create and return an instance of the specified Vector DB provider.

        Args:
            provider (str): The name of the Vector DB provider to create.

        Returns:
            VectorDBProviderInterface: An instance of the specified Vector DB provider \
                if supported, None otherwise.
        """
        if provider.upper() == VectorDBProvider.QDRANT.value:
            db_path = self.settings.vectordb_path
            db_path.mkdir(parents=True, exist_ok=True)
            qdrant_provider = QdrantProvider(
                path=db_path,
                distance_metric=SimilarityMetric[
                    self.settings.vectordb_distance_metric.upper()
                ],
            )
            return qdrant_provider
        self.logger.error("Unsupported Vector DB provider type: %s", provider)
        return None
