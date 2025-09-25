"""
API routes for document-related operations.
"""

from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from controllers import DocumentController, FileController, VectorController
from dependencies import get_session
from models.asset import AssetModel
from models.chunk import DocumentChunk, DocumentChunkModel
from models.enums import ResponseSignals
from models.project import ProjectModel
from routes.schemas import (
    BatchDocumentsResponse,
    ChunkListResponse,
    DocumentProcessingRequest,
    ProjectDocumentsRefreshRequest,
)

document_router = APIRouter(
    prefix="/api/v1/p/{project_id}/documents", tags=["documents", "v1"]
)


@document_router.post(
    "/process",
    response_model=ChunkListResponse,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def process_document(
    request: Request,
    project_id: UUID,
    processing_request: DocumentProcessingRequest,
    db_session: AsyncSession = Depends(get_session),
):
    """
    Processes a document and returns the processing result.

    Args:
        project_id (UUID): The project ID.
        processing_request (DocumentProcessingRequest): The document processing request.

    Returns:
        ChunkListResponse: The list of processed document chunks.
    """
    settings = request.app.state.settings
    project_model = ProjectModel(db_session)
    project_record = await project_model.get_project_by_id(project_id)
    if project_record is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
        )

    file_controller = FileController(settings)
    if not file_controller.file_exists(project_id, processing_request.file_id):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.FILE_NOT_FOUND.value},
        )

    asset_model = AssetModel(db_session)
    asset_record = await asset_model.get_asset_by_name(
        project_record.id, processing_request.file_id
    )
    if asset_record is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.ASSET_NOT_FOUND.value},
        )

    if processing_request.replace_existing:
        document_chunk_model = DocumentChunkModel(db_session)
        await document_chunk_model.delete_chunks_by_project_asset(
            project_id=project_record.id, asset_id=asset_record.id
        )

    document_controller = DocumentController(settings=settings, project_id=project_id)
    chunks = await document_controller.process_file(
        processing_request.file_id,
        processing_request.chunk_size,
        processing_request.chunk_overlap,
    )
    if not chunks:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"msg": ResponseSignals.DOCUMENT_PROCESSING_FAILED.value},
        )

    chunks_objects = [
        DocumentChunk(
            project_id=project_record.id,
            asset_id=asset_record.id,
            content=chunk.page_content,
            metadata_=chunk.metadata,
            order=idx_,
        )
        for idx_, chunk in enumerate(chunks)
    ]
    document_chunk_model = DocumentChunkModel(db_session)
    records = await document_chunk_model.insert_many_chunks(chunks_objects)
    if not records:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"msg": ResponseSignals.DOCUMENT_PROCESSING_FAILED.value},
        )

    document_controller.logger.info(
        "Document processed successfully: %s (%d chunks)",
        str(asset_record.id),
        len(records),
    )

    return {
        "values": records,
        "count": len(records),
        "total": len(records),
    }


