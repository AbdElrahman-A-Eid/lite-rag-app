"""
Asset Database Schema
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import CITEXT, JSONB, UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from databases.lite_rag.schemas.base import Base, PKUUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from databases.lite_rag.schemas.chunk import DocumentChunk
    from databases.lite_rag.schemas.file import File
    from databases.lite_rag.schemas.project import Project


class Asset(PKUUIDMixin, TimestampMixin, Base):
    """
    Asset table schema.
    """

    __tablename__ = "assets"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[str] = mapped_column(CITEXT, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    size: Mapped[Optional[float]]
    config: Mapped[dict] = mapped_column(JSONB, default=dict)

    project: Mapped["Project"] = relationship(back_populates="assets")
    document_chunks: Mapped[List["DocumentChunk"]] = relationship(
        back_populates="asset", cascade="all, delete-orphan", lazy="selectin"
    )
    file: Mapped[Optional["File"]] = relationship(
        "File",
        back_populates="asset",
        cascade="all, delete-orphan",
        single_parent=True,
        lazy="joined",
    )

    __table_args__ = (
        Index(
            "ix_assets_project_id_name",
            "project_id",
            "name",
            unique=True,
        ),
        Index(
            "ix_assets_project_id",
            "project_id",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Asset(id={self.id}, project_id={self.project_id}, "
            f"name={self.name}, type={self.type})>"
        )
