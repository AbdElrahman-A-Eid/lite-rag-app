"""
Main application script for Lite-RAG-App
"""

from typing import Dict
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint

    Returns:
        dict: Health status
    """
    return {"status": "ok"}
