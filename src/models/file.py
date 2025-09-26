"""
Model definitions for files.
"""

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from databases.lite_rag.schemas import File
from models.base import BaseDataModel


class FileModel(BaseDataModel):
    """
    Model for the File entity.
    """

    def __init__(self, db_session: AsyncSession):
        """Initialize the File model.

        Args:
            db_session (AsyncSession): The SQLAlchemy database async session.
        """
        super().__init__(db_session)
        self.logger.info("FileModel initialized")

    async def insert_file(self, file: File) -> Optional[File]:
        """Insert a new file into the database.

        Args:
            file (File): The file to insert.

        Returns:
            Optional[File]: The file with the assigned id if successfully inserted. \
                None otherwise.
        """
        try:
            self.db_session.add(file)
            await self.db_session.flush()
            await self.db_session.refresh(file)
            return file
        except Exception as e:
            self.logger.error("Error inserting file: %s", str(e))
            return None

    async def insert_many_files(self, files: List[File]) -> List[File]:
        """Insert multiple files into the database.

        Args:
            files (List[File]): The list of files to insert.

        Returns:
            List[File]: The list of inserted files with assigned IDs.
        """
        if not files:
            return []
        try:
            self.db_session.add_all(files)
            await self.db_session.flush()
            for file in files:
                await self.db_session.refresh(file)
            return files
        except Exception as e:
            self.logger.error("Error inserting files: %s", str(e))
            return []
