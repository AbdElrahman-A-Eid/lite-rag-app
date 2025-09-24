"""
API routes for RAG-related operations.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from controllers.rag import RAGController
from controllers.vectors import VectorController
from dependencies import get_session
from llm.controllers.templates import TemplateController
from models.enums.responses import ResponseSignals
from models.project import ProjectModel
from routes.schemas.rag import RAGQueryRequest, RAGQueryResponse

rag_router = APIRouter(prefix="/api/v1/p/{project_id}/rag", tags=["rag", "v1"])


@rag_router.post("/generate", response_model=RAGQueryResponse)
async def generate_with_rag(
    request: Request,
    project_id: UUID,
    rag_request: RAGQueryRequest,
    db_session: AsyncSession = Depends(get_session),
):
    """Generate a response using RAG.

    Args:
        request (Request): The incoming request.
        project_id (UUID): The project ID.
        rag_request (RAGQueryRequest): The RAG query request.

    Returns:
        RAGQueryResponse: The RAG query response.
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
        query=rag_request.query,
        top_k=rag_request.top_k,
        threshold=rag_request.threshold,
    )

    template_controller: TemplateController = request.app.state.template_controller
    system_prompt = template_controller.get_template("rag", "SYSTEM_PROMPT")
    if system_prompt is None:
        template_controller.logger.error(
            "RAG request failed; Missing RAG templates: SYSTEM_PROMPT"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"msg": ResponseSignals.RAG_GENERATION_FAILED.value},
        )

    context_entries = "\n".join(
        [
            entry
            for idx, vector in enumerate(relevant_vectors)
            if (
                entry := template_controller.get_template(
                    "rag",
                    "CONTEXT_ENTRY",
                    variables={
                        "index": idx + 1,
                        "content": vector.text,
                    },
                )
            )
            is not None
        ]
    )
    if not context_entries:
        template_controller.logger.error(
            "RAG request failed; Missing RAG templates: CONTEXT_ENTRY"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"msg": ResponseSignals.RAG_GENERATION_FAILED.value},
        )

    footer = template_controller.get_template(
        "rag",
        "FOOTER",
        variables={"query": rag_request.query},
    )
    if footer is None:
        template_controller.logger.error(
            "RAG request failed; Missing RAG templates: FOOTER"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"msg": ResponseSignals.RAG_GENERATION_FAILED.value},
        )

    query_prompt = "\n\n".join([context_entries, footer])

    rag_controller = RAGController(
        settings=settings,
        generation_model=request.app.state.generation_llm,
    )
    rag_response = await rag_controller.generate_response(
        query=query_prompt,
        system_message=system_prompt,
        temperature=rag_request.temperature,
        max_output_tokens=rag_request.max_output_tokens,
    )

    if rag_response is None:
        rag_controller.logger.error("RAG generation failed; No response generated")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"msg": ResponseSignals.RAG_GENERATION_FAILED.value},
        )

    citations = rag_controller.extract_citations(
        response=rag_response, context_entries=relevant_vectors
    )

    return JSONResponse(
        content={
            "response": rag_response,
            "citations": [citation.model_dump() for citation in citations],
            "contexts": [vector.model_dump() for vector in relevant_vectors],
        },
        status_code=status.HTTP_202_ACCEPTED,
    )
