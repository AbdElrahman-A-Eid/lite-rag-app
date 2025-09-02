"""
Pydantic schemas for document-related requests and responses.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class DocumentProcessingRequest(BaseModel):
    """Request schema for document processing."""

    file_id: str = Field(description="The ID of the file to process.")
    chunk_size: int = Field(gt=0, description="The size of each chunk.", default=300)
    chunk_overlap: int = Field(
        ge=0, description="The overlap between chunks.", default=40
    )


class ChunkResponse(BaseModel):
    """Response model for a document chunk."""

    chunk_order: int = Field(description="The order of the chunk in the document.")
    page_content: str = Field(description="The text content of the chunk.")
    metadata: Dict[str, Any] = Field(description="Metadata associated with the chunk.")

    model_config = ConfigDict(from_attributes=True)


class DocumentProcessingResponse(BaseModel):
    """Response schema for document processing."""

    project_id: str = Field(description="The ID of the project.")
    file_id: str = Field(description="The ID of the file.")
    chunks: Optional[List[ChunkResponse]] = Field(
        default=None, description="The list of document chunks."
    )
    count: Optional[int] = Field(default=None, description="The number of chunks.")
    msg: Optional[str] = Field(
        default=None, description="A message indicating the result of the processing."
    )


class DocumentListResponse(BaseModel):
    """Response schema for listing document chunks."""

    project_id: str = Field(description="The ID of the project.")
    file_id: str = Field(description="The ID of the file.")
    chunks: Optional[List[ChunkResponse]] = Field(
        default=None, description="The list of document chunks."
    )
    count: Optional[int] = Field(default=None, description="The number of chunks.")
    total: int = Field(default=0, description="The total number of chunks.")
    msg: Optional[str] = Field(
        default=None, description="A message indicating the result of the processing."
    )
