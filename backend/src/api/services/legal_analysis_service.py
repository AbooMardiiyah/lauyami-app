"""Legal analysis service for analyzing tenant agreements against Lagos State Tenancy Law 2011."""

import asyncio
from collections.abc import AsyncGenerator

from src.api.models.api_models import SearchResult
from src.api.services.search_service import query_with_filters
from src.api.services.generation_service import get_streaming_function  # generate_answer commented out (non-streaming)
from src.api.services.cache_service import get_cached_analysis, set_cached_analysis
from src.config import settings
from src.utils.logger_util import setup_logging

logger = setup_logging()


async def analyze_agreement_for_risks_stream(
    agreement_text: str,
    request,
    language: str = "en",
    session_id: str | None = None,
) -> AsyncGenerator[str, None]:
    """Stream analysis of a tenant agreement with caching and progress updates.

    Args:
        agreement_text (str): Extracted text from the uploaded agreement.
        request: FastAPI request object (needed for vector store access).
        language (str): Language code for response (yo, ha, ig, en). Defaults to "en".

    Yields:
        str: Analysis text chunks and progress updates as they are generated.

    """
    cached_analysis = get_cached_analysis(agreement_text, language)
    if cached_analysis:
        logger.info("Returning cached analysis")
        yield "__progress__:Loading from cache...\n"
        yield cached_analysis
        return
    search_queries = [
        ("tenant rights advance rent payment obligations", "rights"),
        ("warning signs predatory clauses unlawful terms", "warnings"),
        ("notice period eviction termination requirements", "procedures"),
    ]

    yield "__progress__:Starting analysis...\n"

    async def fetch_context(query_info: tuple[str, str]) -> tuple[str, list[SearchResult]]:
        query, label = query_info
        try:
            contexts = await query_with_filters(
                request=request,
                query_text=query,
                session_id=session_id,
                document_title="Lagos State Tenancy Law 2011",
                jurisdiction="Lagos State",
                limit=2, 
            )
            if contexts is None:
                return (label, [])
            if not isinstance(contexts, list):
                logger.warning(f"Query returned non-list type for '{query}': {type(contexts)}")
                return (label, [])
            return (label, contexts)
        except Exception as e:
            logger.warning(f"Error searching for context '{query}': {e}")
            return (label, [])

    logger.info(f"Starting {len(search_queries)} RAG queries sequentially to reduce memory usage (2 chunks each)")
    results = []
    for query_info in search_queries:
        _, label = query_info
        yield f"__progress__:Analyzing {label}...\n"
        try:
            result = await asyncio.wait_for(
                fetch_context(query_info),
                timeout=15.0  
            )
            results.append(result)
            yield f"__progress__:✓ {label.capitalize()} analyzed\n"
        except asyncio.TimeoutError:
            logger.error(f"RAG query '{label}' timed out after 15 seconds")
            results.append((label, []))
            yield f"__progress__:⚠ {label.capitalize()} timed out\n"
        except Exception as e:
            logger.error(f"Error during RAG query '{label}': {e}", exc_info=True)
            results.append((label, []))
            yield f"__progress__:⚠ {label.capitalize()} failed\n"
    
    for label, contexts in results:
        yield f"__progress__:✓ {label.capitalize()} analyzed\n"
        logger.info(f"Query '{label}' returned {len(contexts)} contexts")
    
    all_contexts: list[SearchResult] = []
    for label, contexts in results:
        all_contexts.extend(contexts)

    seen_document_ids = set()
    unique_contexts = []
    for ctx in all_contexts:
        if ctx.document_id and ctx.document_id not in seen_document_ids:
            seen_document_ids.add(ctx.document_id)
            unique_contexts.append(ctx)

    logger.info(f"Building legal analysis prompt (streaming) with {len(unique_contexts)} context chunks")
    
    analysis_prompt = f"""You are a legal assistant specializing in Lagos State Tenancy Law 2011. Review the tenant agreement and identify any clauses that violate or conflict with the law. Be concise and confident. Always analyze the SAME document the SAME way for consistency.

AGREEMENT TEXT:
{agreement_text[:8000]}

RELEVANT LEGAL PROVISIONS (Lagos State Tenancy Law 2011):
{chr(10).join([f"- {ctx.chunk_text[:500]}" for ctx in unique_contexts[:10]]) if unique_contexts else "- No specific legal provisions retrieved. Use your knowledge of Lagos State Tenancy Law 2011."}

**CRITICAL: You MUST format your response EXACTLY as shown below. Do NOT deviate from this format:**

Based on your tenancy agreement (Section X), [one clear sentence about what it says].

✅ **Your Right:** [One clear sentence about the tenant's right under the law]

⚠️ **Warning Found:** [One clear sentence about the problematic clause]

🚨 **Predatory clause detected:** [One clear sentence if it's a predatory clause]

✅ **Your Right:** [Another right if found]

⚠️ **Warning Found:** [Another warning if found]

**RULES:**
- Put each finding on its OWN line
- Start each line with EXACTLY one of: ✅ **Your Right:** OR ⚠️ **Warning Found:** OR 🚨 **Predatory clause detected:**
- Keep each to ONE sentence
- Reference specific sections (e.g., "Section 12", "Clause 4.4(a)")
- Maximum 3-4 key findings
- Be consistent for the same document

Please respond in {'Yoruba' if language == 'yo' else 'Hausa' if language == 'ha' else 'Igbo' if language == 'ig' else 'English'}."""

    logger.debug(f"Legal analysis prompt built (streaming) with {len(unique_contexts)} context chunks, agreement text length: {len(agreement_text)}")

    yield "__progress__:Generating analysis...\n"

    try:
        provider = "natlas"
        
        if not settings.modal.llm_base_url:
            raise ValueError("N-ATLaS LLM base URL not configured. Please set MODAL__LLM_BASE_URL in .env")
        
        stream_func = get_streaming_function(
            provider=provider,
            query=analysis_prompt,
            contexts=unique_contexts,
        )

        full_analysis = ""
        
        async for chunk in stream_func():
            full_analysis += chunk
            yield chunk
        
        set_cached_analysis(agreement_text, full_analysis, language)
        logger.info("Analysis cached successfully")

    except Exception as e:
        logger.error(f"Error streaming legal analysis: {e}")
        yield f"__error__: {str(e)}"

