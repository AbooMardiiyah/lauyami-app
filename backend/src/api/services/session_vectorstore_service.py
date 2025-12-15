"""Session-based vector store service for user-uploaded documents.

Creates isolated Qdrant collections per session to ensure complete data isolation.
Each user session gets its own temporary collection that's deleted when the session ends.
"""

import hashlib
from src.config import settings
from src.infrastructure.qdrant.qdrant_vectorstore import AsyncQdrantVectorStore
from src.models.vectorstore_models import ArticleChunkPayload
from src.utils.logger_util import setup_logging
from src.utils.text_splitter import TextSplitter
from qdrant_client.models import Distance, models
from qdrant_client.models import Batch
from qdrant_client.models import Fusion, FusionQuery, Prefetch

logger = setup_logging()


def get_session_collection_name(session_id: str) -> str:
    """Get the Qdrant collection name for a user session.

    Args:
        session_id: Unique session ID.

    Returns:
        str: Collection name in format 'user_session_{session_id}'.

    """
    safe_session_id = session_id.replace("-", "_").replace(".", "_")[:50]
    return f"user_session_{safe_session_id}"


class SessionVectorStore:
    """Manages a temporary Qdrant collection for a user session.

    Each session gets its own isolated collection that stores embeddings
    for the user's uploaded document. The collection is deleted when
    the session ends.
    """

    def __init__(self, session_id: str, cache_dir: str | None = None):
        """Initialize a session vector store.

        Args:
            session_id: Unique session ID for the user.
            cache_dir: Optional cache directory for embedding models.

        """
        self.session_id = session_id
        self.collection_name = get_session_collection_name(session_id)
        
        self.main_vectorstore = AsyncQdrantVectorStore(cache_dir=cache_dir)
        self.client = self.main_vectorstore.client
        self.dense_model = self.main_vectorstore.dense_model
        self.sparse_model = self.main_vectorstore.sparse_model
        self.embedding_size = self.main_vectorstore.embedding_size
        
        self.splitter = TextSplitter()
        self.logger = setup_logging()

    async def create_collection(self) -> None:
        """Create the session-specific Qdrant collection.

        Creates a collection with the same configuration as the main
        legal documents collection but isolated per session.

        """
        try:
            try:
                await self.client.get_collection(collection_name=self.collection_name)
                self.logger.info(
                    f"Session collection '{self.collection_name}' already exists."
                )
                return
            except Exception:
            
                pass

            self.logger.info(f"Creating session collection: {self.collection_name}")
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    "Dense": models.VectorParams(
                        size=self.embedding_size, distance=Distance.COSINE
                    )
                },
                sparse_vectors_config={
                    "Sparse": models.SparseVectorParams(modifier=models.Modifier.IDF)
                },
                quantization_config=models.ScalarQuantization(
                    scalar=models.ScalarQuantizationConfig(
                        type=models.ScalarType.INT8,
                        quantile=0.99,
                        always_ram=False,
                    )
                ),
                hnsw_config=models.HnswConfigDiff(m=0),
                optimizers_config=models.OptimizersConfigDiff(indexing_threshold=0),
            )

            self.logger.info(f"Session collection '{self.collection_name}' created successfully")

        except Exception as e:
            self.logger.error(f"Failed to create session collection: {e}")
            raise

    async def ingest_document(self, text: str, filename: str) -> int:
        """Ingest a document into the session collection.

        Chunks the text, creates embeddings, and stores in the session collection.

        Args:
            text: Document text to ingest.
            filename: Original filename.

        Returns:
            int: Number of chunks created.

        """
        chunks = self.splitter.split_text(text)
        self.logger.info(f"Chunked document into {len(chunks)} chunks for session {self.session_id[:8]}")

        if not chunks:
            return 0

        all_payloads = []
        all_ids = []
        all_chunks_text = []

        for i, chunk in enumerate(chunks):
            payload = ArticleChunkPayload(
                section_title=f"Section {i + 1}",
                document_title=f"Uploaded Agreement: {filename}",
                jurisdiction="User Upload",
                document_type=["user_upload"],
                document_id=f"{self.session_id}__chunk_{i}",
                chunk_text=chunk,
            )
            all_payloads.append(payload)
            all_chunks_text.append(chunk)
            chunk_id = int(hashlib.md5(payload.url.encode()).hexdigest()[:8], 16)
            all_ids.append(chunk_id)

        batch_size = 10
        total_upserted = 0

        for start in range(0, len(all_chunks_text), batch_size):
            end = start + batch_size
            sub_chunks = all_chunks_text[start:end]
            sub_ids = all_ids[start:end]
            sub_payloads = all_payloads[start:end]

            dense_vecs, sparse_vecs = await self.main_vectorstore.embed_batch_async(sub_chunks)
            await self.client.upsert(
                collection_name=self.collection_name,
                points=Batch(
                    ids=sub_ids,
                    payloads=[p.dict() for p in sub_payloads],
                    vectors={"Dense": dense_vecs, "Sparse": sparse_vecs},
                ),
            )

            total_upserted += len(sub_chunks)
            self.logger.debug(
                f"Upserted batch {start//batch_size + 1} to session collection "
                f"({total_upserted}/{len(all_chunks_text)} chunks)"
            )

        self.logger.info(
            f"Successfully ingested {total_upserted} chunks into session collection "
            f"{self.collection_name}"
        )

        return total_upserted

    async def delete_collection(self) -> None:
        """Delete the session collection and all its data.

        This completely removes all embeddings and data associated
        with this session for privacy compliance.

        """
        try:
            await self.client.delete_collection(collection_name=self.collection_name)
            self.logger.info(f"Deleted session collection: {self.collection_name}")
        except Exception as e:
            self.logger.error(f"Failed to delete session collection {self.collection_name}: {e}")
            raise

    async def query(
        self, query_text: str, limit: int = 5
    ) -> list[dict]:
        """Query the session collection for relevant chunks.

        Args:
            query_text: Search query text.
            limit: Maximum number of results.

        Returns:
            list[dict]: List of search results with metadata.

        """
        dense_vector = self.main_vectorstore.dense_vectors([query_text])[0]
        sparse_vector = self.main_vectorstore.sparse_vectors([query_text])[0]

        response = await self.client.query_points(
            collection_name=self.collection_name,
            query=FusionQuery(fusion=Fusion.RRF),
            prefetch=[
                Prefetch(query=dense_vector, using="Dense", limit=limit * 10),
                Prefetch(query=sparse_vector, using="Sparse", limit=limit * 10),
            ],
            limit=limit,
        )
        results = []
        for point in response.points:
            payload = point.payload or {}
            results.append(
                {
                    "section_title": payload.get("section_title", payload.get("title", "")),
                    "document_title": payload.get("document_title", payload.get("feed_name")),
                    "jurisdiction": payload.get("jurisdiction", payload.get("feed_author")),
                    "document_type": payload.get("document_type", payload.get("article_authors", [])),
                    "document_id": payload.get("document_id", payload.get("url")),
                    "chunk_text": payload.get("chunk_text"),
                    "score": point.score or 0.0,
                }
            )

        return results

