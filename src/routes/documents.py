"""
API routes for document-related operations.
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from controllers import DocumentController
from routes.schemas import DocumentProcessingRequest, DocumentProcessingResponse
from models import ResponseSignals

document_router = APIRouter(
    prefix="/api/v1/p/{project_id}/documents", tags=["documents", "v1"]
)


@document_router.post("/process", response_model=DocumentProcessingResponse)
async def process_document(project_id: str, request: DocumentProcessingRequest):
    """Processes a document and returns the processing result.

    Args:
        project_id (str): The ID of the project.
        request (DocumentProcessingRequest): The request containing document processing parameters.

    Returns:
        JSONResponse: The response containing the processing result.
    """
    document_controller = DocumentController(project_id=project_id)
    chunks = document_controller.process_file(
        request.file_id, request.chunk_size, request.chunk_overlap
    )
    if not chunks:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "file_id": request.file_id,
                "msg": ResponseSignals.DOCUMENT_PROCESSING_FAILED.value,
            },
        )
    document_controller.logger.info(
        "Document processed successfully: %s (%d chunks)", request.file_id, len(chunks)
    )
    return {"file_id": request.file_id, "chunks": chunks, "count": len(chunks)}
