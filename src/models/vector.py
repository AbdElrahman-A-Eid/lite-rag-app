"""
Model defnition for a retrieved document chunk.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class RetrievedDocumentChunk(BaseModel):
    """Model definition for retrieved document chunk."""

    id: str | int = Field(..., description="The unique identifier for the vector")
    text: str = Field(..., description="The text content of the document chunk")
    metadata: Dict[str, Any] = Field(
        ..., description="Metadata associated with the document chunk"
    )
    score: Optional[float] = Field(
        default=None,
        description="The relevance score of the document chunk in case of similarity search",
    )

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="ignore")
