"""
Model definition for a document chunk.
"""

from typing import List, Optional, Sequence
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import functions

from databases.lite_rag.schemas import DocumentChunk
from models.base import BaseDataModel


class DocumentChunkModel(BaseDataModel):
    """
    Model for the DocumentChunk entity.
    """

    def __init__(self, db_session: AsyncSession):
        """Initialize the DocumentChunk model.

        Args:
            db_session (AsyncSession): The SQLAlchemy database async session.
        """
        super().__init__(db_session)
        self.logger.info("DocumentChunkModel initialized")

    async def insert_chunk(self, chunk: DocumentChunk) -> Optional[DocumentChunk]:
        """Insert a new document chunk into the database.

        Args:
            chunk: The document chunk to insert.

        Returns:
            The inserted document chunk with the assigned ID if insertion was successful. \
                Otherwise, None.
        """
        try:
            self.db_session.add(chunk)
            await self.db_session.flush()
            await self.db_session.refresh(chunk)
            return chunk
        except Exception as e:
            self.logger.error("Error inserting document chunk: %s", str(e))
            return None

    async def insert_many_chunks(
        self, chunks: List[DocumentChunk]
    ) -> List[DocumentChunk]:
        """Insert multiple document chunks into the database.

        Args:
            chunks: The list of document chunks to insert.

        Returns:
            The list of inserted document chunks with assigned object_ids.
        """
        if not chunks:
            return []
        try:
            self.db_session.add_all(chunks)
            await self.db_session.flush()
            for chunk in chunks:
                await self.db_session.refresh(chunk)
            return chunks
        except Exception as e:
            self.logger.error("Error inserting assets: %s", str(e))
            return []

    async def get_chunks_by_project(
        self, project_id: UUID, skip: int = 0, limit: int = 10
    ) -> Sequence[DocumentChunk]:
        """Get document chunks for a specific project.

        Args:
            project_id (UUID): The ID of the project.
            skip (int): The number of records to skip for pagination. Defaults to 0.
            limit (int): The maximum number of records to return. Defaults to 10.
        Returns:
            Sequence[DocumentChunk]: The list of document chunks for the specified project.
        """
        result = await self.db_session.execute(
            select(DocumentChunk)
            .where(DocumentChunk.project_id == project_id)
            .offset(skip)
            .limit(limit)
        )
        chunks = result.scalars().all()
        return chunks

    async def delete_chunks_by_project_asset(
        self, project_id: UUID, asset_id: UUID
    ) -> int:
        """Delete document chunks for a specific project and asset.

        Args:
            project_id: The ID of the project.
            asset_id: The ID of the asset.

        Returns:
            The number of deleted chunks.
        """
        result = await self.db_session.execute(
            delete(DocumentChunk).where(
                DocumentChunk.project_id == project_id,
                DocumentChunk.asset_id == asset_id,
            )
        )
        deleted_count = result.rowcount or 0
        return deleted_count

    async def delete_chunks_by_project(self, project_id: UUID) -> int:
        """Delete document chunks for a specific project.

        Args:
            project_id: The ID of the project.

        Returns:
            The number of deleted chunks.
        """
        result = await self.db_session.execute(
            delete(DocumentChunk).where(DocumentChunk.project_id == project_id)
        )
        deleted_count = result.rowcount or 0
        return deleted_count

    async def count_chunks_by_project(self, project_id: UUID) -> int:
        """Count document chunks for a specific project.

        Args:
            project_id: The ID of the project.

        Returns:
            The number of document chunks.
        """
        result = await self.db_session.execute(
            select(functions.count(DocumentChunk.id)).where(
                DocumentChunk.project_id == project_id
            )
        )
        total = result.scalar_one()
        return total
