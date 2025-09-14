"""
Base API routes for Lite-RAG-App
"""

from typing import Dict

from fastapi import APIRouter, Request

base_router = APIRouter(prefix="/api/v1", tags=["base", "v1"])


@base_router.get("/")
async def root(request: Request) -> Dict[str, str]:
    """Root endpoint

    Returns:
        dict: Root status
    """
    settings = request.app.state.settings
    return {"App Name": settings.app_name, "App Version": settings.app_version}


@base_router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint

    Returns:
        dict: Health status
    """
    return {"status": "ok"}
