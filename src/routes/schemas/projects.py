"""
Pydantic schemas for project-related requests and responses.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class ProjectCreationRequest(BaseModel):
    """Model for project creation request."""

    name: Optional[str] = Field(default=None, description="The name of the project.")
    description: Optional[str] = Field(
        default=None, max_length=500, description="The description of the project."
    )


class ProjectCreationResponse(BaseModel):
    """Model for project creation response."""

    id: Optional[str] = Field(
        default=None, description="The ID of the created project."
    )
    name: str
    description: str
    msg: Optional[str] = Field(
        default=None,
        description="A message indicating the result of the project creation.",
    )


class ProjectListResponse(BaseModel):
    """Model for project list response."""

    projects: List[ProjectCreationResponse] = Field(
        default=[], description="The list of projects."
    )
    count: int = Field(default=0, description="The number of projects.")
    total: int = Field(default=0, description="The total number of projects.")
