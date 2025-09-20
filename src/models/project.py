"""
Model definitions for projects.
"""

from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import functions

from databases.lite_rag.schemas import Project
from models.base import BaseDataModel


class ProjectModel(BaseDataModel):
    """
    Model for the Project entity.
    """

    def __init__(self, db_session: AsyncSession):
        """Initialize the Project model.

        Args:
            db_session (AsyncSession): The SQLAlchemy database async session.
        """
        super().__init__(db_session)

    async def insert_project(self, project: Project) -> Optional[Project]:
        """Insert a new project into the database.

        Args:
            project (Project): The project to insert.

        Returns:
            Optional[Project]: The project with the assigned id if successfully inserted. \
                None otherwise.
        """
        try:
            async with self.db_session.begin():
                self.db_session.add(project)
            await self.db_session.refresh(project)
            return project
        except Exception as e:
            self.logger.error("Error inserting project: %s", str(e))
            return None

    async def get_projects(self, skip: int = 0, limit: int = 10) -> Sequence[Project]:
        """Get a list of projects from the database.

        Args:
            skip (int, optional): The number of projects to skip. Defaults to 0.
            limit (int, optional): The maximum number of projects to return. Defaults to 10.

        Returns:
            Sequence[Project]: A list of projects.
        """
        async with self.db_session.begin():
            result = await self.db_session.execute(
                select(Project).offset(skip).limit(limit)
            )
            projects = result.scalars().all()
        return projects

    async def get_project_by_id(self, project_id: UUID) -> Optional[Project]:
        """Get a project by its ID from the database.

        Args:
            project_id (UUID): The ID of the project.

        Returns:
            Optional[Project]: The project with the specified ID, or None if not found.
        """
        async with self.db_session.begin():
            result = await self.db_session.execute(
                select(Project).where(Project.id == project_id)
            )
            project = result.scalar_one_or_none()
        return project

    async def delete_project(self, project_id: UUID) -> bool:
        """Delete a project by its ID from the database and its associated data.

        Args:
            project_id (UUID): The ID of the project.

        Returns:
            bool: True if the project was deleted, False otherwise.
        """
        project = await self.get_project_by_id(project_id)
        if not project:
            return False
        async with self.db_session.begin():
            await self.db_session.delete(project)
        return True

    async def count_projects(self) -> int:
        """Count the total number of projects in the database.

        Returns:
            int: The total number of projects.
        """
        async with self.db_session.begin():
            result = await self.db_session.execute(select(functions.count(Project.id)))
            total = result.scalar_one()
        return total
