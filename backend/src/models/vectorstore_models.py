# src/models/qdrant_models.py
from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


# -----------------------------
# Qdrant payload settings for legal documents
# -----------------------------
class ArticleChunkPayload(BaseModel):
    """Payload model for legal document chunks in Qdrant.
    
    Field names are kept for backward compatibility but semantically represent:
    - feed_name → document_title (e.g., "Lagos State Tenancy Law 2011")
    - feed_author → jurisdiction (e.g., "Lagos State")
    - title → section_title (for chunked sections)
    - url → document_id (unique identifier for the document)
    - article_authors → document_type or empty list
    - published_at → effective_date or issued_date
    """
    feed_name: str = Field(default="", description="Document title (e.g., 'Lagos State Tenancy Law 2011')")
    feed_author: str = Field(default="", description="Jurisdiction (e.g., 'Lagos State')")
    article_authors: list[str] = Field(default_factory=list, description="Document type or related metadata")
    title: str = Field(default="", description="Section title for the chunk")
    url: HttpUrl | str | None = Field(default=None, description="Document ID (unique identifier for the document)")
    published_at: datetime | str = Field(
        default_factory=datetime.now, description="Effective date or issued date of the document"
    )
    created_at: datetime | str = Field(
        default_factory=datetime.now, description="Creation date when chunk was indexed"
    )
    chunk_index: int = Field(default=0, description="Index of the document chunk")
    chunk_text: str | None = Field(default=None, description="Text content of the document chunk")
