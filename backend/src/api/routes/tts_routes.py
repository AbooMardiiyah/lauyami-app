"""API routes for Text-to-Speech using YarnGPT."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from src.api.services.tts_service import text_to_speech, get_available_voices
from src.utils.logger_util import setup_logging

logger = setup_logging()

router = APIRouter()


class TTSRequest(BaseModel):
    """Request model for Text-to-Speech."""
    text: str = Field(..., description="Text to convert to speech (max 2000 chars)")
    language: str = Field(default="en", description="Language code: yo, ha, ig, en")
    voice: str | None = Field(default=None, description="Voice name (optional)")
    response_format: str = Field(default="mp3", description="Audio format: mp3, wav, opus, flac")


class VoicesResponse(BaseModel):
    """Response model for available voices."""
    voices: dict[str, dict[str, str]]


@router.post("/text-to-speech")
async def convert_text_to_speech(request: TTSRequest):
    """Convert text to speech using YarnGPT API.
    
    Args:
        request: TTSRequest with text, language, voice, and format
        
    Returns:
        Audio file as binary response
    """
    logger.info(
        f"TTS request: language={request.language}, voice={request.voice}, "
        f"format={request.response_format}, text_length={len(request.text)}"
    )
    
    try:
        text_to_convert = request.text
    
        if len(request.text) > 500:
            logger.info(f"Text is long ({len(request.text)} chars), using first 500 chars")
            text_to_convert = request.text[:500]
        
        audio_bytes = await text_to_speech(
            text=text_to_convert,
            language=request.language,
            voice=request.voice,
            response_format=request.response_format,
        )
        
        media_types = {
            "mp3": "audio/mpeg",
            "wav": "audio/wav",
            "opus": "audio/opus",
            "flac": "audio/flac",
        }
        media_type = media_types.get(request.response_format, "audio/mpeg")
        
        return Response(
            content=audio_bytes,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename=speech.{request.response_format}"
            },
        )
    
    except ValueError as e:
        logger.error(f"TTS validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS conversion failed: {str(e)}")


@router.get("/voices", response_model=VoicesResponse)
async def get_voices():
    """Get available voices for each language.
    
    Returns:
        VoicesResponse: Mapping of language codes to voice info
    """
    return VoicesResponse(voices=get_available_voices())

