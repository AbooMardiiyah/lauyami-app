from prefect import task
from prefect.cache_policies import NO_CACHE
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from src.config import settings
from src.infrastructure.supabase.init_session import init_session
from src.models.article_models import ArticleItem
from src.models.sql_models import LegalDocument
from src.utils.logger_util import setup_logging


@task(
    task_run_name="ingest-legal-documents",
    description="Ingest legal documents into database in batches.",
    retries=2,
    retry_delay_seconds=120,
    cache_policy=NO_CACHE,
)
def ingest_documents(
    document_items: list[ArticleItem],
    document_model: type[LegalDocument],
    engine: Engine,
    skip_existing: bool = True,
) -> None:
    """Ingest legal document items into database.

    Documents are inserted in batches to optimize database writes. Errors during
    ingestion of individual batches are logged but do not stop subsequent batches.

    Args:
        document_items: List of ArticleItem objects to ingest (representing legal documents).
        document_model: The SQLAlchemy model class for documents.
        engine: SQLAlchemy Engine for database connection.
        skip_existing: If True, skip documents that already exist (based on URL/document_id).
            Defaults to True.

    Raises:
        RuntimeError: If ingestion completes with errors.
    """
    logger = setup_logging()
    doc_settings = settings.document
    errors = []
    batch: list[ArticleItem] = []
    skipped_count = 0

    session: Session = init_session(engine)

    try:
        for i, document in enumerate(document_items, start=1):
            if skip_existing:
                existing = session.query(document_model).filter_by(document_id=document.document_id).first()
                if existing:
                    logger.debug(
                        f"Document '{document.document_title}' (ID: {document.document_id}) already exists, skipping"
                    )
                    skipped_count += 1
                    continue

            batch.append(document)

            if len(batch) >= doc_settings.batch_size:
                batch_num = i // doc_settings.batch_size
                try:
                    _persist_batch(session, batch, document_model)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    logger.error(f"Failed to ingest batch {batch_num}: {e}")
                    errors.append(f"Batch {batch_num}")
                else:
                    logger.info(
                        f"Ingested batch {batch_num} with {len(batch)} document(s)"
                    )
                batch = []

        if batch:
            try:
                _persist_batch(session, batch, document_model)
                session.commit()
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to ingest final batch: {e}")
                errors.append("Final batch")
            else:
                logger.info(f"Ingested final batch of {len(batch)} document(s)")

        if errors:
            raise RuntimeError(f"Ingestion completed with errors: {errors}")

        ingested_count = len(document_items) - skipped_count
        logger.info(
            f"Successfully ingested {ingested_count} document item(s)"
            + (f" (skipped {skipped_count} existing)" if skipped_count > 0 else "")
        )

    except Exception as e:
        logger.error(f"Unexpected error in ingest_documents: {e}")
        raise
    finally:
        session.close()
        logger.info("Database session closed")


def _persist_batch(
    session: Session,
    batch: list[ArticleItem],
    document_model: type[LegalDocument],
) -> None:
    """Helper to bulk insert a batch of ArticleItems (legal documents)."""
    rows = [
        document_model(
            document_title=document.document_title,
            jurisdiction=document.jurisdiction,
            section_title=document.section_title,
            document_id=document.document_id,
            content=document.content,
            document_type=document.document_type,
            effective_date=document.effective_date,
        )
        for document in batch
    ]
    session.bulk_save_objects(rows)
