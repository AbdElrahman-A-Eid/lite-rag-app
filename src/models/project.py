"""
Model definitions for projects.
"""

from typing import Optional, List
from bson.objectid import ObjectId
from pymongo.asynchronous.database import AsyncDatabase
from pydantic import BaseModel, Field, model_validator, ConfigDict
from models.base import BaseDataModel
from models.enums import CollectionNames


class Project(BaseModel):
    """Database Schema for the Project Entity"""

    object_id: Optional[ObjectId] = Field(default=None, alias="_id")
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
