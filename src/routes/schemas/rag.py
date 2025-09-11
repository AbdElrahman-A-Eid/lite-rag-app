"""
Pydantic schemas for RAG-related requests and responses.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from models.vector import RetrievedDocumentChunk


class RAGQueryRequest(BaseModel):
    """
    Request schema for querying RAG generation.
    """

    query: str = Field(..., description="The query text to generate RAG responses.")
    top_k: int = Field(
        default=5, ge=1, description="The number of top similar vectors to return."
    )
    threshold: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional similarity threshold for filtering context documents.",
    )
    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="Optional temperature for controlling the randomness of the LLM output.",
    )
    max_output_tokens: Optional[int] = Field(
        default=None,
        ge=1,
        description="Optional maximum number of tokens to generate in the LLM output.",
    )


class RAGQueryResponse(BaseModel):
    """
    Response schema for RAG querying.
    """

    response: Optional[str] = Field(default=None, description="List of RAG response")
    citations: Optional[List[RetrievedDocumentChunk]] = Field(
        default=None,
        description="List of citations within the RAG response (as per the LLM output)",
    )
    contexts: Optional[List[RetrievedDocumentChunk]] = Field(
        default=None, description="List of context documents used in the RAG request"
    )
    msg: Optional[str] = Field(default=None, description="Response message")
