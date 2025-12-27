from pathlib import Path
from pydantic import BaseModel, Field


class DocumentConfig(BaseModel):
    """Configuration model for legal documents to ingest from PDF files."""
    pdf_path: str | Path = Field(description="Path to the PDF file ")
    document_title: str = Field(description="Title of the legal document (e.g., 'Lagos State Tenancy Law 2011')")
    jurisdiction: str = Field(description="Jurisdiction of the document (e.g., 'Lagos State')")
    document_id: str | None = Field(
        default=None,
        description="Unique identifier for the document. If None, uses PDF filename without extension"
    )
    effective_date: str | None = Field(
        default=None,
        description="Effective or issued date of the document in YYYY-MM-DD format"
    )

