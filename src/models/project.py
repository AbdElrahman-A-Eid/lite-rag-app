"""
Model definitions for projects.
"""

from typing import Optional, List, Dict, Any
from pymongo import IndexModel
from pymongo.asynchronous.database import AsyncDatabase
from bson.objectid import ObjectId
from pydantic import BaseModel, Field, model_validator, ConfigDict
from models.base import BaseDataModel, MongoObjectId
from models.enums import CollectionNames
from models.asset import AssetModel
from controllers import ProjectController


class Project(BaseModel):
    """Database Schema for the Project Entity"""

    object_id: Optional[MongoObjectId] = Field(default=None, alias="_id")
    id: str
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(
        default="No description provided.", max_length=500
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def fill_default_name(self):
        """Fill default name if not provided."""
        if not self.name:
            self.name = f"Project-{self.id}"
        return self

    @staticmethod
    def get_index_fields() -> List[Dict[str, Any]]:
        """Get the index fields for the DocumentChunk model.

        Returns:
            A list of index field names.
        """
        return [
            {
                "keys": [
                    ("id", 1),
                ],
                "name": "id_index_1",
                "unique": True,
            },
        ]


class ProjectModel(BaseDataModel):
    """
    Model for the Project entity.
    """

    def __init__(self, mongo_db: AsyncDatabase):
        """Initialize the Project model.

        Args:
            mongo_db (AsyncDatabase): The MongoDB database async instance.
        """
        super().__init__(mongo_db)
        self.collection = self.mongo_db[CollectionNames.PROJECTS.value]

    @classmethod
    async def create_instance(cls, mongo_db: AsyncDatabase) -> "ProjectModel":
        """Create a new instance of the Project model.

        Args:
            mongo_db (AsyncDatabase): The MongoDB database async instance.

        Returns:
            ProjectModel: The new instance of the Project model.
        """
        instance = cls(mongo_db)
        await instance.create_index_fields()
        return instance

    async def create_index_fields(self):
        """Create the index fields for the Project model."""
        self.logger.info("Checking index fields for Project model...")
        index_fields = Project.get_index_fields()
        index_info = await self.collection.index_information()
        if any(not index_info.get(index_field["name"]) for index_field in index_fields):
            await self.collection.create_indexes(
                [IndexModel(**index_field) for index_field in index_fields]
            )
            self.logger.info(
                "Created %d index fields for Project model.", len(index_fields)
            )

    async def insert_project(self, project: Project) -> Project:
        """Insert a new project into the database.

        Args:
            project (Project): The project to insert.

        Returns:
            Project: The inserted project with the assigned object_id.
        """
        record = await self.collection.insert_one(
            project.model_dump(exclude={"object_id"})
        )
        project.object_id = record.inserted_id
        return project

    async def get_projects(self, skip: int = 0, limit: int = 10) -> List[Project]:
        """Get a list of projects from the database.

        Args:
            skip (int, optional): The number of projects to skip. Defaults to 0.
            limit (int, optional): The maximum number of projects to return. Defaults to 10.

        Returns:
            List[Project]: A list of projects.
        """
        cursor = self.collection.find().skip(skip).limit(limit)
        projects = await cursor.to_list(length=limit)
        return [Project(**project) for project in projects]

    async def get_project_by_id(self, project_id: str) -> Optional[Project]:
        """Get a project by its ID from the database.

        Args:
            project_id (str): The ID of the project.

        Returns:
            Optional[Project]: The project if found, None otherwise.
        """
        project_data = await self.collection.find_one({"id": project_id})
        if project_data:
            return Project(**project_data)
        return None

    async def delete_project(self, project_id: str) -> bool:
        """Delete a project by its ID from the database and its associated data.

        Args:
            project_id (str): The ID of the project.

        Returns:
            bool: True if the project was deleted, False otherwise.
        """
        project = await ProjectModel(self.mongo_db).collection.find_one(
            {"id": project_id}
        )
        project_object_id: Optional[ObjectId] = project["_id"] if project else None
        if not project_object_id:
            return False
        asset_model = await AssetModel.create_instance(self.mongo_db)
        await asset_model.delete_assets_by_project(project_object_id)
        result = await self.collection.delete_one({"_id": project_object_id})
        if result.deleted_count != 0:
            ProjectController().delete_project_folder(project_id)
            return True
        return False

    async def count_projects(self) -> int:
        """Count the total number of projects in the database.

        Returns:
            int: The total number of projects.
        """
        return await self.collection.count_documents({})
