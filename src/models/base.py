"""
Base model for all database entities.
"""

import logging
from typing import Annotated, Optional, Union

from bson.objectid import ObjectId
from pydantic import BeforeValidator, PlainSerializer
from pymongo.asynchronous.database import AsyncDatabase


def validate_object_id(v: Union[str, ObjectId, None]) -> Optional[ObjectId]:
    """Validate ObjectId input."""
    if v is None:
        return v
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str):
        try:
            return ObjectId(v)
        except Exception as exc:
            raise ValueError("Invalid ObjectId format") from exc
    raise ValueError("ObjectId must be a valid ObjectId or string")


def serialize_object_id(v: Optional[ObjectId]) -> Optional[str]:
    """Serialize ObjectId to string."""
    return str(v) if v is not None else None


MongoObjectId = Annotated[
    ObjectId,
    BeforeValidator(validate_object_id),
    PlainSerializer(serialize_object_id, return_type=str, when_used="json"),
]


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
