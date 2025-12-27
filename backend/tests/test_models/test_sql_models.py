import uuid
from uuid import UUID

from sqlalchemy import ARRAY, TIMESTAMP, BigInteger, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class LegalDocumentTest(Base):
    __tablename__ = "legal_documents_test"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    uuid: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        index=True,
    )

    document_title: Mapped[str] = mapped_column(
        String, nullable=False, comment="Document title (e.g., 'Lagos State Tenancy Law 2011')"
    )
    jurisdiction: Mapped[str] = mapped_column(
        String, nullable=False, comment="Jurisdiction (e.g., 'Lagos State')"
    )
    document_type: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, comment="Document type or related metadata"
    )
    section_title: Mapped[str] = mapped_column(
        String, nullable=False, comment="Section title for chunked sections"
    )
    document_id: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, comment="Unique identifier for the document"
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Content of the document section/chunk"
    )
    effective_date: Mapped[str] = mapped_column(
        TIMESTAMP, nullable=False, comment="Effective date or issued date"
    )
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
