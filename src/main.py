"""
Main application script for Lite-RAG-App
"""

from fastapi import FastAPI
from routes.base import base_router
from routes.files import files_router
from routes.projects import projects_router

app = FastAPI()

app.include_router(base_router)
app.include_router(files_router)
app.include_router(projects_router)
