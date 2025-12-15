"""ASR (Automatic Speech Recognition) service for N-ATLaS multilingual transcription.

Supports:
- Yoruba (yo)
- Hausa (ha)
- Igbo (ig)
- Nigerian Accented English (en)
"""

import base64

import httpx

from src.config import settings
from src.utils.logger_util import setup_logging

logger = setup_logging()

# -----------------------
# ASR Service Configuration
# -----------------------
modal_settings = settings.modal


async def transcribe_audio(
    audio_bytes: bytes, language_code: str = "en"
) -> tuple[str, str]:
    """Transcribe audio using N-ATLaS ASR models on Modal.

    Args:
        audio_bytes (bytes): Audio file bytes (WAV, MP3, etc.)
        language_code (str): Language code - 'yo' (Yoruba), 'ha' (Hausa),
            'ig' (Igbo), or 'en' (Nigerian Accented English). Defaults to 'en'.

    Returns:
        tuple[str, str]: Transcribed text and language used.

    Raises:
        ValueError: If language code is not supported or ASR URL is not configured.
        httpx.HTTPError: If the ASR service request fails.

    """
    if not modal_settings.asr_base_url:
        raise ValueError(
            "Modal ASR base URL not configured. Set MODAL__ASR_BASE_URL in .env"
        )

    # Validate language code
    supported = modal_settings.supported_languages
    if language_code not in supported:
        raise ValueError(
            f"Language code '{language_code}' not supported. "
            f"Supported codes: {list(supported.keys())}"
        )

    # Log audio size for debugging
    audio_size_mb = len(audio_bytes) / (1024 * 1024)
    logger.info(
        f"Starting ASR transcription: language={language_code}, "
        f"audio_size={audio_size_mb:.2f}MB"
    )

    # Encode audio to base64
    import time
    start_time = time.time()
    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
    encode_time = time.time() - start_time
    logger.debug(f"Audio encoding took {encode_time:.2f}s")

    payload = {
        "audio_base64": audio_base64,
        "language": language_code,
    }

    try:
        request_start = time.time()
        async with httpx.AsyncClient(timeout=180.0, follow_redirects=True) as client:
            response = await client.post(
                modal_settings.asr_base_url,
                json=payload,
                timeout=180.0, 
            )
            request_time = time.time() - request_start
            logger.info(f"ASR request completed in {request_time:.2f}s")
            
            response.raise_for_status()

            result = response.json()
            transcribed_text = result.get("text", "")
            language_used = result.get("language_used", language_code)

            total_time = time.time() - start_time
            logger.info(
                f"ASR transcription completed (language={language_used}, "
                f"text_length={len(transcribed_text)}, total_time={total_time:.2f}s)"
            )

            return transcribed_text, language_used

    except httpx.HTTPError as e:
        logger.error(f"ASR service HTTP error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in ASR transcription: {e}")
        raise


def get_supported_languages() -> dict[str, str]:
    """Get mapping of supported language codes to language names.

    Returns:
        dict[str, str]: Mapping of language codes to language names.

    """
    return modal_settings.supported_languages.copy()

