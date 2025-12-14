from collections.abc import AsyncGenerator, Callable

try:
    import opik
    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False
    # No-op decorator when opik is not available
    class opik:
        @staticmethod
        def track(name=None, **kwargs):
            def decorator(func):
                return func
            return decorator

from src.api.models.api_models import SearchResult
from src.api.models.provider_models import MODEL_REGISTRY
from src.api.services.providers.natlas_service import stream_natlas
from src.api.services.providers.openai_service import stream_openai
from src.api.services.providers.utils.prompts import build_research_prompt
from src.utils.logger_util import setup_logging

logger = setup_logging()


@opik.track(name="get_streaming_function")
def get_streaming_function(
    provider: str,
    query: str,
    contexts: list[SearchResult],
    selected_model: str | None = None,
) -> Callable[[], AsyncGenerator[str, None]]:
    """Get a streaming function for the specified LLM provider.

    Args:
        provider (str): The LLM provider to use ("natlas"). Defaults to "natlas".
        query (str): The user's research query.
        contexts (list[SearchResult]): List of context documents with metadata.

    Returns:
        Callable[[], AsyncGenerator[str, None]]: A function that returns an async generator yielding
        response chunks.

    """
    prompt = build_research_prompt(contexts, query=query)
    provider_lower = provider.lower()
    config = MODEL_REGISTRY.get_config(provider_lower)
    logger.info(f"Using model config: {config}")

    async def stream_gen() -> AsyncGenerator[str, None]:
        """Asynchronous generator that streams response chunks from the specified provider.

        Yields:
            str: The next chunk of the response.

        """
        buffer = []  # collect all chunks here

        if provider_lower == "openai":
            async for chunk in stream_openai(prompt, config=config):
                buffer.append(chunk)
                yield chunk

        elif provider_lower == "natlas":
            async for chunk in stream_natlas(prompt, config=config):
                buffer.append(chunk)
                yield chunk

        else:
            raise ValueError(f"Unknown provider: {provider}. Only 'openai' and 'natlas' are supported.")

    return stream_gen
