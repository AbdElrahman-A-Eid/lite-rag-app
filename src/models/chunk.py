"""
Model definition for a document chunk.
"""

from typing import Dict, List, Optional, Any

from bson.objectid import ObjectId
from pydantic import BaseModel, ConfigDict, Field
from pymongo import InsertOne
from pymongo.asynchronous.database import AsyncDatabase

from models.base import BaseDataModel
from models.enums import CollectionNames


class DocumentChunk(BaseModel):
    """Model definition for a document chunk."""

    object_id: Optional[ObjectId] = Field(default=None, alias="_id")
    project_id: str
    file_id: str
    chunk_order: int
    page_content: str
    metadata: Dict[str, Any]

    model_config = ConfigDict(arbitrary_types_allowed=True)


class DocumentChunkModel(BaseDataModel):
    """
    Model for the DocumentChunk entity.
    """

    def __init__(self, mongo_db: AsyncDatabase):
        """Initialize the DocumentChunk model.

        Args:
            mongo_db: The MongoDB database async instance.
        """
        super().__init__(mongo_db)
        self.collection = self.mongo_db[CollectionNames.CHUNKS.value]

    async def insert_chunk(self, chunk: DocumentChunk) -> DocumentChunk:
        """Insert a new document chunk into the database.

        Args:
            chunk: The document chunk to insert.

        Returns:
            The inserted document chunk with the assigned object_id.
        """
        record = await self.collection.insert_one(
            chunk.model_dump(exclude={"object_id"})
        )
        chunk.object_id = record.inserted_id
        return chunk

    async def insert_many_chunks(
        self, chunks: List[DocumentChunk]
    ) -> List[DocumentChunk]:
        """Insert multiple document chunks into the database.

        Args:
            chunks: The list of document chunks to insert.

        Returns:
            The list of inserted document chunks with assigned object_ids.
        """
        deleted_count = await self.collection.delete_many(
            {"project_id": chunks[0].project_id, "file_id": chunks[0].file_id}
        )
        if deleted_count.deleted_count > 0:
            self.logger.info(
                "Deleted %d existing chunks for project %s, file %s",
                deleted_count.deleted_count,
                chunks[0].project_id,
                chunks[0].file_id,
            )
        chunk_operations = [
            InsertOne(chunk.model_dump(exclude={"object_id"})) for chunk in chunks
        ]
        records = await self.collection.bulk_write(chunk_operations)
        if records is not None and records.upserted_ids is not None:
            for chunk, object_id in zip(chunks, records.upserted_ids.values()):
                chunk.object_id = object_id
        return chunks

    async def get_chunks_by_project_file(
        self, project_id: str, file_id: str, skip: int, limit: int
    ) -> List[DocumentChunk]:
        """Get a list of document chunks for a specific project and file.

        Args:
            project_id: The ID of the project.
            file_id: The ID of the file.

        Returns:
            A list of document chunks.
        """
        cursor = (
            self.collection.find({"project_id": project_id, "file_id": file_id})
            .sort("chunk_order", 1)
            .skip(skip)
            .limit(limit)
        )
        chunks = await cursor.to_list(length=None)
        return [DocumentChunk(**chunk) for chunk in chunks]

    async def delete_chunks_by_project_file(self, project_id: str, file_id: str) -> int:
        """Delete document chunks for a specific project and file.

        Args:
            project_id: The ID of the project.
            file_id: The ID of the file.

        Returns:
            The number of deleted chunks.
        """
        result = await self.collection.delete_many(
            {"project_id": project_id, "file_id": file_id}
        )
        return result.deleted_count

    async def delete_chunks_by_project(self, project_id: str) -> int:
        """Delete document chunks for a specific project.

        Args:
            project_id: The ID of the project.

        Returns:
            The number of deleted chunks.
        """
        result = await self.collection.delete_many({"project_id": project_id})
        return result.deleted_count
