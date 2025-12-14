from pydantic import BaseModel, Field


# -----------------------------
# Legal Document settings
# -----------------------------
class ArticleItem(BaseModel):
    """Model for legal document sections/chunks.
    
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
    title: str = Field(default="", description="Section title for the chunk")
    url: str = Field(default="", description="Document ID (unique identifier for the document)")
    content: str = Field(default="", description="Content of the document section/chunk")
    article_authors: list[str] = Field(default_factory=list, description="Document type or related metadata")
    published_at: str | None = Field(default=None, description="Effective date or issued date of the document")
