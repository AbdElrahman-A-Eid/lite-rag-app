"""
API routes for vector-related operations.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from controllers import VectorController
from dependencies import get_session
from models.chunk import DocumentChunkModel
from models.enums import ResponseSignals
from models.project import ProjectModel
from routes.schemas import (
    VectorIndexRequest,
    VectorIndexResponse,
    VectorQueryRequest,
    VectorQueryResponse,
)

vector_router = APIRouter(
    prefix="/api/v1/p/{project_id}/vectors", tags=["vectors", "v1"]
)


@vector_router.post("/index", response_model=VectorIndexResponse)
async def index_vectors(
    request: Request,
    project_id: UUID,
    index_request: VectorIndexRequest,
    db_session: AsyncSession = Depends(get_session),
):
    """Index vectors for a specific project.

    Args:
        request (Request): The FastAPI request object.
        project_id (UUID): The ID of the project to index vectors for.
        index_request (VectorIndexRequest): The request object containing indexing parameters.
        db_session (AsyncSession): The SQLAlchemy database async session.

    Returns:
        VectorIndexResponse: The response object containing the result of the indexing operation.
    """
    settings = request.app.state.settings
    project_model = ProjectModel(db_session)
    project_record = await project_model.get_project_by_id(project_id)
    if project_record is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
        )

    document_chunk_model = DocumentChunkModel(db_session)
    chunk_count = await document_chunk_model.count_chunks_by_project(project_record.id)
    if chunk_count == 0:
        return JSONResponse(
            content={"msg": ResponseSignals.NO_DOCUMENTS_FOUND.value},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    chunks = await document_chunk_model.get_chunks_by_project(
        project_record.id, skip=0, limit=chunk_count
    )

    vector_controller = VectorController(
        settings=settings,
        vectordb_client=request.app.state.vectordb_client,
        embedding_model=request.app.state.embedding_llm,
    )
    inserted = await vector_controller.index_vectors(
        project_id=project_id, chunks=list(chunks), reset=index_request.reset
    )
    if not inserted:
        return JSONResponse(
            content={"msg": ResponseSignals.VECTOR_INDEXING_FAILED.value},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return JSONResponse(
        content={},
        status_code=status.HTTP_201_CREATED,
    )


@vector_router.post("/query", response_model=VectorQueryResponse)
async def query_vectors(
    request: Request,
    project_id: UUID,
    query_request: VectorQueryRequest,
    db_session: AsyncSession = Depends(get_session),
):
    """Query vectors for a specific project.

    Args:
        request (Request): The FastAPI request object.
        project_id (UUID): The ID of the project to query vectors for.
        query_request (VectorQueryRequest): The request object containing query parameters.
        db_session (AsyncSession): The SQLAlchemy database async session.

    Returns:
        VectorQueryResponse: The response object containing the result of the query operation.
    """
    settings = request.app.state.settings
    project_model = ProjectModel(db_session)
    project_record = await project_model.get_project_by_id(project_id)
    if project_record is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
        )

    vector_controller = VectorController(
        settings=settings,
        vectordb_client=request.app.state.vectordb_client,
        embedding_model=request.app.state.embedding_llm,
    )
    index_info = await vector_controller.get_index_info(project_id=project_id)
    if index_info is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.VECTOR_INDEX_NOT_FOUND.value},
        )
    if "points_count" not in index_info or index_info["points_count"] < 1:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.VECTOR_INDEX_EMPTY.value},
        )

    relevant_vectors = await vector_controller.query_vectors(
        project_id=project_id,
        query=query_request.query,
        top_k=query_request.top_k,
        threshold=query_request.threshold,
    )

    return JSONResponse(
        content={
            "results": [vector.model_dump() for vector in relevant_vectors],
            "count": len(relevant_vectors),
        },
        status_code=status.HTTP_200_OK,
    )
