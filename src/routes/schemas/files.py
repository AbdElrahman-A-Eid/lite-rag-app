"""
Schemas for file-related requests and responses.
"""

from typing import Optional
from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    """Response schema for file upload."""

    file_id: Optional[str] = Field(
        default=None, description="The ID of the uploaded file"
    )
    project_id: str = Field(
        description="The ID of the project to which the file was uploaded"
    )
    message: Optional[str] = Field(
        default=None, description="A message indicating the result of the upload"
    )
