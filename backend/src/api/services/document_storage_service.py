"""Temporary document storage service for uploaded agreements.

Stores uploaded documents in-memory with session management.
Documents are automatically cleaned up when session expires or user exits.
"""

import asyncio
import time
import uuid
from datetime import datetime, timedelta

from src.infrastructure.supabase.init_session import init_engine, init_session
from src.models.sql_models import LegalDocument
from src.utils.logger_util import setup_logging
from src.api.services.session_vectorstore_service import SessionVectorStore

logger = setup_logging()

_uploaded_documents: dict[str, dict] = {}

DEFAULT_SESSION_EXPIRY = timedelta(hours=24)

_cleanup_task: asyncio.Task | None = None


class UploadedDocument:
    """Represents an uploaded document with session management."""

    def __init__(
        self,
        session_id: str,
        document_id: str,
        text: str,
        filename: str,
        expires_at: datetime | None = None,
    ):
        self.session_id = session_id
        self.document_id = document_id
        self.text = text
        self.filename = filename
        self.uploaded_at = datetime.now()
        self.expires_at = expires_at or (datetime.now() + DEFAULT_SESSION_EXPIRY)

    def is_expired(self) -> bool:
        """Check if the document session has expired."""
        return datetime.now() > self.expires_at

    def time_until_expiry(self) -> timedelta:
        """Get time remaining until expiration."""
        return self.expires_at - datetime.now()


def generate_session_id() -> str:
    """Generate a unique session ID for a user session."""
    return str(uuid.uuid4())


def generate_document_id(session_id: str, filename: str) -> str:
    """Generate a unique document ID for an uploaded document."""
    timestamp = int(time.time())
    clean_filename = filename.replace(" ", "_").replace(".", "_")[:50]
    return f"upload_{session_id[:8]}_{clean_filename}_{timestamp}"


async def store_uploaded_document(
    session_id: str,
    text: str,
    filename: str,
    jurisdiction: str = "User Upload",
    expires_in: timedelta | None = None,
) -> dict:
    """Store an uploaded document temporarily.

    Args:
        session_id: Unique session ID for the user.
        text: Extracted text from the uploaded document.
        filename: Original filename.
        jurisdiction: Jurisdiction/jurisdiction for the document.
        expires_in: Time until expiration. Defaults to 24 hours.

    Returns:
        dict: Document metadata with document_id, session_id, expires_at.

    """
    document_id = generate_document_id(session_id, filename)
    expires_at = datetime.now() + (expires_in or DEFAULT_SESSION_EXPIRY)

    _uploaded_documents[session_id] = {
        "document_id": document_id,
        "text": text,
        "filename": filename,
        "jurisdiction": jurisdiction,
        "uploaded_at": datetime.now().isoformat(),
        "expires_at": expires_at.isoformat(),
    }

    logger.info(
        f"Stored uploaded document: session={session_id[:8]}, "
        f"doc_id={document_id}, expires_at={expires_at}"
    )

    try:
        await _store_in_db_for_rag(session_id, document_id, text, filename, jurisdiction, expires_at)
    except Exception as e:
        logger.warning(f"Failed to store document in session collection: {e}")

    return {
        "session_id": session_id,
        "document_id": document_id,
        "expires_at": expires_at.isoformat(),
        "expires_in_seconds": int((expires_at - datetime.now()).total_seconds()),
    }


async def _store_in_db_for_rag(
    session_id: str,
    document_id: str,
    text: str,
    filename: str,
    jurisdiction: str,
    expires_at: datetime,
) -> None:
    """Store document in isolated session collection for RAG queries.

    Creates a separate Qdrant collection per session to ensure complete
    data isolation. The document is stored ONLY in the session collection,
    not in the main legal documents collection.
    """
    try:
        session_store = SessionVectorStore(session_id=session_id)
        await session_store.create_collection()
        
        num_chunks = await session_store.ingest_document(text=text, filename=filename)
        
        logger.info(
            f"Stored document in isolated session collection: "
            f"session={session_id[:8]}, chunks={num_chunks}, collection={session_store.collection_name}"
        )

    except Exception as e:
        logger.error(f"Failed to store document in session collection {session_id[:8]}: {e}")
        raise


def get_uploaded_document(session_id: str) -> dict | None:
    """Get an uploaded document by session ID.

    Args:
        session_id: Session ID.

    Returns:
        dict: Document data or None if not found/expired.

    """
    if session_id not in _uploaded_documents:
        return None

    doc_data = _uploaded_documents[session_id]
    expires_at = datetime.fromisoformat(doc_data["expires_at"])

    if datetime.now() > expires_at:
        delete_session(session_id)
        return None

    return doc_data


def get_document_id_from_session(session_id: str) -> str | None:
    """Get document ID from session ID for filtering queries.

    Args:
        session_id: Session ID.

    Returns:
        str: Document ID prefix or None if not found.

    """
    doc_data = get_uploaded_document(session_id)
    if doc_data:
        return doc_data["document_id"]
    return None


def delete_session(session_id: str) -> bool:
    """Delete a session and clean up associated data.

    Args:
        session_id: Session ID to delete.

    Returns:
        bool: True if deleted, False if not found.

    """
    if session_id not in _uploaded_documents:
        return False

    doc_data = _uploaded_documents[session_id]
    document_id = doc_data["document_id"]

    del _uploaded_documents[session_id]

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(_delete_from_db(session_id))
        else:
            asyncio.run(_delete_from_db(session_id))
    except RuntimeError:
        asyncio.run(_delete_from_db(session_id))

    logger.info(f"Deleted session: {session_id[:8]}, document_id={document_id}")
    return True


async def _delete_from_db(session_id: str) -> None:
    """Delete session collection from Qdrant."""
   
    try:
        session_store = SessionVectorStore(session_id=session_id)
        await session_store.delete_collection()
        logger.info(f"Deleted session collection for session: {session_id[:8]}")
    except Exception as e:
        logger.error(f"Error deleting session collection: {e}")


async def cleanup_expired_sessions() -> None:
    """Background task to clean up expired sessions."""
    while True:
        try:
            expired_sessions = []
            for session_id, doc_data in _uploaded_documents.items():
                expires_at = datetime.fromisoformat(doc_data["expires_at"])
                if datetime.now() > expires_at:
                    expired_sessions.append(session_id)

            for session_id in expired_sessions:
                delete_session(session_id)

            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

            await asyncio.sleep(3600)

        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
            await asyncio.sleep(3600)


def start_cleanup_task() -> None:
    """Start the background cleanup task."""
    global _cleanup_task
    if _cleanup_task is None or _cleanup_task.done():
        _cleanup_task = asyncio.create_task(cleanup_expired_sessions())
        logger.info("Started background cleanup task for expired sessions")

