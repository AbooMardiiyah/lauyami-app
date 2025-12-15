# src/models/qdrant_models.py
from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


# -----------------------------
# Qdrant payload settings for legal documents
# -----------------------------
class ArticleChunkPayload(BaseModel):
    """Payload model for legal document chunks in Qdrant."""
    document_title: str = Field(default="", description="Document title (e.g., 'Lagos State Tenancy Law 2011')")
    jurisdiction: str = Field(default="", description="Jurisdiction (e.g., 'Lagos State')")
    document_type: list[str] = Field(default_factory=list, description="Document type or related metadata")
    section_title: str = Field(default="", description="Section title for the chunk")
    document_id: HttpUrl | str | None = Field(default=None, description="Document ID (unique identifier for the document)")
    effective_date: datetime | str = Field(
        default_factory=datetime.now, description="Effective date or issued date of the document"
    )
    created_at: datetime | str = Field(
        default_factory=datetime.now, description="Creation date when chunk was indexed"
    )
    chunk_index: int = Field(default=0, description="Index of the document chunk")
    chunk_text: str | None = Field(default=None, description="Text content of the document chunk")
