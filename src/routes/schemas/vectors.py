"""
Pydantic schemas for document-related requests and responses.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class VectorIndexRequest(BaseModel):
    """
    Request schema for indexing vectors.
    """

    reset: bool = Field(
        default=False,
        description="Whether to reset the index before adding new vectors.",
    )


class VectorQueryRequest(BaseModel):
    """
    Request schema for querying vectors.
    """

    query: str = Field(..., description="The query text to search for similar vectors.")
    top_k: int = Field(
        default=5, ge=1, description="The number of top similar vectors to return."
    )
    threshold: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional similarity threshold for filtering results.",
    )


class VectorIndexResponse(BaseModel):
    """
    Response schema for vector indexing.
    """

    msg: Optional[str] = Field(default=None, description="Response message")


class VectorQueryResponse(BaseModel):
    """
    Response schema for vector querying.
    """

    results: Optional[List[BaseModel]] = Field(
        default=None, description="List of vector search results"
    )
    count: Optional[int] = Field(default=None, description="Number of results returned")
    msg: Optional[str] = Field(default=None, description="Response message")
