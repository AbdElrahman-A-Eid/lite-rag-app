"""
Base model for all database entities.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession


class BaseDataModel:
    """
    Base model for all database entities.
    """

    def __init__(self, db_session: AsyncSession):
        """Initialize the base data model.

        Args:
            db_session (AsyncSession): The SQLAlchemy database async session.
        """
        self.db_session = db_session
        self.logger = logging.getLogger(self.__class__.__name__)
