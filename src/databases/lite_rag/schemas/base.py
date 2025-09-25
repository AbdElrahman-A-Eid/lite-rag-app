"""
SQLAlchemy Async Declarative setup with opt-in mixins (Postgres).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Identity,
    Integer,
    MetaData,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)
from sqlalchemy.sql import functions

_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s__%(column_0_name)s",
    "ck": "ck_%(table_name)s__%(constraint_name)s",
    "fk": "fk_%(table_name)s__%(column_0_name)s__%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata_obj = MetaData(naming_convention=_convention)


class Base(AsyncAttrs, DeclarativeBase):
    """
    Base class for all database models.

    Inherits from AsyncAttrs for async support and DeclarativeBase for ORM mapping.
    """

    metadata = metadata_obj


class PKUUIDMixin:
    """
    Mixin to add a UUID primary key column named 'id'.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class PKIntMixin:
    """
    Mixin to add an Integer primary key column named 'id' with Identity.
    """

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(always=False),
        primary_key=True,
    )


class TimestampMixin:
    """
    Mixin to add 'created_at' and 'updated_at' timestamp columns.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=functions.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=functions.now(),
        server_onupdate=functions.now(),
        nullable=False,
    )
