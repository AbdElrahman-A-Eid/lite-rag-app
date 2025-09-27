"""
Controller for document-related operations.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from langchain_community.document_loaders import Blob
from langchain_community.document_loaders.parsers import PyMuPDFParser
from langchain_community.document_loaders.parsers.txt import TextParser
from langchain_core.document_loaders import BaseBlobParser
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
        self.logger.info("Initializing DocumentController")
        self.project_id = project_id

    def _get_file_type(self, filename: str) -> str:
        """Get the file type based on the file extension.

        Args:
            filename (str): The name of the file.

        Returns:
            str: The file type.
        """
        return Path(filename).suffix.lower()

    def _get_parser(self, filename: str) -> Optional[BaseBlobParser]:
        """Get the document parser based on the file type.

        Args:
            filename (str): The name of the file.

        Returns:
            BaseLoader: The document prser for the specified file type.
        """
        file_type = self._get_file_type(filename)
        if file_type == DocumentFileType.PDF.value:
            return PyMuPDFParser(mode="page")
        elif file_type == DocumentFileType.TXT.value:
            return TextParser()
        else:
            self.logger.warning(
                "Unsupported file type: %s (name: %s)", file_type, filename
            )
            return None

    async def _load_file(
        self, filename: str, data: bytes, content_type: str
    ) -> Optional[Tuple[List[str], List[Dict]]]:
        """Load the documents from the file.

        Args:
            filename (str): The name of the file.
            data (bytes): The file data.
            content_type (str): The content type of the file.

        Returns:
            Optional[Tuple[List[str], List[Dict]]]: The list of loaded document text contents
            and their metadata, or None if loading failed.
        """
        parser = self._get_parser(filename)
        if parser:
            try:
                blob = Blob.from_data(data=data, mime_type=content_type)
                documents = parser.lazy_parse(blob)
                file_texts = []
                file_metadatas = []
                for doc in documents:
                    file_texts.append(self._cleanup_text(doc.page_content))
                    file_metadatas.append(doc.metadata)
                if file_texts:
                    return file_texts, file_metadatas
            except Exception as e:
                self.logger.error(
                    "Failed to load file %s: %s", filename, str(e), exc_info=True
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
        self,
        filename: str,
        data: bytes,
        content_type: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> Optional[List[Document]]:
        """Process the file and extract chunk documents.

        Args:
            filename (str): The name of the file.
            data (bytes): The file data.
            content_type (str): The content type of the file.
            chunk_size (int): The size of each text chunk.
            chunk_overlap (int): The overlap between text chunks.

        Returns:
            Optional[List[Document]]: The list of processed chunk documents
            if it was loaded successfully.
        """
        file_documents = await self._load_file(
            filename=filename, data=data, content_type=content_type
        )
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
