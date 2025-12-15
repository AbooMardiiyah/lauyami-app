from pydantic import BaseModel, Field


# -----------------------------
# Legal Document settings
# -----------------------------
class ArticleItem(BaseModel):
    """Model for legal document sections/chunks."""
    document_title: str = Field(default="", description="Document title (e.g., 'Lagos State Tenancy Law 2011')")
    jurisdiction: str = Field(default="", description="Jurisdiction (e.g., 'Lagos State')")
    section_title: str = Field(default="", description="Section title for the chunk")
    document_id: str = Field(default="", description="Document ID (unique identifier for the document)")
    content: str = Field(default="", description="Content of the document section/chunk")
    document_type: list[str] = Field(default_factory=list, description="Document type or related metadata")
    effective_date: str | None = Field(default=None, description="Effective date or issued date of the document")
