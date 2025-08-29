"""
Base model for all database entities.
"""

import logging
from pymongo.asynchronous.database import AsyncDatabase


class BaseDataModel:
    """
    Base model for all database entities.
    """

    def __init__(self, mongo_db: AsyncDatabase):
        """Initialize the base data model.

        Args:
            mongo_db (AsyncDatabase): The MongoDB database async instance.
        """
        self.mongo_db = mongo_db
        self.logger = logging.getLogger(self.__class__.__name__)
