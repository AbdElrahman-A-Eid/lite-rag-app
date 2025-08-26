"""
Pydantic schemas for project-related requests and responses.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class ProjectCreationResponse(BaseModel):
    """Model for project creation response."""

    project_id: Optional[str] = Field(
        default=None, description="The ID of the created project."
    )
    msg: Optional[str] = Field(
        default=None,
        description="A message indicating the result of the project creation.",
    )


class ProjectListResponse(BaseModel):
    """Model for project list response."""

    projects: List[str] = Field(default=[], description="The list of projects.")
    count: int = Field(default=0, description="The number of projects.")
