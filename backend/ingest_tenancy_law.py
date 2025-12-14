#!/usr/bin/env python3
"""Script to ingest legal documents from YAML configuration.

This script reads legal document configurations from legal_documents.yaml,
extracts text from PDFs, and ingests them into the Supabase database.
After running this, you should run the embeddings ingestion flow to create vector embeddings.

To add new documents, edit src/configs/legal_documents.yaml

Usage:
    python ingest_tenancy_law.py
"""

import sys
from pathlib import Path
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent))

from src.pipelines.flows.batch_document_ingestion_flow import batch_document_ingestion_flow


def main():
    """Ingest legal documents from YAML configuration."""
    logger.info("Starting batch document ingestion from YAML configuration...")
    logger.info("Reading documents from: src/configs/legal_documents.yaml")
    logger.info("")

    try:
        batch_document_ingestion_flow()

        logger.success("\nBatch document ingestion completed successfully!")
        logger.info("\nNext steps:")
        logger.info("   1. Run the embeddings ingestion flow to create vector embeddings:")
        logger.info("      python -m src.infrastructure.qdrant.ingest_from_sql")
        logger.info("   OR use Prefect flow:")
        logger.info("      from src.pipelines.flows.embeddings_ingestion_flow import qdrant_ingest_flow")
        logger.info("      import asyncio")
        logger.info("      asyncio.run(qdrant_ingest_flow())")
        logger.info("\n💡 To add more documents, edit: src/configs/legal_documents.yaml")

    except Exception as e:
        logger.error(f"\nError during document ingestion: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
