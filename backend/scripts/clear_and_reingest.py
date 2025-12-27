#!/usr/bin/env python3
"""Script to clear database and Qdrant, then re-ingest legal documents.

This script:
1. Drops and recreates the database table
2. Deletes the Qdrant collection
3. Re-ingests documents from PDFs
4. Creates vector embeddings in Qdrant
"""

import asyncio
from pathlib import Path

from src.config import settings
from src.infrastructure.qdrant.qdrant_vectorstore import AsyncQdrantVectorStore
from src.infrastructure.supabase.create_db import create_table
from src.infrastructure.supabase.delete_db import delete_all_tables
from src.pipelines.flows.batch_document_ingestion_flow import batch_document_ingestion_flow
from src.pipelines.flows.embeddings_ingestion_flow import qdrant_ingest_flow
from src.utils.logger_util import setup_logging

logger = setup_logging()


async def clear_qdrant_collection() -> None:
    """Delete the Qdrant collection."""
    try:
        vectorstore = AsyncQdrantVectorStore()
        logger.info(f"Deleting Qdrant collection: {vectorstore.collection_name}")
        await vectorstore.client.delete_collection(vectorstore.collection_name)
        logger.info("Qdrant collection deleted successfully")
    except Exception as e:
        logger.warning(f"Error deleting Qdrant collection (may not exist): {e}")


async def recreate_qdrant_collection() -> None:
    """Recreate the Qdrant collection with proper schema."""
    try:
        vectorstore = AsyncQdrantVectorStore()
        logger.info(f"Creating Qdrant collection: {vectorstore.collection_name}")
        await vectorstore.create_collection()
        logger.info("Qdrant collection created successfully")
        
        logger.info("Creating Qdrant indexes...")
        await vectorstore.enable_hnsw()
        await vectorstore.create_section_title_index()
        await vectorstore.create_document_type_index()
        await vectorstore.create_jurisdiction_index()
        await vectorstore.create_document_title_index()
        logger.info("Qdrant indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating Qdrant collection: {e}")
        raise


def main() -> None:
    """Main function to clear and re-ingest."""
    logger.info("=" * 60)
    logger.info("Starting clear and re-ingest process")
    logger.info("=" * 60)
    
    logger.info("\n[Step 1/4] Clearing database...")
    try:
        delete_all_tables(confirm=True)  
        logger.info("Database cleared successfully")
    except Exception as e:
        logger.error(f"Error clearing database: {e}")
        raise
    
    logger.info("\n[Step 2/4] Recreating database table...")
    try:
        create_table()
        logger.info("Database table created successfully")
    except Exception as e:
        logger.error(f"Error creating database table: {e}")
        raise
    
    logger.info("\n[Step 3/4] Clearing and recreating Qdrant collection...")
    try:
        asyncio.run(clear_qdrant_collection())
        asyncio.run(recreate_qdrant_collection())
        logger.info("Qdrant collection recreated successfully")
    except Exception as e:
        logger.error(f"Error recreating Qdrant collection: {e}")
        raise
    
    logger.info("\n[Step 4/4] Re-ingesting documents...")
    try:
        batch_document_ingestion_flow()
        logger.info("Documents ingested successfully")
    except Exception as e:
        logger.error(f"Error ingesting documents: {e}")
        raise
    
    logger.info("\n[Step 5/5] Creating vector embeddings...")
    try:
        asyncio.run(qdrant_ingest_flow(from_date=None))
        logger.info("Vector embeddings created successfully")
    except Exception as e:
        logger.error(f"Error creating vector embeddings: {e}")
        raise
    
    logger.info("\n" + "=" * 60)
    logger.info("Clear and re-ingest process completed successfully!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

