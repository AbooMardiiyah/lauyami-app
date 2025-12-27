"""API routes for tenant agreement upload and analysis."""

import asyncio
import json
from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import StreamingResponse
from src.api.services.document_storage_service import (
    generate_session_id,
    store_uploaded_document,
    delete_session
)
from src.api.services.legal_analysis_service import (
    analyze_agreement_for_risks_stream,
)
from src.api.services.ocr_service import extract_text_from_file
from src.utils.logger_util import setup_logging

logger = setup_logging()

router = APIRouter()


@router.post("/upload-agreement/stream")
async def upload_and_analyze_agreement_stream(
    request: Request,
    file: UploadFile = File(..., description="Agreement file (PDF or image)"),
    language: str = Form(default="en", description="Language code: yo, ha, ig, en"),
    session_id: str | None = Form(default=None, description="Optional: Existing session ID"),
):
    """Upload a tenant agreement and stream the analysis.

    Same as /upload-agreement but streams the analysis response as it's generated.
    First yields session metadata, then streams the analysis text.

    Args:
        request: FastAPI request object (for vector store access).
        file: Uploaded file (PDF, JPG, PNG).
        language: Language code for response (yo, ha, ig, en). Defaults to "en".
        session_id: Optional session ID. If not provided, a new session will be created.

    Returns:
        StreamingResponse: Streams session metadata JSON, then analysis text chunks.

    """
    logger.info(f"Processing agreement upload (streaming): {file.filename}, language={language}")

    async def stream_generator():
        try:
            if not session_id:
                current_session_id = generate_session_id()
                logger.info(f"Generated new session: {current_session_id[:8]}...")
            else:
                current_session_id = session_id

            extracted_text = await extract_text_from_file(file)

            if not extracted_text.strip():
                yield f"__error__: No text could be extracted from the uploaded file\n"
                return

            logger.info(f"Extracted {len(extracted_text)} characters from {file.filename}")

            storage_result = await store_uploaded_document(
                session_id=current_session_id,
                text=extracted_text,
                filename=file.filename or "uploaded_agreement",
                jurisdiction="User Upload",
            )
            document_id = storage_result["document_id"]

            logger.info(f"Stored document temporarily: session={current_session_id[:8]}, doc_id={document_id}")

            metadata = {
                "session_id": current_session_id,
                "document_id": document_id,
                "expires_at": storage_result["expires_at"],
                "filename": file.filename or "uploaded_agreement",
            }
            metadata_json = json.dumps(metadata)
            yield f"__metadata__:{metadata_json}\n"
            yield "Starting analysis...\n"

            try:
                logger.info("Starting to stream analysis from LLM")
                async for chunk in analyze_agreement_for_risks_stream(
                    agreement_text=extracted_text,
                    request=request,
                    language=language,
                    session_id=current_session_id,
                ):
                    if chunk:
                        yield chunk
                    await asyncio.sleep(0.01)  
                    
            except Exception as stream_error:
                logger.error(f"Error during analysis streaming: {stream_error}", exc_info=True)
                error_msg = f"__error__: Analysis failed: {str(stream_error)}"
                yield f"{error_msg}\n"
                return

        except Exception as e:
            logger.error(f"Error processing agreement upload (streaming): {e}", exc_info=True)
            yield f"__error__: Upload processing failed: {str(e)}\n"
            return

    return StreamingResponse(stream_generator(), media_type="text/plain")


@router.delete("/session/{session_id}")
async def delete_session_endpoint(session_id: str):
    """Delete a session and all associated uploaded documents.

    This endpoint immediately deletes the session and all associated data,
    including database entries and embeddings. Useful for privacy compliance.

    Args:
        session_id: Session ID to delete.

    Returns:
        dict: Success message.

    """
    deleted = delete_session(session_id)
    if deleted:
        return {"message": "Session deleted successfully", "session_id": session_id}
    else:
        return {"message": "Session not found", "session_id": session_id}

