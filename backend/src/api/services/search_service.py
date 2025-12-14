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

from fastapi import Request
from qdrant_client.models import (
    FieldCondition,
    Filter,
    Fusion,
    FusionQuery,
    MatchText,
    MatchValue,
    Prefetch,
)

from src.api.models.api_models import SearchResult
from src.infrastructure.qdrant.qdrant_vectorstore import AsyncQdrantVectorStore
from src.utils.logger_util import setup_logging
from src.api.services.session_vectorstore_service import SessionVectorStore

logger = setup_logging()


@opik.track(name="query_with_filters")
async def query_with_filters(
    request: Request,
    query_text: str = "",
    session_id: str | None = None,
    feed_author: str | None = None,
    feed_name: str | None = None,
    title_keywords: str | None = None,
    limit: int = 5,
) -> list[SearchResult]:
    """Query the vector store with optional filters and return search results.

    Performs a hybrid dense + sparse search on Qdrant and applies filters based
    on feed author, feed name, and title keywords. Results are deduplicated by point ID.

    Args:
        request (Request): FastAPI request object containing the vector store in app.state.
        query_text (str): Text query to search for.
        feed_author (str | None): Optional filter for the feed author.
        feed_name (str | None): Optional filter for the feed name.
        title_keywords (str | None): Optional filter for title keywords.
        limit (int): Maximum number of results to return.

    Returns:
        list[SearchResult]:
            List of search results containing title, feed info, URL, chunk text, and score.

    """
    session_results: list[SearchResult] = []
    
    if session_id:
        try:
            session_store = SessionVectorStore(session_id=session_id)
            session_chunks = await session_store.query(query_text, limit=limit)
            
            if session_chunks is None:
                session_chunks = []
            if not isinstance(session_chunks, list):
                logger.warning(f"Session query returned non-list type: {type(session_chunks)}")
                session_chunks = []
            for chunk in session_chunks:
                session_results.append(
                    SearchResult(
                        title=chunk["title"],
                        feed_author=chunk["feed_author"],
                        feed_name=chunk["feed_name"],
                        article_author=chunk["article_authors"],
                        url=chunk["url"],
                        chunk_text=chunk["chunk_text"],
                        score=chunk["score"],
                    )
                )
            
            logger.info(f"Found {len(session_results)} results from session collection")
        except Exception as e:
            logger.warning(f"Failed to query session collection: {e}")
    
    vectorstore: AsyncQdrantVectorStore = request.app.state.vectorstore
    dense_vector = vectorstore.dense_vectors([query_text])[0]
    sparse_vector = vectorstore.sparse_vectors([query_text])[0]

    conditions: list[FieldCondition] = []
    if feed_author:
        conditions.append(FieldCondition(key="feed_author", match=MatchValue(value=feed_author)))
    if feed_name:
        conditions.append(FieldCondition(key="feed_name", match=MatchValue(value=feed_name)))
    if title_keywords:
        conditions.append(
            FieldCondition(key="title", match=MatchText(text=title_keywords.strip().lower()))
        )

    query_filter = Filter(must=conditions) if conditions else None  # type: ignore

    fetch_limit = max(1, limit) * 100
    logger.info(f"Fetching up to {fetch_limit} points for unique Ids.")

    try:
    response = await vectorstore.client.query_points(
        collection_name=vectorstore.collection_name,
        query=FusionQuery(fusion=Fusion.RRF),
        prefetch=[
            Prefetch(query=dense_vector, using="Dense", limit=fetch_limit, filter=query_filter),
            Prefetch(query=sparse_vector, using="Sparse", limit=fetch_limit, filter=query_filter),
        ],
        query_filter=query_filter,
        limit=fetch_limit,
    )
    except Exception as e:
        logger.warning(f"Error querying reference law collection: {e}")
        response = None
    seen_ids: set[str] = set()
    results: list[SearchResult] = []
    if response and hasattr(response, "points") and response.points:
    for point in response.points:
        if point.id in seen_ids:
            continue
        seen_ids.add(point.id)  # type: ignore
        payload = point.payload or {}
        results.append(
            SearchResult(
                title=payload.get("title", ""),
                feed_author=payload.get("feed_author"),
                feed_name=payload.get("feed_name"),
                article_author=payload.get("article_authors"),
                url=payload.get("url"),
                chunk_text=payload.get("chunk_text"),
                score=point.score,
            )
        )

    results = results[:limit]
    
    combined_results = session_results + results
    
    seen_urls = set()
    final_results = []
    for result in combined_results:
        if result.url and result.url not in seen_urls:
            seen_urls.add(result.url)
            final_results.append(result)
    
    final_results.sort(key=lambda x: x.score or 0.0, reverse=True)
    final_results = final_results[:limit]
    
    logger.info(
        f"Returning {len(final_results)} combined results "
        f"({len(session_results)} from session, {len(results)} from reference law) "
        f"for query '{query_text}'"
    )
    
    return final_results


