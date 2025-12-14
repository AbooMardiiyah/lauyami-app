"""N-ATLaS LLM provider service.

Provides integration with Modal-hosted N-ATLaS LLM (OpenAI-compatible API).
Supports Yoruba, Hausa, Igbo, and Nigerian Accented English.
"""

from collections.abc import AsyncGenerator

from openai import AsyncOpenAI

from src.api.models.provider_models import ModelConfig
from src.api.services.providers.utils.messages import build_messages
from src.config import settings
from src.utils.logger_util import setup_logging

logger = setup_logging()

# -----------------------
# N-ATLaS client (Modal-hosted)
# -----------------------
modal_settings = settings.modal

# Ensure base_url has /v1 if not already present (OpenAI client expects it)
llm_base_url = modal_settings.llm_base_url
if llm_base_url and not llm_base_url.endswith("/v1") and not llm_base_url.endswith("/v1/"):
    llm_base_url = f"{llm_base_url.rstrip('/')}/v1"

natlas_client = AsyncOpenAI(
    base_url=llm_base_url,
    api_key=modal_settings.llm_api_key,
    timeout=300.0,  # 5 minute timeout
)


async def generate_natlas(
    prompt: str, config: ModelConfig, language: str | None = None
) -> tuple[str, str, None]:
    """Generate a response from N-ATLaS LLM for a given prompt.

    Args:
        prompt (str): The input prompt.
        config (ModelConfig): The model configuration.
        language (str | None): Optional language code (yo, ha, ig, en) for context.

    Returns:
        tuple[str, str, None]: The generated response, model name, and None for finish reason.

    """
    if not modal_settings.llm_base_url:
        raise ValueError(
            "Modal LLM base URL not configured. Set MODAL__LLM_BASE_URL in .env"
        )

    try:
        logger.info(f"Calling N-ATLaS LLM at {llm_base_url} with model {modal_settings.llm_model_name}")
        
        resp = await natlas_client.chat.completions.create(
            model=modal_settings.llm_model_name,
            messages=build_messages(prompt),
            temperature=config.temperature,
            max_completion_tokens=config.max_completion_tokens,
            timeout=300.0,  # 5 minute timeout
        )

        model_used = modal_settings.llm_model_name
        content = resp.choices[0].message.content or ""

        logger.info(
            f"N-ATLaS generated response (language={language}, model={model_used}, length={len(content)})"
        )

        return content, model_used, None

    except Exception as e:
        error_msg = f"Error generating response from N-ATLaS: {e}"
        logger.error(error_msg, exc_info=True)
        raise ValueError(f"Failed to connect to N-ATLaS LLM service at {llm_base_url}. Please ensure the Modal service is deployed and running. Error: {str(e)}") from e


async def stream_natlas(
    prompt: str, config: ModelConfig, language: str | None = None
) -> AsyncGenerator[str, None]:
    """Stream a response from N-ATLaS LLM for a given prompt.

    Args:
        prompt (str): The input prompt.
        config (ModelConfig): The model configuration.
        language (str | None): Optional language code (yo, ha, ig, en) for context.

    Yields:
        str: Response chunks as they are generated.

    """
    if not modal_settings.llm_base_url:
        raise ValueError(
            "Modal LLM base URL not configured. Set MODAL__LLM_BASE_URL in .env"
        )

    try:
        logger.info(f"Calling N-ATLaS LLM at {llm_base_url} with model {modal_settings.llm_model_name}")
        
        stream = await natlas_client.chat.completions.create(
            model=modal_settings.llm_model_name,
            messages=build_messages(prompt),
            temperature=config.temperature,
            max_completion_tokens=config.max_completion_tokens,
            stream=True,
            timeout=300.0,  # 5 minute timeout
        )

        last_finish_reason = None
        chunk_count = 0
        async for chunk in stream:
            delta_text = getattr(chunk.choices[0].delta, "content", None)
            if delta_text:
                yield delta_text
                chunk_count += 1

            finish_reason = getattr(chunk.choices[0], "finish_reason", None)
            if finish_reason:
                last_finish_reason = finish_reason

        if last_finish_reason == "length":
            yield "__truncated__"

        logger.info(f"N-ATLaS streamed response completed (language={language}, chunks={chunk_count})")

    except Exception as e:
        error_msg = f"Error streaming response from N-ATLaS: {e}"
        logger.error(error_msg, exc_info=True)
        # Yield error message so frontend can display it
        yield f"__error__: Failed to connect to N-ATLaS LLM service. Please ensure the Modal service is deployed and running. Error: {str(e)}"
        # Don't re-raise, let the stream finish with the error message

