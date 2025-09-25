"""
Model definitions for assets.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from databases.lite_rag.schemas import Asset
from models.base import BaseDataModel


class AssetModel(BaseDataModel):
    """
    Model for the Asset entity.
    """

    def __init__(self, db_session: AsyncSession):
        """Initialize the Asset model.

        Args:
            db_session (AsyncSession): The SQLAlchemy database async session.
        """
        super().__init__(db_session)
        self.logger.info("AssetModel initialized")

    async def insert_asset(self, asset: Asset) -> Optional[Asset]:
        """Insert a new asset into the database.

        Args:
            asset (Asset): The asset to insert.

        Returns:
            Optional[Asset]: The asset with the assigned id if successfully inserted. \
                None otherwise.
        """
        try:
            self.db_session.add(asset)
            await self.db_session.flush()
            await self.db_session.refresh(asset)
            return asset
        except Exception as e:
            self.logger.error("Error inserting asset: %s", str(e))
            return None

    async def insert_many_assets(self, assets: List[Asset]) -> List[Asset]:
        """Insert multiple assets into the database.

        Args:
            assets (List[Asset]): The list of assets to insert.

        Returns:
            List[Asset]: The list of inserted assets with assigned IDs.
        """
        if not assets:
            return []
        try:
            self.db_session.add_all(assets)
            await self.db_session.flush()
            for asset in assets:
                await self.db_session.refresh(asset)
            return assets
        except Exception as e:
            self.logger.error("Error inserting assets: %s", str(e))
            return []

    async def get_asset_by_id(self, asset_id: UUID) -> Optional[Asset]:
        """Get a specific asset by its ID.

        Args:
            asset_id (UUID): The ID of the asset.

        Returns:
            Optional[Asset]: The asset if found, None otherwise.
        """

        result = await self.db_session.execute(
            select(Asset).where(Asset.id == asset_id)
        )
        asset = result.scalars().first()
        return asset

    async def get_asset_by_name(self, project_id: UUID, name: str) -> Optional[Asset]:
        """Get a specific asset by its name for a project.

        Args:
            project_id (UUID): The ID of the project.
            name (str): The name of the asset.

        Returns:
            Optional[Asset]: The asset if found, None otherwise.
        """

        result = await self.db_session.execute(
            select(Asset).where(
                Asset.project_id == project_id,
                Asset.name == name,
            )
        )
        asset = result.scalars().first()
        return asset

    async def delete_asset(self, project_id: UUID, name: str) -> bool:
        """Delete a specific asset by its name for a project.

        Args:
            project_id (UUID): The ID of the project.
            name (str): The name of the asset.

        Returns:
            bool: True if the asset was deleted, False otherwise.
        """
        result = await self.db_session.execute(
            delete(Asset).where(
                Asset.project_id == project_id,
                Asset.name == name,
            )
        )
        deleted_count = result.rowcount or 0
        return deleted_count > 0

    async def delete_assets_by_project(self, project_id: UUID) -> int:
        """Delete all assets for a specific project.

        Args:
            project_id (UUID): The ID of the project.

        Returns:
            int: The number of assets deleted.
        """

        result = await self.db_session.execute(
            delete(Asset).where(Asset.project_id == project_id)
        )
        deleted_count = result.rowcount or 0
        return deleted_count
