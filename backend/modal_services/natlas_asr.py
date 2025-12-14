"""Deploy N-ATLaS ASR models on Modal for multilingual speech recognition.

This service provides speech-to-text for 4 languages:
- Yoruba (yo)
- Hausa (ha)
- Igbo (ig)
- Nigerian Accented English (en)

All 4 models run on a single A10G GPU for efficiency.

Deploy: modal deploy modal_services/natlas_asr.py
Usage: https://your-workspace--natlas-asr-multilingual-api-transcribe.modal.run
"""

import os
import modal
import base64
import time
import torch
import tempfile
import librosa

from transformers import pipeline
from huggingface_hub import login
from fastapi import HTTPException
from loguru import logger


asr_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")  # Required for WebM and other audio formats
    .pip_install(
        "transformers",
        "torch",
        "accelerate",
        "librosa",
        "numpy",
        "soundfile",
        "fastapi[standard]",
        "huggingface_hub",
        "loguru",
    )
)

app = modal.App("natlas-asr-multilingual")

vol = modal.Volume.from_name("hf-hub-cache", create_if_missing=True)

hf_secret = modal.Secret.from_name("huggingface-secret")


@app.cls(
    image=asr_image,
    gpu="A10G",
    volumes={"/root/.cache/huggingface": vol},
    scaledown_window=300,  
    timeout=600,
    secrets=[hf_secret],
)
class NAtlasASR:
    @modal.enter()
    def load_models(self):
        
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            raise ValueError("HF_TOKEN not found in environment. Make sure the Modal secret 'huggingface-secret' contains HF_TOKEN.")

        login(token=hf_token)
        logger.success("Authenticated with Hugging Face")

        device = "cuda" if torch.cuda.is_available() else "cpu"

        logger.info("Loading N-ATLaS ASR models...")

        pipeline_kwargs = {
            "return_timestamps": True, 
        }
        
        self.pipelines = {
            "yo": pipeline(
                "automatic-speech-recognition",
                model="NCAIR1/Yoruba-ASR",
                device=device,
                token=hf_token,
                **pipeline_kwargs,
            ),
            "ha": pipeline(
                "automatic-speech-recognition",
                model="NCAIR1/Hausa-ASR",
                device=device,
                token=hf_token,
                **pipeline_kwargs,
            ),
            "ig": pipeline(
                "automatic-speech-recognition",
                model="NCAIR1/Igbo-ASR",
                device=device,
                token=hf_token,
                **pipeline_kwargs,
            ),
            "en": pipeline(
                "automatic-speech-recognition",
                model="NCAIR1/NigerianAccentedEnglish",
                device=device,
                token=hf_token,
                **pipeline_kwargs,
            ),
        }
        logger.success("All N-ATLaS models loaded!")

    @modal.method()
    def transcribe_audio(self, audio_bytes: bytes, lang_code: str) -> str:

        if lang_code not in self.pipelines:
            error_msg = f"Error: Language '{lang_code}' not supported. Use 'yo', 'ha', 'ig', or 'en'."
            logger.error(error_msg)
            raise ValueError(error_msg)

        transcriber = self.pipelines[lang_code]
        logger.info(f"Transcribing audio: {len(audio_bytes)} bytes, language={lang_code}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".audio") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name

        try:
            logger.info(f"Loading audio from temp file: {tmp_path}")
            data, samplerate = librosa.load(tmp_path, sr=16000, mono=True)
            logger.info(f"Audio loaded: shape={data.shape}, samplerate={samplerate}Hz, duration={len(data)/samplerate:.2f}s")

            if len(data) == 0:
                raise ValueError("Audio file is empty or could not be decoded")

            logger.info("Running transcription...")
            
            result = transcriber(data)
            if isinstance(result, dict):
                transcribed_text = result.get("text", "")
                if not transcribed_text and "chunks" in result:
                    transcribed_text = " ".join(
                        chunk.get("text", "") for chunk in result["chunks"]
                    )
            else:
                transcribed_text = str(result)
            
            logger.info(f"Transcription result: {transcribed_text[:100]}...")
            
            return transcribed_text
        except Exception as e:
            logger.error(f"Error in transcribe_audio: {e}", exc_info=True)
            raise
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                logger.debug(f"Cleaned up temp file: {tmp_path}")


@app.function(image=asr_image)
@modal.fastapi_endpoint(method="POST")
def api_transcribe(item: dict):
    """API endpoint for transcription.

    Expects JSON: {"audio_base64": "...", "language": "yo"}
    Returns: {"text": "...", "language_used": "yo"}
    """
    request_start = time.time()
    
    try:
        language = item.get("language", "en") 
        audio_base64 = item.get("audio_base64")
        
        if not audio_base64:
            logger.error("Missing audio_base64 in request")
            raise HTTPException(status_code=400, detail="Missing audio_base64 in request")
        
        decode_start = time.time()
        audio_data = base64.b64decode(audio_base64)
        decode_time = time.time() - decode_start
        logger.info(f"Decoded audio: {len(audio_data)} bytes in {decode_time:.2f}s, language={language}")

        if len(audio_data) == 0:
            logger.error("Empty audio data received")
            raise HTTPException(status_code=400, detail="Empty audio data")

        transcribe_start = time.time()
        model_instance = NAtlasASR()
        text = model_instance.transcribe_audio.remote(audio_data, language)
        transcribe_time = time.time() - transcribe_start
        
        if not text or not text.strip():
            logger.warning("Empty transcription result")
            text = ""
        
        total_time = time.time() - request_start
        logger.info(
            f"Transcription completed: language={language}, "
            f"text_length={len(text)}, transcribe_time={transcribe_time:.2f}s, "
            f"total_time={total_time:.2f}s"
        )
        return {"text": text, "language_used": language}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in api_transcribe: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")

