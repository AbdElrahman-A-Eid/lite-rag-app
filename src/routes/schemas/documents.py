"""
Pydantic schemas for document-related requests and responses.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Chunk(BaseModel):
    """Pydantic model for a document chunk."""

    id: UUID = Field(..., description="The unique identifier of the chunk")
    project_id: UUID = Field(
        ..., description="The ID of the project this chunk belongs to"
    )
    asset_id: UUID = Field(..., description="The ID of the asset this chunk belongs to")
    order: int = Field(..., description="The order of the chunk in the document")
    content: str = Field(..., description="The text content of the chunk")
    metadata_: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata associated with the chunk",
        serialization_alias="metadata",
    )
    created_at: datetime = Field(
        description="The timestamp when the chunk was created.",
    )
    updated_at: datetime = Field(
        description="The timestamp when the chunk was last updated.",
    )

    model_config = ConfigDict(from_attributes=True)


class DocumentProcessingRequest(BaseModel):
    """Request schema for document processing."""

    file_id: str = Field(description="The ID of the file to process.")
    chunk_size: int = Field(gt=0, description="The size of each chunk.", default=300)
    chunk_overlap: int = Field(
        ge=0, description="The overlap between chunks.", default=40
    )
    replace_existing: bool = Field(
        default=False, description="Whether to replace existing chunks for the asset."
    )


class ProjectDocumentsRefreshRequest(BaseModel):
    """Request schema for project documents refresh."""

    chunk_size: int = Field(gt=0, description="The size of each chunk.", default=300)
    chunk_overlap: int = Field(
        ge=0, description="The overlap between chunks.", default=40
    )
    replace_existing: bool = Field(
        default=False, description="Whether to replace all existing chunks."
    )


class ChunkResponse(BaseModel):
    """Response model for a document chunk."""

    value: Optional[Chunk] = Field(default=None, description="The document chunk data.")
    msg: Optional[str] = Field(
        default=None, description="A message indicating the result of the processing."
    )


class ChunkListResponse(BaseModel):
    """Response schema for listing document chunks."""

    values: Optional[List[Chunk]] = Field(
        default=None, description="The list of document chunks."
    )
    count: Optional[int] = Field(default=None, description="The number of chunks.")
    total: Optional[int] = Field(
        default=None, description="The total number of chunks."
    )
    msg: Optional[str] = Field(
        default=None, description="A message indicating the result of the processing."
    )


class BatchDocumentsResponse(BaseModel):
    """Response schema for batch document processing."""

    values: Dict[str, ChunkListResponse] = Field(
        default_factory=dict,
        description="A mapping of asset names to their chunk responses.",
    )
    count: Optional[int] = Field(
        default=None, description="The number of successful assets."
    )
    total: Optional[int] = Field(
        default=None, description="The total number of assets."
    )
