"""
API routes for document-related operations.
"""

from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from pymongo.asynchronous.database import AsyncDatabase
from controllers import DocumentController
from routes.schemas import (
    DocumentProcessingRequest,
    DocumentProcessingResponse,
    DocumentListResponse,
    ProjectDocumentsRefreshRequest,
    ProjectDocumentsRefreshResponse,
    ChunkResponse,
)
from models import DocumentChunk, DocumentChunkModel, ProjectModel, AssetModel
from models.enums import ResponseSignals
from dependencies import get_db

document_router = APIRouter(
    prefix="/api/v1/p/{project_id}/documents", tags=["documents", "v1"]
)


@document_router.post("/process", response_model=DocumentProcessingResponse)
async def process_document(
    project_id: str,
    request: DocumentProcessingRequest,
    mongo_db: AsyncDatabase = Depends(get_db),
):
    """Processes a document and returns the processing result.

    Args:
        project_id (str): The ID of the project.
        request (DocumentProcessingRequest): The request containing document processing parameters.

    Returns:
        JSONResponse: The response containing the processing result.
    """
    project_model = await ProjectModel.create_instance(mongo_db=mongo_db)
    project_record = await project_model.get_project_by_id(project_id)
    if project_record is None or project_record.object_id is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
        )
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
    asset_model = await AssetModel.create_instance(mongo_db=mongo_db)
    asset_object_id = await asset_model.get_asset_object_id(
        project_record.object_id, request.file_id
    )
    if asset_object_id is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.ASSET_NOT_FOUND.value},
        )
    chunks_objects = [
        DocumentChunk(
            **chunk.model_dump(),
            project_id=project_record.object_id,
            asset_id=asset_object_id,
            chunk_order=idx_
        )
        for idx_, chunk in enumerate(chunks)
    ]
    document_chunk_model = await DocumentChunkModel.create_instance(mongo_db=mongo_db)
    records = await document_chunk_model.insert_many_chunks(chunks_objects)
    if not records:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "file_id": request.file_id,
                "msg": ResponseSignals.DOCUMENT_PROCESSING_FAILED.value,
            },
        )

    document_controller.logger.info(
        "Document processed successfully: %s (%d chunks)",
        str(asset_object_id),
        len(records),
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "project_id": project_id,
            "file_id": request.file_id,
            "chunks": [
                {**chunk.model_dump(exclude={"object_id", "asset_id", "project_id"})}
                for chunk in records
            ],
            "count": len(records),
        },
    )


@document_router.post("/refresh", response_model=ProjectDocumentsRefreshResponse)
async def refresh_project_documents(
    project_id: str,
    request: ProjectDocumentsRefreshRequest,
    mongo_db: AsyncDatabase = Depends(get_db),
):
    """Refreshes all documents for a specific project by removing old chunks and reprocessing them.

    Args:
        project_id (str): The ID of the project.

    Returns:
        JSONResponse: The response containing the list of document processing results.
    """
    project_model = await ProjectModel.create_instance(mongo_db=mongo_db)
    project_record = await project_model.get_project_by_id(project_id)
    if project_record is None or project_record.object_id is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
        )
    asset_model = await AssetModel.create_instance(mongo_db=mongo_db)
    assets = await asset_model.get_project_assets(project_record.object_id)
    if not assets:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.ASSET_NOT_FOUND.value},
        )
    document_controller = DocumentController(project_id=project_id)
    document_chunk_model = await DocumentChunkModel.create_instance(mongo_db=mongo_db)
    await document_chunk_model.delete_chunks_by_project(project_record.object_id)
    processing_results = []
    for asset in assets:
        if asset.object_id is None:
            processing_results.append(
                DocumentProcessingResponse(
                    project_id=project_id,
                    file_id=asset.name,
                    msg=ResponseSignals.ASSET_NOT_FOUND.value,
                ).model_dump(mode="json", exclude_defaults=True)
            )
            continue
        chunks = document_controller.process_file(
            asset.name,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
        )
        if not chunks:
            processing_results.append(
                DocumentProcessingResponse(
                    project_id=project_id,
                    file_id=asset.name,
                    msg=ResponseSignals.DOCUMENT_PROCESSING_FAILED.value,
                ).model_dump(mode="json", exclude_defaults=True)
            )
            continue
        chunks_objects = [
            DocumentChunk(
                **chunk.model_dump(),
                project_id=project_record.object_id,
                asset_id=asset.object_id,
                chunk_order=idx_
            )
            for idx_, chunk in enumerate(chunks)
        ]
        records = await document_chunk_model.insert_many_chunks(chunks_objects)
        if not records:
            processing_results.append(
                DocumentProcessingResponse(
                    project_id=project_id,
                    file_id=asset.name,
                    msg=ResponseSignals.DOCUMENT_PROCESSING_FAILED.value,
                ).model_dump(mode="json", exclude_defaults=True)
            )
            continue
        document_controller.logger.info(
            "Document processed successfully: %s (%d chunks)",
            str(asset.object_id),
            len(records),
        )
        processing_results.append(
            DocumentProcessingResponse(
                project_id=project_id,
                file_id=asset.name,
                chunks=[
                    ChunkResponse(
                        **chunk.model_dump(
                            exclude={"object_id", "asset_id", "project_id"}
                        )
                    )
                    for chunk in records
                ],
                count=len(records),
            ).model_dump(mode="json", exclude_defaults=True)
        )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "project_id": project_id,
            "assets": processing_results,
        },
    )


