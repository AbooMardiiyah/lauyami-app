import asyncio

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from src.api.models.api_models import (
    AskRequest,
    AskStreamingResponse,
    SearchResult,
    UniqueTitleRequest,
    UniqueTitleResponse,
)
from src.api.services.generation_service import get_streaming_function 
from src.api.services.search_service import query_unique_titles, query_with_filters

router = APIRouter()


@router.post("/unique-titles", response_model=UniqueTitleResponse)
async def search_unique(request: Request, params: UniqueTitleRequest):
    """Returns unique article titles based on a query and optional filters.

    Deduplicates results by article title.

    Args:
        request: FastAPI request object.
        params: UniqueTitleRequest with search parameters.

    Returns:
        UniqueTitleResponse: List of unique titles.

    """
    results = await query_unique_titles(
        request=request,
        query_text=params.query_text,
        jurisdiction=params.jurisdiction,
        document_title=params.document_title,
        title_keywords=params.title_keywords,
        limit=params.limit,
    )
    return {"results": results}

@router.post("/ask/stream", response_model=AskStreamingResponse)
async def ask_with_generation_stream(request: Request, ask: AskRequest):
    """Streaming question-answering endpoint using vector search and LLM.

    Workflow:
        1. Retrieve relevant documents (possibly duplicate titles for richer context).
        2. Stream generated answer with the selected LLM provider.

    Args:
        request: FastAPI request object.
        ask: AskRequest with query, provider, and limit.

    Returns:
        StreamingResponse: Yields text chunks as plain text.

    """
    results: list[SearchResult] = await query_with_filters(
        request,
        query_text=ask.query_text,
        session_id=ask.session_id,
        jurisdiction=ask.jurisdiction,
        document_title=ask.document_title,
        title_keywords=ask.title_keywords,
        limit=ask.limit,
    )

    stream_func = get_streaming_function(
        provider=ask.provider, query=ask.query_text, contexts=results, selected_model=ask.model, language=ask.language
    )

    async def stream_generator():
        async for delta in stream_func():
            yield delta
            await asyncio.sleep(0)  

    return StreamingResponse(stream_generator(), media_type="text/plain")