@opik.track(name="query_unique_titles")
async def query_unique_titles(
    request: Request,
    query_text: str,
    feed_author: str | None = None,
    feed_name: str | None = None,
    title_keywords: str | None = None,
    limit: int = 5,
) -> list[SearchResult]:
    """Query the vector store and return only unique titles.

    Performs a hybrid dense + sparse search with optional filters and dynamically
    increases the fetch limit to account for duplicates. Deduplicates results
    by article title.

    Args:
        request (Request): FastAPI request object containing the vector store in app.state.
        query_text (str): Text query to search for.
        feed_author (str | None): Optional filter for the feed author.
        feed_name (str | None): Optional filter for the feed name.
        title_keywords (str | None): Optional filter for title keywords.
        limit (int): Maximum number of unique results to return.

    Returns:
        list[SearchResult]:
            List of unique search results containing title, feed info, URL, chunk text, and score.

    """
    vectorstore: AsyncQdrantVectorStore = request.app.state.vectorstore
    dense_vector = vectorstore.dense_vectors([query_text])[0]
    sparse_vector = vectorstore.sparse_vectors([query_text])[0]

    # Build filter conditions
    conditions: list[FieldCondition] = []
    if feed_author:
        conditions.append(FieldCondition(key="feed_author", match=MatchValue(value=feed_author)))
    if feed_name:
        conditions.append(FieldCondition(key="feed_name", match=MatchValue(value=feed_name)))
    if title_keywords:
        conditions.append(
            FieldCondition(key="title", match=MatchText(text=title_keywords.strip().lower()))
        )

    query_filter = Filter(must=conditions) if conditions else None  # type: ignore

    fetch_limit = max(1, limit) * 280
    logger.info(f"Fetching up to {fetch_limit} points for unique titles.")

    try:
    response = await vectorstore.client.query_points(
        collection_name=vectorstore.collection_name,
        query=FusionQuery(fusion=Fusion.RRF),
        prefetch=[
            Prefetch(query=dense_vector, using="Dense", limit=fetch_limit, filter=query_filter),
            Prefetch(query=sparse_vector, using="Sparse", limit=fetch_limit, filter=query_filter),
        ],
        query_filter=query_filter,
        limit=fetch_limit,
    )
    except Exception as e:
        logger.warning(f"Error querying reference law collection: {e}")
        response = None

    # Deduplicate by title
    seen_titles: set[str] = set()
    results: list[SearchResult] = []
    if response and hasattr(response, "points") and response.points:
    for point in response.points:
        payload = point.payload or {}
        title = payload.get("title")
        if not title or title in seen_titles:
            continue
        seen_titles.add(title)
        results.append(
            SearchResult(
                title=title,
                feed_author=payload.get("feed_author"),
                feed_name=payload.get("feed_name"),
                article_author=payload.get("article_authors"),
                url=payload.get("url"),
                chunk_text=payload.get("chunk_text"),
                score=point.score,
            )
        )
        if len(results) >= limit:
            break

    logger.info(f"Returning {len(results)} unique title results for matching query '{query_text}'")

    # logger.info(f"results: {results}")
    return results
