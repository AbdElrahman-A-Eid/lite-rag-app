"""
Model definition for a document chunk.
"""

from typing import Any, Dict, List, Optional

from bson.objectid import ObjectId
from pydantic import BaseModel, ConfigDict, Field
from pymongo import IndexModel, InsertOne
from pymongo.asynchronous.database import AsyncDatabase

from models.base import BaseDataModel, MongoObjectId
from models.enums import CollectionNames


class DocumentChunk(BaseModel):
    """Model definition for a document chunk."""

    object_id: Optional[MongoObjectId] = Field(default=None, alias="_id")
    project_id: MongoObjectId
    asset_id: MongoObjectId
    chunk_order: int
    page_content: str
    metadata: Dict[str, Any]

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
                    ("asset_id", 1),
                ],
                "name": "project_asset_id_index_1",
                "unique": False,
            },
        ]


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

    @classmethod
    async def create_instance(cls, mongo_db: AsyncDatabase) -> "DocumentChunkModel":
        """Create a new instance of the DocumentChunk model.

        Args:
            mongo_db (AsyncDatabase): The MongoDB database async instance.

        Returns:
            DocumentChunkModel: The new instance of the Document Chunk model.
        """
        instance = cls(mongo_db)
        await instance.create_index_fields()
        return instance

    async def create_index_fields(self):
        """Create the index fields for the Project model."""
        self.logger.info("Checking index fields for DocumentChunk model...")
        index_fields = DocumentChunk.get_index_fields()
        index_info = await self.collection.index_information()
        if any(not index_info.get(index_field["name"]) for index_field in index_fields):
            await self.collection.create_indexes(
                [IndexModel(**index_field) for index_field in index_fields]
            )
            self.logger.info(
                "Created %d index fields for DocumentChunk model.", len(index_fields)
            )

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
            {"project_id": chunks[0].project_id, "asset_id": chunks[0].asset_id}
        )
        if deleted_count.deleted_count > 0:
            self.logger.info(
                "Deleted %d existing chunks for project %s, asset %s",
                deleted_count.deleted_count,
                str(chunks[0].project_id),
                str(chunks[0].asset_id),
            )
        chunk_operations = [
            InsertOne(chunk.model_dump(exclude={"object_id"})) for chunk in chunks
        ]
        records = await self.collection.bulk_write(chunk_operations)
        if records is not None and records.upserted_ids is not None:
            for chunk, object_id in zip(chunks, records.upserted_ids.values()):
                chunk.object_id = object_id
        return chunks

    async def get_chunks_by_project_asset(
        self,
        project_object_id: ObjectId,
        asset_object_id: ObjectId,
        skip: int,
        limit: int,
    ) -> List[DocumentChunk]:
        """Get a list of document chunks for a specific project and asset.

        Args:
            project_object_id: The object ID of the project.
            asset_object_id: The object ID of the asset.

        Returns:
            A list of document chunks.
        """
        cursor = (
            self.collection.find(
                {"project_id": project_object_id, "asset_id": asset_object_id}
            )
            .sort("chunk_order", 1)
            .skip(skip)
            .limit(limit)
        )
        chunks = await cursor.to_list(length=None)
        return [DocumentChunk(**chunk) for chunk in chunks]

    async def get_chunk_by_project(
        self, project_object_id: ObjectId, skip: int, limit: int
    ) -> List[DocumentChunk]:
        """Get a list of document chunks for a specific project.

        Args:
            project_object_id: The object ID of the project.
            skip: The number of chunks to skip.
            limit: The maximum number of chunks to return.

        Returns:
            A list of document chunks.
        """
        cursor = (
            self.collection.find({"project_id": project_object_id})
            .sort([("file_id", 1), ("chunk_order", 1)])
            .skip(skip)
            .limit(limit)
        )
        chunks = await cursor.to_list(length=None)
        return [DocumentChunk(**chunk) for chunk in chunks]

    async def delete_chunks_by_project_asset(
        self, project_object_id: ObjectId, asset_object_id: ObjectId
    ) -> int:
        """Delete document chunks for a specific project and asset.

        Args:
            project_object_id: The object ID of the project.
            asset_object_id: The object ID of the asset.

        Returns:
            The number of deleted chunks.
        """
        result = await self.collection.delete_many(
            {"project_id": project_object_id, "asset_id": asset_object_id}
        )
        return result.deleted_count

    async def delete_chunks_by_project(self, project_object_id: ObjectId) -> int:
        """Delete document chunks for a specific project.

        Args:
            project_object_id: The object ID of the project.

        Returns:
            The number of deleted chunks.
        """
        result = await self.collection.delete_many({"project_id": project_object_id})
        return result.deleted_count

    async def count_chunks_by_project_asset(
        self, project_object_id: ObjectId, asset_object_id: ObjectId
    ) -> int:
        """Count document chunks for a specific project and asset.

        Args:
            project_object_id: The object ID of the project.
            asset_object_id: The object ID of the asset.

        Returns:
            The number of document chunks.
        """
        return await self.collection.count_documents(
            {"project_id": project_object_id, "asset_id": asset_object_id}
        )

    async def count_chunks_by_project(self, project_object_id: ObjectId) -> int:
        """Count document chunks for a specific project.

        Args:
            project_object_id: The object ID of the project.

        Returns:
            The number of document chunks.
        """
        return await self.collection.count_documents({"project_id": project_object_id})
