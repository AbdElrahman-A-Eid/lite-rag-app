"""
Model definitions for assets.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from bson.objectid import ObjectId
from pydantic import BaseModel, ConfigDict, Field
from pymongo import IndexModel, InsertOne
from pymongo.asynchronous.database import AsyncDatabase

from models.base import BaseDataModel, MongoObjectId
from models.enums import CollectionNames


class Asset(BaseModel):
    """Database Schema for the Asset Entity"""

    object_id: Optional[MongoObjectId] = Field(default=None, alias="_id")
    project_id: MongoObjectId = Field(
        ..., description="The Object ID of the project this asset belongs to"
    )
    type: str = Field(..., description="The type of the asset (e.g., file, URL, etc.)")
    name: str = Field(..., description="The name of the asset (e.g., file id, etc.)")
    size: Optional[float] = Field(
        default=None, ge=0, description="The size of the asset in Megabytes"
    )
    config: Dict[str, Any] = Field(
        default_factory=dict, description="Various config of the asset"
    )
    pushed_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="The time when the asset was pushed",
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @staticmethod
    def get_index_fields() -> List[Dict[str, Any]]:
        """Get the index fields for the DocumentChunk model.

        Returns:
            A list of index field names.
        """
        return [
            {
                "keys": [
                    ("project_id", 1),
                ],
                "name": "project_id_index_1",
                "unique": False,
            },
            {
                "keys": [
                    ("project_id", 1),
                    ("name", 1),
                ],
                "name": "project_id_name_index_1",
                "unique": True,
            },
        ]


class AssetModel(BaseDataModel):
    """
    Model for the Asset entity.
    """

    def __init__(self, mongo_db: AsyncDatabase):
        """Initialize the Asset model.

        Args:
            mongo_db (AsyncDatabase): The MongoDB database async instance.
        """
        super().__init__(mongo_db)
        self.collection = self.mongo_db[CollectionNames.ASSETS.value]

    @classmethod
    async def create_instance(cls, mongo_db: AsyncDatabase) -> "AssetModel":
        """Create a new instance of the Asset model.

        Args:
            mongo_db (AsyncDatabase): The MongoDB database async instance.

        Returns:
            AssetModel: The new instance of the Asset model.
        """
        instance = cls(mongo_db)
        await instance.create_index_fields()
        return instance

    async def create_index_fields(self):
        """Create the index fields for the Asset model."""
        self.logger.info("Checking index fields for Asset model...")
        index_fields = Asset.get_index_fields()
        index_info = await self.collection.index_information()
        if any(not index_info.get(index_field["name"]) for index_field in index_fields):
            await self.collection.create_indexes(
                [IndexModel(**index_field) for index_field in index_fields]
            )
            self.logger.info(
                "Created %d index fields for Asset model.", len(index_fields)
            )

    async def insert_asset(self, asset: Asset) -> Asset:
        """Insert a new asset into the database.

        Args:
            asset (Asset): The asset to insert.

        Returns:
            Asset: The inserted asset with the assigned object_id.
        """
        record = await self.collection.insert_one(
            asset.model_dump(exclude={"object_id"})
        )
        asset.object_id = record.inserted_id
        return asset

    async def insert_many_assets(self, assets: List[Asset]) -> List[Asset]:
        """Insert multiple assets into the database.

        Args:
            assets (List[Asset]): The list of assets to insert.

        Returns:
            List[Asset]: The list of inserted assets with assigned object_ids.
        """
        if not assets:
            return []

        operations = [
            InsertOne(asset.model_dump(exclude={"object_id"})) for asset in assets
        ]
        records = await self.collection.bulk_write(operations)
        if records is not None and records.upserted_ids is not None:
            for asset, object_id in zip(assets, records.upserted_ids.values()):
                asset.object_id = object_id
        return assets

    async def get_project_assets(self, project_object_id: ObjectId) -> List[Asset]:
        """Get all assets for a specific project.

        Args:
            project_object_id (ObjectId): The object ID of the project.

        Returns:
            List[Asset]: A list of assets belonging to the project.
        """
        cursor = self.collection.find({"project_id": project_object_id})
        assets = await cursor.to_list(length=None)
        return [Asset(**asset) for asset in assets]

    async def get_asset_by_name(
        self, project_object_id: ObjectId, name: str
    ) -> Optional[Asset]:
        """Get a specific asset by its name for a project.

        Args:
            project_object_id (ObjectId): The object ID of the project.
            name (str): The name of the asset.

        Returns:
            Optional[Asset]: The asset if found, None otherwise.
        """
        asset_data = await self.collection.find_one(
            {"project_id": project_object_id, "name": name}
        )
        if asset_data:
            return Asset(**asset_data)
        return None

    async def get_asset_object_id(
        self, project_object_id: ObjectId, name: str
    ) -> Optional[ObjectId]:
        """Get the ObjectId of a specific asset by its name for a project.

        Args:
            project_object_id (ObjectId): The object ID of the project.
            name (str): The name of the asset.

        Returns:
            Optional[ObjectId]: The ObjectId of the asset if found, None otherwise.
        """
        asset = await self.get_asset_by_name(project_object_id, name)
        return asset.object_id if asset else None

    async def get_asset_name(self, asset_object_id: ObjectId) -> Optional[str]:
        """Get the name of a specific asset by its ObjectId.

        Args:
            asset_object_id (ObjectId): The object ID of the asset.

        Returns:
            Optional[str]: The name of the asset if found, None otherwise.
        """
        asset = await self.collection.find_one({"_id": asset_object_id})
        return asset.name if asset else None

    async def delete_asset(self, project_object_id: ObjectId, name: str) -> bool:
        """Delete a specific asset by its name for a project.

        Args:
            project_object_id (ObjectId): The object ID of the project.
            name (str): The name of the asset.

        Returns:
            bool: True if the asset was deleted, False otherwise.
        """
        asset_object_id = await self.get_asset_object_id(project_object_id, name)
        if not asset_object_id:
            return False
        result = await self.collection.delete_one(
            {"project_id": project_object_id, "name": name}
        )
        return result.deleted_count > 0

    async def delete_assets_by_project(self, project_object_id: ObjectId) -> int:
        """Delete all assets for a specific project.

        Args:
            project_object_id (ObjectId): The object ID of the project.

        Returns:
            int: The number of assets deleted.
        """
        result = await self.collection.delete_many({"project_id": project_object_id})
        self.logger.info(
            "Deleted assets for project '%s': %d",
            str(project_object_id),
            result.deleted_count,
        )
        return result.deleted_count
