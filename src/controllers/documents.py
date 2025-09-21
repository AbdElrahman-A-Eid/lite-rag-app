"""
Controller for document-related operations.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import Settings
from controllers.base import BaseController
from models.enums import DocumentFileType


class DocumentController(BaseController):
    """
    Controller for document-related operations.
    """

    def __init__(self, settings: Settings, project_id: UUID):
        """Initialize the DocumentController.

        Args:
            settings (Settings): The application settings.
            project_id (UUID): The ID of the project.
        """
        super().__init__(settings)
        self.files_dir = self.settings.files_dir
        self.project_id = str(project_id)
        self.project_dir = self.files_dir / self.project_id

    def _get_file_type(self, file_path: Path) -> str:
        """Get the file type based on the file extension.

        Args:
            file_path (Path): The path to the file.

        Returns:
            str: The file type.
        """
        return file_path.suffix.lower()

    def _get_loader(self, file_path: Path) -> Optional[BaseLoader]:
        """Get the document loader based on the file type.

        Args:
            file_path (Path): The path to the file.

        Returns:
            BaseLoader: The document loader for the specified file type.
        """
        file_type = self._get_file_type(file_path)
        if file_type == DocumentFileType.PDF.value:
            return PyMuPDFLoader(file_path, mode="page")
        elif file_type == DocumentFileType.TXT.value:
            return TextLoader(file_path, encoding="utf8")
        else:
            self.logger.warning(
                "Unsupported file type: %s (at %s)", file_type, file_path
            )
            return None

    async def _load_file(
        self, file_path: Path
    ) -> Optional[Tuple[List[str], List[Dict]]]:
        """Load the documents from the file.

        Args:
            file_path (Path): The path to the file.

        Returns:
            Optional[Tuple[List[str], List[Dict]]]: The list of loaded document text contents
            and their metadata, or None if loading failed.
        """
        loader = self._get_loader(file_path)
        if loader:
            try:
                documents = await loader.aload()
                if documents:
                    file_texts = [
                        self._cleanup_text(doc.page_content) for doc in documents
                    ]
                    file_metadatas = [doc.metadata for doc in documents]
                    return file_texts, file_metadatas
            except Exception as e:
                self.logger.error(
                    "Failed to load file at %s: %s", file_path, str(e), exc_info=True
                )
        return None

    def _cleanup_text(self, text: str) -> str:
        """Clean up the text by removing problematic characters.

        Args:
            text (str): The text to clean up.

        Returns:
            str: The cleaned-up text.
        """
        return re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", text)

    async def process_file(
        self, file_id: str, chunk_size: int, chunk_overlap: int
    ) -> Optional[List[Document]]:
        """Process the file and extract chunk documents.

        Args:
            file_id (str): The ID of the file.

        Returns:
            Optional[List[Document]]: The list of processed chunk documents
            if it was loaded successfully.
        """
        file_path = self.project_dir / file_id
        file_documents = await self._load_file(file_path)
        if file_documents is not None:
            file_texts, file_metadatas = file_documents
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size, chunk_overlap=chunk_overlap
            )
            chunks = splitter.create_documents(
                texts=file_texts, metadatas=file_metadatas
            )
            return chunks
        return None
