"""
Document Chunk Database Schema
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from databases.lite_rag.schemas.base import Base, PKUUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from databases.lite_rag.schemas.asset import Asset
    from databases.lite_rag.schemas.project import Project


class DocumentChunk(PKUUIDMixin, TimestampMixin, Base):
    """
    Document Chunk table schema.
    """

    __tablename__ = "chunks"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    asset_id: Mapped[UUID] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False,
    )
    order: Mapped[int]
    content: Mapped[str]
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict)

    project: Mapped["Project"] = relationship(back_populates="document_chunks")
    asset: Mapped["Asset"] = relationship(back_populates="document_chunks")

    __table_args__ = (
        Index(
            "ix_chunks_project_id",
            "project_id",
        ),
        Index(
            "ix_chunks_project_asset_id",
            "project_id",
            "asset_id",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<DocumentChunk(id={self.id}, project_id={self.project_id}, "
            f"asset_id={self.asset_id}, order={self.order})>"
        )
