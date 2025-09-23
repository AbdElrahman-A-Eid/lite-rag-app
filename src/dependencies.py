"""
Dependencies for the application.
"""

import logging
from typing import AsyncGenerator

from fastapi import Request
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
    logger = logging.getLogger("dependencies")
    Session: async_sessionmaker = request.app.state.async_session
    async with Session() as session:
        try:
            yield session
            await session.commit()
            logger.debug("Transaction committed successfully")
        except Exception as e:
            logger.error("Error occurred, rolling back: %s", str(e))
            await session.rollback()
