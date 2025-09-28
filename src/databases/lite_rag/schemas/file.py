"""
File Database Schema
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    Index,
    LargeBinary,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from databases.lite_rag.schemas.base import Base, PKUUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from databases.lite_rag.schemas.asset import Asset


class File(PKUUIDMixin, TimestampMixin, Base):
    """
    File table schema.
    """

    __tablename__ = "files"

    asset_id: Mapped[UUID] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"),
        unique=True,
    )
    name: Mapped[str]
    content_type: Mapped[str] = mapped_column(String(255))
    data: Mapped[bytes] = mapped_column(LargeBinary)

    asset: Mapped["Asset"] = relationship(
        back_populates="file",
    )

    __table_args__ = (
        Index(
            "ix_files_asset_id",
            "asset_id",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<File(id={self.id}, asset_id={self.asset_id}, "
            f"name={self.name}, content_type={self.content_type})>"
        )