@document_router.get("/{file_id}/list", response_model=DocumentListResponse)
async def list_document_chunks(
    project_id: str,
    file_id: str,
    skip: int = 0,
    limit: int = 100,
    mongo_db: AsyncDatabase = Depends(get_db),
):
    """Lists all processed document chunks for a specific project.

    Args:
        project_id (str): The ID of the project.

    Returns:
        JSONResponse: The response containing the list of processed document chunks.
    """
    if limit > 300:
        limit = 300
    project_model = await ProjectModel.create_instance(mongo_db=mongo_db)
    project_record = await project_model.get_project_by_id(project_id)
    if project_record is None or project_record.object_id is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
        )
    asset_model = await AssetModel.create_instance(mongo_db=mongo_db)
    asset_object_id = await asset_model.get_asset_object_id(
        project_record.object_id, file_id
    )
    if asset_object_id is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.ASSET_NOT_FOUND.value},
        )
    chunk_model = await DocumentChunkModel.create_instance(mongo_db=mongo_db)
    chunks = await chunk_model.get_chunks_by_project_asset(
        project_object_id=project_record.object_id,
        asset_object_id=asset_object_id,
        skip=skip,
        limit=limit,
    )
    if not chunks:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.CHUNK_NOT_FOUND.value},
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "project_id": project_id,
            "file_id": file_id,
            "chunks": [
                {**chunk.model_dump(exclude={"object_id", "asset_id", "project_id"})}
                for chunk in chunks
            ],
            "count": len(chunks),
            "total": await chunk_model.count_chunks_by_project_asset(
                project_record.object_id, asset_object_id
            ),
        },
    )


@document_router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document_chunks(
    project_id: str,
    file_id: str,
    mongo_db: AsyncDatabase = Depends(get_db),
):
    """Deletes all processed document chunks for a specific project.

    Args:
        project_id (str): The ID of the project.
        file_id (str): The ID of the file.

    Returns:
        JSONResponse: The response indicating the result of the deletion.
    """
    project_model = await ProjectModel.create_instance(mongo_db=mongo_db)
    project_record = await project_model.get_project_by_id(project_id)
    if project_record is None or project_record.object_id is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
        )
    asset_model = await AssetModel.create_instance(mongo_db=mongo_db)
    asset_object_id = await asset_model.get_asset_object_id(
        project_record.object_id, file_id
    )
    if asset_object_id is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.ASSET_NOT_FOUND.value},
        )
    chunk_model = await DocumentChunkModel.create_instance(mongo_db=mongo_db)
    deleted_count = await chunk_model.delete_chunks_by_project_asset(
        project_object_id=project_record.object_id, asset_object_id=asset_object_id
    )
    if deleted_count == 0:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.CHUNK_NOT_FOUND.value},
        )
    return
