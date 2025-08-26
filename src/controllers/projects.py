"""
Controllers for project management operations.
"""

from uuid import uuid4
from typing import List
from controllers.base import BaseController


class ProjectController(BaseController):
    """
    Controller for managing projects.
    """

    def __init__(self):
        super().__init__()
        self.files_dir = self.settings.files_dir
        self.files_dir.mkdir(parents=True, exist_ok=True)

    def create_new_project(self) -> str:
        """Creates a new project directory.

        Returns:
            str: The ID of the newly created project or an error message.
        """
        project_id = str(uuid4())
        project_dir = self.files_dir / project_id
        while project_dir.exists():
            project_id = str(uuid4())
            project_dir = self.files_dir / project_id
        try:
            project_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info("Created new project with ID: %s", project_id)
            return project_id
        except Exception as e:
            self.logger.error(
                "Failed to create project directory: %s", str(e), exc_info=True
            )
            return ""

    def list_projects(self) -> List[str]:
        """Lists all existing project directories.

        Returns:
            List[str]: A list of project IDs.
        """
        return [d.name for d in self.files_dir.iterdir() if d.is_dir()]

    def validate_project(self, project_id: str) -> bool:
        """Validates the existence of a project directory.

        Args:
            project_id (str): The ID of the project to validate.

        Returns:
            bool: True if the project exists, False otherwise.
        """
        project_dir = self.files_dir / project_id
        return project_dir.is_dir()
