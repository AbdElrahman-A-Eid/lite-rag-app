"""
Schemas for file-related requests and responses.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from models.enums import AssetType


class Asset(BaseModel):
    """Pydantic model for an asset."""

    id: UUID = Field(..., description="The unique identifier of the asset")
    project_id: UUID = Field(
        ..., description="The ID of the project this asset belongs to"
    )
    type: AssetType = Field(
        ..., description="The type of the asset (e.g., file, URL, etc.)"
    )
    name: str = Field(..., description="The name of the asset (e.g., file id, etc.)")
    size: Optional[float] = Field(
        default=None, ge=0, description="The size of the asset in Megabytes"
    )
    config: Dict[str, Any] = Field(
        default_factory=dict, description="Various config of the asset"
    )
    created_at: datetime = Field(
        description="The timestamp when the asset was created.",
    )
    updated_at: datetime = Field(
        description="The timestamp when the asset was last updated.",
    )

    class Config:
        from_attributes = True


class AssetResponse(BaseModel):
    """Response schema for asset operations."""

    value: Optional[Asset] = Field(
        default=None, description="The asset object if the operation was successful"
    )
    msg: Optional[str] = Field(
        default=None, description="A message indicating the result of the operation"
    )


class AssetListResponse(BaseModel):
    """Response schema for operations involving multiple assets."""

    values: Optional[List[Asset]] = Field(default=None, description="List of assets")
    count: Optional[int] = Field(default=None, description="The number of assets")
    total: Optional[int] = Field(
        default=None, description="The total number of assets."
    )
    msgs: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="A list of message dictionaries indicating the results of the asset operations",
    )
