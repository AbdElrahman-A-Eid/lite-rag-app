"""
Dependencies for the application.
"""

from typing import AsyncGenerator

from fastapi import Request
from pymongo import AsyncMongoClient


async def get_db(request: Request) -> AsyncGenerator[AsyncMongoClient, None]:
    """Get the database client from the request state.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        AsyncGenerator[AsyncMongoClient]: The MongoDB client.
    """
    yield request.app.state.mongo_db
