"""Text-to-Speech service using YarnGPT API for Nigerian languages with chunking support."""

import asyncio
import httpx
import re
from src.config import settings
from src.utils.logger_util import setup_logging

logger = setup_logging()


async def text_to_speech_chunked(
    text: str,
    language: str = "en",
    voice: str | None = None,
    response_format: str = "mp3",
    chunk_size: int = 500,
) -> list[bytes]:
    """Convert text to speech in chunks for better performance.
    
    Splits text into smaller chunks and generates audio for each chunk.
    This provides faster initial response and better UX.
    
    Args:
        text: Text to convert to speech
        language: Language code (yo, ha, ig, en)
        voice: Specific voice name
        response_format: Audio format (mp3, wav, opus, flac)
        chunk_size: Maximum characters per chunk (default 500)
    
    Returns:
        list[bytes]: List of audio file bytes for each chunk
    """
    # Split text into sentences first
    sentences = _split_into_sentences(text)
    
    # Group sentences into chunks
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    logger.info(f"Split text into {len(chunks)} chunks for TTS")
    
    audio_chunks = []
    for i in range(0, len(chunks), 3):
        batch = chunks[i:i+3]
        batch_audio = await asyncio.gather(*[
            text_to_speech(chunk, language, voice, response_format)
            for chunk in batch
        ])
        audio_chunks.extend(batch_audio)
    
    return audio_chunks


def _split_into_sentences(text: str) -> list[str]:
    """Split text into sentences for better TTS chunking."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


async def text_to_speech(
    text: str,
    language: str = "en",
    voice: str | None = None,
    response_format: str = "mp3",
) -> bytes:
    """Convert text to speech using YarnGPT API.
    
    Supports Nigerian voices in multiple languages.
    
    Args:
        text: Text to convert to speech (max 2000 characters)
        language: Language code (yo, ha, ig, en) - used to select appropriate voice
        voice: Specific voice name. If None, uses default for language.
        response_format: Audio format (mp3, wav, opus, flac). Defaults to mp3.
    
    Returns:
        bytes: Audio file bytes
        
    Raises:
        ValueError: If text exceeds max length or API key not configured
        httpx.HTTPError: If the TTS service request fails
    """
    if not settings.yarngpt_api_key:
        logger.error("YarnGPT API key not configured!")
        logger.error(f"Settings yarngpt object: {settings.yarngpt}")
        raise ValueError(
            "YarnGPT API key not configured. Set YARNGPT__API_KEY in .env (with double underscore)"
        )
    
    if len(text) > 2000:
        logger.warning(f"Text too long ({len(text)} chars), truncating to 2000")
        text = text[:2000]

    default_voices = {
        "yo": "Wura",      
        "ha": "Zainab",    
        "ig": "Chinenye", 
        "en": "Idera",   
    }
    
    if not voice:
        voice = default_voices.get(language, "Idera")
    
    logger.info(
        f"TTS request: language={language}, voice={voice}, "
        f"format={response_format}, text_length={len(text)}"
    )
    
    payload = {
        "text": text,
        "voice": voice,
        "response_format": response_format,
    }
    
    headers = {
        "Authorization": f"Bearer {settings.yarngpt_api_key}",
        "Content-Type": "application/json",
    }
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:  
            logger.info(f"Sending request to {settings.yarngpt_api_url}")
            # Removed payload log to prevent exposing user text
            logger.debug(f"TTS request: language={language}, voice={voice}, text_length={len(text)}")
            logger.info(f"Using API key: {settings.yarngpt_api_key[:20]}...")
            
            response = await client.post(
                settings.yarngpt_api_url,
                json=payload,
                headers=headers,
            )
            
            logger.info(f"YarnGPT response status: {response.status_code}")
            
            if response.status_code != 200:
                error_text = response.text
                # Sanitized error log to prevent exposing sensitive data
                logger.error(f"YarnGPT error response (status {response.status_code}): {error_text[:200] if len(error_text) > 200 else error_text}")
                raise ValueError(f"YarnGPT API returned {response.status_code}: {error_text}")
            
            response.raise_for_status()
            
            audio_bytes = response.content
            logger.info(
                f"TTS completed: received {len(audio_bytes)} bytes "
                f"({len(audio_bytes) / 1024:.1f} KB)"
            )
            
            return audio_bytes
    
    except httpx.TimeoutException as e:
        logger.error(f"YarnGPT API timeout: {e}")
        raise ValueError("YarnGPT API request timed out. The service might be slow or unavailable.")
    except httpx.HTTPStatusError as e:
        logger.error(f"YarnGPT HTTP error: {e}")
        logger.error(f"Response status: {e.response.status_code}")
        # Sanitized error log to prevent exposing sensitive data
        error_body = e.response.text[:200] if len(e.response.text) > 200 else e.response.text
        logger.error(f"Response body (truncated): {error_body}")
        raise ValueError(f"YarnGPT API error ({e.response.status_code}): {e.response.text}")
    except httpx.HTTPError as e:
        logger.error(f"YarnGPT TTS connection error: {type(e).__name__}: {str(e)}")
        raise ValueError(f"Failed to connect to YarnGPT API: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected TTS error: {type(e).__name__}: {str(e)}")
        raise


def get_available_voices() -> dict[str, dict[str, str]]:
    """Get mapping of language codes to recommended voices.
    
    Returns:
        dict: Mapping of language codes to voice info
    """
    return {
        "yo": {"voice": "Wura", "description": "Young, sweet (Yoruba)"},
        "ha": {"voice": "Zainab", "description": "Soothing, gentle (Hausa)"},
        "ig": {"voice": "Chinenye", "description": "Engaging, warm (Igbo)"},
        "en": {"voice": "Idera", "description": "Melodic, gentle (English)"},
    }

YARNGPT_VOICES = {
    "Idera": "Melodic, gentle",
    "Emma": "Authoritative, deep",
    "Zainab": "Soothing, gentle",
    "Osagie": "Smooth, calm",
    "Wura": "Young, sweet",
    "Jude": "Warm, confident",
    "Chinenye": "Engaging, warm",
    "Tayo": "Upbeat, energetic",
    "Regina": "Mature, warm",
    "Femi": "Rich, reassuring",
    "Adaora": "Warm, Engaging",
    "Umar": "Calm, smooth",
    "Mary": "Energetic, youthful",
    "Nonso": "Bold, resonant",
    "Remi": "Melodious, warm",
    "Adam": "Deep, Clear",
}
