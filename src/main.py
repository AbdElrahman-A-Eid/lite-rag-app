"""
Main application script for Lite-RAG-App
"""

from fastapi import FastAPI
from routes.base import base_router
from routes.files import files_router
from routes.projects import projects_router
from routes.documents import document_router
from config import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.include_router(base_router)
app.include_router(files_router)
app.include_router(projects_router)
app.include_router(document_router)
