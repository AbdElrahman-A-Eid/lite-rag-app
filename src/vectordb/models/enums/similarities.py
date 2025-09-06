"""
Defines the similarity metrics available for vector search.
"""

from enum import Enum


class SimilarityMetric(str, Enum):
    """Defines the similarity metrics supported for vector search."""

    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"
    MANHATTAN = "manhattan"
