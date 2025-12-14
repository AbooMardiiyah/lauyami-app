import uuid
from uuid import UUID

from sqlalchemy import ARRAY, TIMESTAMP, BigInteger, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.config import settings


class Base(DeclarativeBase):
    pass


class LegalDocument(Base):
    """SQLAlchemy model for legal documents.
    
    Represents legal documents stored in the database. Field names are maintained
    for database compatibility but semantically represent legal document properties.
    """
    __tablename__ = settings.supabase_db.table_name

    # Primary internal ID
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    # External unique identifier
    uuid: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        index=True,
    )

    # Legal Document fields (mapped from legacy article fields)
    # feed_name → document_title (e.g., "Lagos State Tenancy Law 2011")
    feed_name: Mapped[str] = mapped_column(String, nullable=False)
    # feed_author → jurisdiction (e.g., "Lagos State")
    feed_author: Mapped[str] = mapped_column(String, nullable=False)
    # article_authors → document_type or empty list
    article_authors: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    # title → section_title (for chunked sections)
    title: Mapped[str] = mapped_column(String, nullable=False)
    # url → document_id (unique identifier for the document)
    url: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    # content → section/chunk content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # published_at → effective_date or issued_date
    published_at: Mapped[str] = mapped_column(TIMESTAMP, nullable=False)
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
