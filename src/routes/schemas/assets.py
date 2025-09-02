"""
Schemas for file-related requests and responses.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from models.enums import AssetType


class AssetPushResponse(BaseModel):
    """Response schema for asset push."""

    project_id: str = Field(
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
    msg: Optional[str] = Field(
        default=None, description="A message indicating the result of the upload"
    )


class BatchAssetsPushResponse(BaseModel):
    """Response schema for batch asset push."""

    project_id: str = Field(
        ..., description="The ID of the project this asset belongs to"
    )
    assets: List[AssetPushResponse] = Field(
        default_factory=list, description="List of assets that were uploaded"
    )
    msgs: Optional[List[Dict[str, str]]] = Field(
        default=None, description="Messages indicating the results of the upload"
    )


class AssetListResponse(BaseModel):
    """Response schema for listing assets."""

    assets: List[AssetPushResponse] = Field(
        default_factory=list, description="List of assets for the project"
    )
    count: Optional[int] = Field(
        default=None, description="Total number of assets for the project"
    )
    msg: Optional[str] = Field(
        default=None, description="A message indicating the result of the asset listing"
    )
