"""Script to clear all user session collections from Qdrant.

This helps free up memory and resources by removing temporary session collections
that may have accumulated from previous document uploads.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import settings
from src.infrastructure.qdrant.qdrant_vectorstore import AsyncQdrantVectorStore
from src.utils.logger_util import setup_logging

logger = setup_logging()


async def clear_all_session_collections():
    """Clear all user session collections from Qdrant."""
    try:
        vectorstore = AsyncQdrantVectorStore()
        client = vectorstore.client
        
        collections = await client.get_collections()
        logger.info(f"Found {len(collections.collections)} total collections")
        
        session_collections = [
            col.name for col in collections.collections 
            if col.name.startswith("user_session_")
        ]
        
        logger.info(f"Found {len(session_collections)} session collections to delete")
        
        if not session_collections:
            logger.info("No session collections to delete")
            return
        
        deleted_count = 0
        for collection_name in session_collections:
            try:
                await client.delete_collection(collection_name=collection_name)
                logger.info(f"Deleted session collection: {collection_name}")
                deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to delete collection {collection_name}: {e}")
        
        logger.info(f"Successfully deleted {deleted_count} session collections")
        
        await client.close()
        
    except Exception as e:
        logger.error(f"Error clearing session collections: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    print("Clearing all user session collections from Qdrant...")
    asyncio.run(clear_all_session_collections())
    print("Done!")