@document_router.post(
    "/refresh",
    response_model=BatchDocumentsResponse,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def refresh_project_documents(
    request: Request,
    project_id: UUID,
    refresh_request: ProjectDocumentsRefreshRequest,
    db_session: AsyncSession = Depends(get_session),
):
    """
    Refreshes all documents for a specific project by removing old chunks and reprocessing them.

    Args:
        project_id (UUID): The project ID.
        refresh_request (ProjectDocumentsRefreshRequest): The document refresh request.

    Returns:
        BatchDocumentsResponse: The batch document processing response.
    """
    settings = request.app.state.settings
    project_model = ProjectModel(db_session)
    project_record = await project_model.get_project_by_id(project_id)
    if project_record is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
        )

    assets = project_record.assets
    if not assets:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.ASSET_NOT_FOUND.value},
        )
    assets_info = [(asset.id, asset.name) for asset in assets]

    file_controller = FileController(settings)
    document_controller = DocumentController(
        settings=settings, project_id=project_record.id
    )

    document_chunk_model = DocumentChunkModel(db_session)
    if refresh_request.replace_existing:
        vector_controller = VectorController(
            settings=settings,
            vectordb_client=request.app.state.vectordb_client,
            embedding_model=request.app.state.embedding_llm,
        )
        await vector_controller.delete_index(project_record.id)
        deleted_count = await document_chunk_model.delete_chunks_by_project(
            project_record.id
        )
        document_chunk_model.logger.info(
            "Deleted existing chunks for project '%s': %d",
            str(project_record.id),
            deleted_count,
        )
    results: Dict[str, Any] = {}
    for asset_id, asset_name in assets_info:
        if not file_controller.file_exists(project_id, asset_name):
            results[asset_name] = {"msg": ResponseSignals.FILE_NOT_FOUND.value}
            continue

        chunks = await document_controller.process_file(
            asset_name,
            chunk_size=refresh_request.chunk_size,
            chunk_overlap=refresh_request.chunk_overlap,
        )
        if not chunks:
            results[asset_name] = {
                "msg": ResponseSignals.DOCUMENT_PROCESSING_FAILED.value
            }
            continue

        chunks_objects = [
            DocumentChunk(
                project_id=project_record.id,
                asset_id=asset_id,
                content=chunk.page_content,
                metadata_=chunk.metadata,
                order=idx_,
            )
            for idx_, chunk in enumerate(chunks)
        ]
        records = await document_chunk_model.insert_many_chunks(chunks_objects)
        if not records:
            results[asset_name] = {
                "msg": ResponseSignals.DOCUMENT_PROCESSING_FAILED.value
            }
            continue

        document_controller.logger.info(
            "Document processed successfully: %s (%d chunks)",
            str(asset_id),
            len(records),
        )

        results[asset_name] = {
            "values": records,
            "count": len(records),
            "total": len(records),
        }

    return {
        "values": results,
        "count": sum(
            1 for v in results.values() if isinstance(v, dict) and "values" in v
        ),
        "total": len(results),
    }


@document_router.get(
    "/{file_id}/list",
    response_model=ChunkListResponse,
    status_code=status.HTTP_200_OK,
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def list_document_chunks(
    project_id: UUID,
    file_id: str,
    skip: int = 0,
    limit: int = 100,
    db_session: AsyncSession = Depends(get_session),
):
    """
    Lists all processed document chunks for a specific project.

    Args:
        project_id (UUID): The project ID.
        file_id (str): The file ID of the asset.
        skip (int): Number of chunks to skip for pagination.
        limit (int): Maximum number of chunks to return.

    Returns:
        ChunkListResponse: The list of document chunks.
    """
    if limit > 300:
        limit = 300

    project_model = ProjectModel(db_session)
    project_record = await project_model.get_project_by_id(project_id)
    if project_record is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
        )

    asset_model = AssetModel(db_session)
    asset_record = await asset_model.get_asset_by_name(project_record.id, file_id)
    if asset_record is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.ASSET_NOT_FOUND.value},
        )

    # Ensure deterministic ordering by chunk order
    chunks = asset_record.document_chunks
    page = chunks[skip : skip + limit]

    if not page:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.CHUNK_NOT_FOUND.value},
        )

    return {
        "values": page,
        "count": len(page),
        "total": len(chunks),
    }


@document_router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document_chunks(
    project_id: UUID,
    file_id: str,
    db_session: AsyncSession = Depends(get_session),
):
    """
    Deletes all processed document chunks for a specific project.

    Args:
        project_id (UUID): The project ID.
        file_id (str): The file ID of the asset.
    """
    project_model = ProjectModel(db_session)
    project_record = await project_model.get_project_by_id(project_id)
    if project_record is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
        )

    asset_model = AssetModel(db_session)
    asset_record = await asset_model.get_asset_by_name(project_record.id, file_id)
    if asset_record is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.ASSET_NOT_FOUND.value},
        )

    chunk_model = DocumentChunkModel(db_session)
    deleted_count = await chunk_model.delete_chunks_by_project_asset(
        project_id=project_record.id, asset_id=asset_record.id
    )
    if deleted_count == 0:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.CHUNK_NOT_FOUND.value},
        )
    return
