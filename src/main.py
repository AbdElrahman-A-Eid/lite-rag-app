"""
Main application script for Lite-RAG-App
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import get_settings, setup_logging
from llm.controllers.factory import LLMProviderFactory
from llm.controllers.templates import TemplateController
from routes.assets import assets_router
from routes.base import base_router
from routes.documents import document_router
from routes.projects import projects_router
from routes.rag import rag_router
from routes.vectors import vector_router
from vectordb import VectorDBProviderFactory


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """Manage the lifespan of the application.

    Args:
        fastapi_app (FastAPI): The FastAPI application instance.
    """
    fastapi_app.state.settings = get_settings()
    fastapi_app.title = fastapi_app.state.settings.app_name
    fastapi_app.version = fastapi_app.state.settings.app_version
    setup_logging(fastapi_app.state.settings)
    db_url = URL.create(
        "postgresql+asyncpg",
        username=fastapi_app.state.settings.database_username,
        password=fastapi_app.state.settings.database_password,
        host=fastapi_app.state.settings.database_hostname,
        port=fastapi_app.state.settings.database_port,
        database=fastapi_app.state.settings.database_name,
    )
    fastapi_app.state.engine = create_async_engine(
        db_url.render_as_string(hide_password=False),
    )
    fastapi_app.state.async_session = async_sessionmaker(
        bind=fastapi_app.state.engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    llm_factory = LLMProviderFactory(fastapi_app.state.settings)
    fastapi_app.state.embedding_llm = llm_factory.create(
        provider_type=fastapi_app.state.settings.embedding_backend
    )
    if fastapi_app.state.embedding_llm is not None:
        await fastapi_app.state.embedding_llm.set_embedding_model(
            fastapi_app.state.settings.embedding_model_id,
            fastapi_app.state.settings.embedding_dimensions,
        )
    fastapi_app.state.generation_llm = llm_factory.create(
        provider_type=fastapi_app.state.settings.generation_backend
    )
    if fastapi_app.state.generation_llm is not None:
        await fastapi_app.state.generation_llm.set_generation_model(
            fastapi_app.state.settings.generation_model_id
        )

    vectordb_factory = VectorDBProviderFactory(fastapi_app.state.settings)
    fastapi_app.state.vectordb_client = vectordb_factory.create(
        provider=fastapi_app.state.settings.vectordb_backend
    )
    if fastapi_app.state.vectordb_client is not None:
        await fastapi_app.state.vectordb_client.connect()

    fastapi_app.state.template_controller = TemplateController(
        primary_lang=fastapi_app.state.settings.primary_language,
        fallback_lang=fastapi_app.state.settings.fallback_language,
    )

    yield

    await fastapi_app.state.engine.dispose()
    if fastapi_app.state.vectordb_client is not None:
        await fastapi_app.state.vectordb_client.disconnect()


app = FastAPI(lifespan=lifespan)
app.include_router(base_router)
app.include_router(assets_router)
app.include_router(projects_router)
app.include_router(document_router)
app.include_router(vector_router)
app.include_router(rag_router)
