"""
Main application script for Lite-RAG-App
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from pymongo import AsyncMongoClient
from routes.base import base_router
from routes.assets import assets_router
from routes.projects import projects_router
from routes.documents import document_router
from config import settings
from llm import LLMProviderFactory


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """Manage the lifespan of the application.

    Args:
        fastapi_app (FastAPI): The FastAPI application instance.
    """
    fastapi_app.state.mongo_client = AsyncMongoClient(str(settings.mongo_uri))
    fastapi_app.state.mongo_db = fastapi_app.state.mongo_client[settings.mongo_db_name]

    llm_factory = LLMProviderFactory(settings)
    fastapi_app.state.embedding_llm = llm_factory.create(
        provider_type=settings.embedding_backend
    )
    if fastapi_app.state.embedding_llm is not None:
        fastapi_app.state.embedding_llm.set_embedding_model(
            settings.embedding_model_id, settings.embedding_dimensions
        )
    fastapi_app.state.generation_llm = llm_factory.create(
        provider_type=settings.generation_backend
    )
    if fastapi_app.state.generation_llm is not None:
        fastapi_app.state.generation_llm.set_generation_model(
            settings.generation_model_id
        )

    yield

    await fastapi_app.state.mongo_client.close()


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
app.include_router(base_router)
app.include_router(assets_router)
app.include_router(projects_router)
app.include_router(document_router)
