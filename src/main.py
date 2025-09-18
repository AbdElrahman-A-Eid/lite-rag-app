"""
Main application script for Lite-RAG-App
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from pymongo import AsyncMongoClient
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
    fastapi_app.state.engine = create_async_engine(
        f"postgresql+asyncpg://{fastapi_app.state.settings.database_username}:"
        f"{fastapi_app.state.settings.database_password}@"
        f"{fastapi_app.state.settings.database_hostname}:"
        f"{fastapi_app.state.settings.database_port}/"
        f"{fastapi_app.state.settings.database_name}",
        expire_on_commit=False,
    )
    fastapi_app.state.async_session = async_sessionmaker(
        bind=fastapi_app.state.engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    fastapi_app.state.mongo_client = AsyncMongoClient(
        str(fastapi_app.state.settings.mongo_uri)
    )
    fastapi_app.state.mongo_db = fastapi_app.state.mongo_client[
        fastapi_app.state.settings.mongo_db_name
    ]

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
    await fastapi_app.state.mongo_client.close()


app = FastAPI(lifespan=lifespan)
app.include_router(base_router)
app.include_router(assets_router)
app.include_router(projects_router)
app.include_router(document_router)
app.include_router(vector_router)
app.include_router(rag_router)
