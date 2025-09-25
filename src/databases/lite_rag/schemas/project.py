"""
Project Database Schema
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from databases.lite_rag.schemas.base import Base, PKUUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from databases.lite_rag.schemas.asset import Asset


class Project(PKUUIDMixin, TimestampMixin, Base):
    """
    Project table schema.
    """

    __tablename__ = "projects"

    name: Mapped[Optional[str]] = mapped_column(default="Unnamed Project")
    description: Mapped[Optional[str]] = mapped_column(
        default="No description provided."
    )
    assets: Mapped[List["Asset"]] = relationship(
        back_populates="project", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, assets_count={len(self.assets)})>"
