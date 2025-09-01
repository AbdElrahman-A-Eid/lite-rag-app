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

    def delete_project_folder(self, project_id: str) -> None:
        """Deletes a project directory including all its files.

        Args:
            project_id (str): The ID of the project to delete.
        """
        project_dir = self.files_dir / project_id
        files_count = 0
        if project_dir.is_dir():
            for item in project_dir.iterdir():
                if item.is_file():
                    item.unlink()
                    files_count += 1
                elif item.is_dir():
                    for sub_item in item.iterdir():
                        if sub_item.is_file():
                            sub_item.unlink()
                            files_count += 1
                    item.rmdir()
            project_dir.rmdir()
            self.logger.info(
                "Deleted project directory: %s (%d files)", project_id, files_count
            )
        else:
            self.logger.warning("Project directory not found: %s", project_id)

    def delete_file(self, project_id: str, file_name: str) -> bool:
        """Deletes a specific file from a project directory.

        Args:
            project_id (str): The ID of the project.
            file_name (str): The name of the file to delete.

        Returns:
            bool: True if the file was deleted successfully, False otherwise.
        """
        project_dir = self.files_dir / project_id
        file_path = project_dir / file_name
        if file_path.is_file():
            file_path.unlink()
            self.logger.info("Deleted file: %s", file_path)
            return True
        else:
            self.logger.warning("File not found: %s", file_path)
            return False

    def delete_project_files(self, project_id: str, file_names: List[str]) -> bool:
        """Deletes multiple files from a project directory.

        Args:
            project_id (str): The ID of the project.
            file_names (List[str]): A list of file names to delete.

        Returns:
            bool: True if all files were deleted successfully, False otherwise.
        """
        return all(self.delete_file(project_id, file_name) for file_name in file_names)
