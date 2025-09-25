"""
Pydantic schemas for project-related requests and responses.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreationRequest(BaseModel):
    """Model for project creation request."""

    name: Optional[str] = Field(default=None, description="The name of the project.")
    description: Optional[str] = Field(
        default=None, max_length=500, description="The description of the project."
    )


class Project(BaseModel):
    """Pydantic model for Project."""

    id: UUID = Field(description="The unique identifier of the project.")
    name: str = Field(description="The name of the project.")
    description: str = Field(description="The description of the project.")
    created_at: datetime = Field(
        description="The timestamp when the project was created.",
    )
    updated_at: datetime = Field(
        description="The timestamp when the project was last updated.",
    )

    model_config = ConfigDict(from_attributes=True)


class ProjectResponse(BaseModel):
    """Response schema for project operations."""

    value: Optional[Project] = Field(default=None, description="The project details.")
    msg: Optional[str] = Field(
        default=None,
        description="A message indicating the result of the project operation.",
    )


class ProjectListResponse(BaseModel):
    """Response schema for operations involving multiple projects."""

    values: Optional[List[Project]] = Field(
        default=None, description="The list of projects."
    )
    count: Optional[int] = Field(default=None, description="The number of projects.")
    total: Optional[int] = Field(
        default=None, description="The total number of projects."
    )
    msg: Optional[str] = Field(
        default=None,
        description="A message indicating the result of the project operation.",
    )
