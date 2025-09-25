"""
Enumerations for response signals.
"""

from enum import Enum


class ResponseSignals(str, Enum):
    """Enumeration for response signals."""

    FILE_UPLOAD_FAILED = "File Upload Failed"
    NO_FILE_PROVIDED = "No File Provided"
    UNSUPPORTED_FILE_TYPE = "Unsupported File Type"
    FILE_TOO_LARGE = "File Too Large"
    FILE_VALIDATION_ERROR = "File Validation Error"
    DOCUMENT_PROCESSING_FAILED = "Document Processing Failed"
    PROJECT_CREATION_FAILED = "Project Creation Failed"
    CHUNK_NOT_FOUND = "No Chunks Found for the specified Project or File"
    PROJECT_NOT_FOUND = "Project Not Found"
    ASSET_NOT_FOUND = "Asset Not Found"
    NO_DOCUMENTS_FOUND = "No Documents Found"
    VECTOR_INDEXING_FAILED = "Vector Indexing Failed"
    VECTOR_INDEX_NOT_FOUND = "Vector Index Not Found"
    VECTOR_INDEX_EMPTY = "Vector Index is Empty"
    RAG_GENERATION_FAILED = "RAG Generation Failed"
    FILE_NOT_FOUND = "File Not Found"
    ASSET_DELETION_FAILED = "Asset Deletion Failed"
