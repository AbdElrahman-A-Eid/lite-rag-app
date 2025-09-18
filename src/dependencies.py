"""
Dependencies for the application.
"""

from typing import AsyncGenerator

from fastapi import Request
from pymongo import AsyncMongoClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Get a database session from the request state.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        AsyncGenerator[AsyncSession, None]: The database session.
    """
    Session: async_sessionmaker = request.app.state.async_session
    async with Session() as session:
        yield session


async def get_db(request: Request) -> AsyncGenerator[AsyncMongoClient, None]:
    """Get the database client from the request state.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        AsyncGenerator[AsyncMongoClient]: The MongoDB client.
    """
    yield request.app.state.mongo_db
