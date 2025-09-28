"""
Controllers for asset management operations.
"""

import re
from typing import Tuple
from uuid import uuid4

from fastapi import UploadFile

from config import Settings
from controllers.base import BaseController
from models.enums import ResponseSignals


class FileController(BaseController):
    """
    Controller for managing file uploads and processing.
    """

    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.logger.info("Initializing FileController")

    def _clean_filename(self, filename: str) -> str:
        pattern = re.compile(r"[^\w\s.-_\d]")
        filename = re.sub(r"\s+", "_", filename).lower()
        return pattern.sub("", filename)

    def generate_unique_filename(self, filename: str) -> str:
        """Generate a unique filename by appending a UUID to the cleaned original filename."""
        unique_id = str(uuid4())[:8]
        clean_filename = self._clean_filename(filename)
        return f"{unique_id}_{clean_filename}"

    def get_file_size_mb(self, file: UploadFile) -> float:
        """Get the size of the uploaded file in Megabytes.

        Args:
            file (UploadFile): The uploaded file.

        Returns:
            float: The size of the file in Megabytes.
        """
        if hasattr(file, "size") and file.size is not None:
            file_size_mb = file.size / (1024 * 1024)
        else:
            current_position = file.file.tell()
            file.file.seek(0, 2)
            file_size_mb = file.file.tell() / (1024 * 1024)
            file.file.seek(current_position)
        return file_size_mb

    def validate_file(self, file: UploadFile) -> Tuple[bool, str]:
        """Validates the uploaded file against supported types and size limits.

        Args:
            file (UploadFile): The uploaded file.

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            if not file.filename:
                error_msg = ResponseSignals.NO_FILE_PROVIDED.value
                self.logger.warning(error_msg)
                return False, error_msg

            if file.content_type not in self.settings.files_supported_types:
                error_msg = ResponseSignals.UNSUPPORTED_FILE_TYPE.value
                self.logger.warning(
                    "%s: %s (Allowed Types: %s)",
                    error_msg,
                    file.content_type,
                    self.settings.files_supported_types,
                )
                return False, error_msg

            file_size_mb = self.get_file_size_mb(file)

            if file_size_mb > self.settings.files_max_size_mb:
                error_msg = ResponseSignals.FILE_TOO_LARGE.value
                self.logger.warning(
                    "%s: %s (Maximum Allowed: %s MB)",
                    error_msg,
                    file_size_mb,
                    self.settings.files_max_size_mb,
                )
                return False, error_msg

            return True, ""

        except Exception as e:
            error_msg = ResponseSignals.FILE_VALIDATION_ERROR.value
            self.logger.error("Validation error occurred: %s", str(e), exc_info=True)
            return False, error_msg
