"""API routes for voice-based question-answering."""

import asyncio
import json
from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import StreamingResponse

from src.api.models.api_models import VoiceAskRequest, VoiceAskResponse
from src.api.services.asr_service import transcribe_audio
from src.api.services.generation_service import get_streaming_function
from src.api.services.search_service import query_with_filters
from src.utils.logger_util import setup_logging

logger = setup_logging()

router = APIRouter()


@router.post("/ask-with-voice") 
async def ask_with_voice(
    request: Request,
    audio_file: UploadFile = File(..., description="Audio file with voice question"),
    session_id: str | None = Form(default=None, description="Session ID to query against uploaded document"),
    language: str = Form(default="en", description="Language code: yo, ha, ig, en"),
    limit: int = Form(default=5, description="Number of context documents to retrieve"),
    provider: str = Form(default="natlas", description="LLM provider to use"),
):
    """Ask a question using voice (audio) and get a streaming answer.

    This endpoint:
    1. Transcribes the audio using N-ATLaS ASR models
    2. Searches the RAG system for relevant legal context
    3. Streams the answer using the LLM (N-ATLaS by default)

    Args:
        request: FastAPI request object (for vector store access).
        audio_file: Audio file with the user's voice question.
        language: Language code for ASR and response (yo, ha, ig, en). Defaults to "en".
        limit: Number of context documents to retrieve. Defaults to 5.
        provider: LLM provider to use. Defaults to "natlas".

    Returns:
        StreamingResponse: Streams metadata + answer chunks.

    """
    logger.info(f"Processing voice query (streaming): language={language}, provider={provider}")

    try:
        audio_bytes = await audio_file.read()
        transcribed_text, language_detected = await transcribe_audio(
            audio_bytes=audio_bytes, language_code=language
        )

        if not transcribed_text.strip():
            raise ValueError("No speech could be transcribed from the audio file")

        logger.info(
            f"Transcribed text ({language_detected}): {transcribed_text[:100]}..."
        )

        search_results = await query_with_filters(
            request=request,
            query_text=transcribed_text,
            session_id=session_id,
            feed_name="Lagos State Tenancy Law 2011",
            feed_author="Lagos State",
            limit=limit,
        )

        logger.info(f"Retrieved {len(search_results)} context documents")
        stream_func = get_streaming_function(
            provider=provider,
            query=transcribed_text,
            contexts=search_results,
        )
        
        async def voice_stream_generator():
            metadata = {
                "transcribed_text": transcribed_text,
                "language_detected": language_detected,
                "query": transcribed_text,
                "num_sources": len(search_results),
            }
            yield f"__metadata__:{json.dumps(metadata)}\n"
            
            async for chunk in stream_func():
                yield chunk
                await asyncio.sleep(0) 

        return StreamingResponse(voice_stream_generator(), media_type="text/plain")

    except Exception as e:
        logger.error(f"Error processing voice query: {e}")
        raise

