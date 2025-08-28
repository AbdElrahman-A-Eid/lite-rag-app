"""
Dependencies for the application.
"""

from typing import AsyncGenerator
from pymongo import AsyncMongoClient
from fastapi import Request

async def get_db(request: Request) -> AsyncGenerator[AsyncMongoClient, None]:
    """Get the database client from the request state.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        AsyncGenerator[AsyncMongoClient]: The MongoDB client.
    """
    yield request.app.state.mongo_client
