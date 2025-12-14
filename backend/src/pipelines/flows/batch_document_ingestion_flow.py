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
    name="batch_document_ingestion_flow",
    flow_run_name="batch_document_ingestion_flow_run",
    description="Extract and ingest multiple legal documents from PDF files configured in YAML.",
    retries=2,
    retry_delay_seconds=120,
)
def batch_document_ingestion_flow(
    document_model: type[LegalDocument] = LegalDocument,
) -> None:
    """Extract and ingest multiple legal documents from YAML configuration.

    This flow reads the legal documents configuration from the YAML file,
    extracts text from each PDF, and ingests them into the Supabase database.
    After ingestion, you can run the embeddings ingestion flow to create vector embeddings.

    Args:
        document_model (type[LegalDocument]): SQLAlchemy model for storing documents.
            Defaults to LegalDocument.

    Returns:
        None

    Raises:
        RuntimeError: If ingestion fails.
        Exception: For unexpected errors during execution.
    """
    engine = init_engine()
    documents_config = settings.legal_documents

    if not documents_config:
        logger.warning("No legal documents found in configuration file")
        return

    logger.info(f"Starting batch document ingestion flow for {len(documents_config)} document(s)")

    successful = 0
    failed = 0

    try:
        for idx, doc_config in enumerate(documents_config, start=1):
            pdf_path = Path(doc_config.pdf_path)
            
            if not pdf_path.is_absolute():
                backend_dir = Path(__file__).parent.parent.parent.parent
                pdf_path = backend_dir / pdf_path

            logger.info(f"[{idx}/{len(documents_config)}] Processing: {doc_config.document_title}")
            logger.info(f"  PDF path: {pdf_path}")
            logger.info(f"  Jurisdiction: {doc_config.jurisdiction}")

            try:
                if not pdf_path.exists():
                    logger.error(f"PDF file not found: {pdf_path}")
                    failed += 1
                    continue

                # Step 1: Extract text from PDF and create document items
                logger.info("Extracting text from PDF...")
                document_items = create_document_items_from_pdf(
                    pdf_path=pdf_path,
                    document_title=doc_config.document_title,
                    jurisdiction=doc_config.jurisdiction,
                    document_id=doc_config.document_id,
                    effective_date=doc_config.effective_date,
                )

                if not document_items:
                    logger.warning(f"No document items created from PDF: {pdf_path}")
                    failed += 1
                    continue

                logger.info(f" Extracted {len(document_items)} document item(s) from PDF")

                # Step 2: Ingest documents into database
                logger.info("Ingesting documents into database...")
                ingest_documents(
                    document_items=document_items,
                    document_model=document_model,
                    engine=engine,
                    skip_existing=True,
                )

                logger.info(f"Successfully ingested: {doc_config.document_title}")
                successful += 1

            except Exception as e:
                logger.error(f" Error processing document '{doc_config.document_title}': {e}")
                failed += 1
                continue

        # Summary
        logger.info("")
        logger.info("=" * 60)
        logger.info(f"Batch ingestion summary:")
        logger.info(f"  Successful: {successful}")
        logger.info(f" Failed: {failed}")
        logger.info(f" Total: {len(documents_config)}")
        logger.info("=" * 60)

        if successful > 0:
            logger.info("")
            logger.info("Next step: Run embeddings_ingestion_flow to create vector embeddings for search")

        if failed > 0:
            raise RuntimeError(f"Batch ingestion completed with {failed} failure(s)")

    except Exception as e:
        logger.error(f"Error in batch document ingestion flow: {e}")
        raise RuntimeError("Batch document ingestion flow failed") from e
    finally:
        engine.dispose()
        logger.info("Database engine disposed")


if __name__ == "__main__":
    batch_document_ingestion_flow()

