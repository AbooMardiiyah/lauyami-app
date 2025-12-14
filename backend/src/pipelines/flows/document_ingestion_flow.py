from pathlib import Path

from prefect import flow

from src.config import settings
from src.infrastructure.supabase.init_session import init_engine
from src.models.sql_models import LegalDocument
from src.pipelines.tasks.extract_pdf import create_document_items_from_pdf
from src.pipelines.tasks.ingest_document import ingest_documents
from src.utils.logger_util import setup_logging

logger = setup_logging()


@flow(
    name="document_ingestion_flow",
    flow_run_name="document_ingestion_flow_run",
    description="Extract and ingest legal document from PDF file.",
    retries=2,
    retry_delay_seconds=120,
)
def document_ingestion_flow(
    pdf_path: str | Path,
    document_title: str,
    jurisdiction: str,
    document_id: str | None = None,
    effective_date: str | None = None,
    document_model: type[LegalDocument] = LegalDocument,
) -> None:
    """Extract and ingest a legal document from a PDF file.

    This flow extracts text from a PDF file and ingests it into the Supabase database.
    After ingestion, you can run the embeddings ingestion flow to create vector embeddings.

    Args:
        pdf_path (str | Path): Path to the PDF file.
        document_title (str): Title of the legal document (e.g., "Lagos State Tenancy Law 2011").
        jurisdiction (str): Jurisdiction of the document (e.g., "Lagos State").
        document_id (str | None, optional): Unique identifier for the document.
            If None, uses the PDF filename without extension. Defaults to None.
        effective_date (str | None, optional): Effective or issued date of the document.
            Format: "YYYY-MM-DD". Defaults to None.
        document_model (type[LegalDocument]): SQLAlchemy model for storing documents.
            Defaults to LegalDocument.

    Returns:
        None

    Raises:
        RuntimeError: If ingestion fails.
        Exception: For unexpected errors during execution.
    """
    engine = init_engine()

    try:
        logger.info(f"Starting document ingestion flow for: {pdf_path}")
        logger.info(f"Document title: {document_title}")
        logger.info(f"Jurisdiction: {jurisdiction}")

        logger.info("Extracting text from PDF...")
        document_items = create_document_items_from_pdf(
            pdf_path=pdf_path,
            document_title=document_title,
            jurisdiction=jurisdiction,
            document_id=document_id,
            effective_date=effective_date,
        )

        if not document_items:
            logger.warning("No document items created from PDF")
            return

        logger.info(f"Extracted {len(document_items)} document item(s) from PDF")

        logger.info("Ingesting documents into database...")
        ingest_documents(
            document_items=document_items,
            document_model=document_model,
            engine=engine,
            skip_existing=True,
        )

        logger.info("Document ingestion flow completed successfully")
        logger.info(
            "Next step: Run embeddings_ingestion_flow to create vector embeddings for search"
        )

    except Exception as e:
        logger.error(f"Error in document ingestion flow: {e}")
        raise RuntimeError("Document ingestion flow failed") from e
    finally:
        engine.dispose()
        logger.info("Database engine disposed")


def main() -> None:
    """Run document ingestion flow for all documents in YAML config.
    
    Loads document configurations from src/configs/legal_documents.yaml
    and processes each document defined there.
    """
    legal_documents = settings.legal_documents
    
    if not legal_documents:
        logger.warning(
            "No legal documents found in configuration. "
            f"Check {settings.document.documents_config_path}"
        )
        logger.info(
            "Add documents to the YAML file with format:\n"
            "documents:\n"
            "  - pdf_path: 'data/your-document.pdf'\n"
            "    document_title: 'Your Document Title'\n"
            "    jurisdiction: 'Your Jurisdiction'\n"
            "    document_id: 'your-document-id'\n"
            "    effective_date: 'YYYY-MM-DD'"
        )
        return
    
    logger.info(f"Found {len(legal_documents)} document(s) in configuration")
    
    for doc_config in legal_documents:
        logger.info(f"Processing: {doc_config.document_title}")
        try:
            document_ingestion_flow(
                pdf_path=Path(doc_config.pdf_path),
                document_title=doc_config.document_title,
                jurisdiction=doc_config.jurisdiction,
                document_id=doc_config.document_id,
                effective_date=doc_config.effective_date,
            )
            logger.info(f"✓ Successfully processed: {doc_config.document_title}")
        except Exception as e:
            logger.error(
                f"✗ Failed to process {doc_config.document_title}: {e}"
            )
            continue
    
    logger.info("Document ingestion flow completed for all configured documents")


if __name__ == "__main__":
    main()

