import os
import uvicorn
import re
import dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client.http.exceptions import UnexpectedResponse
from contextlib import asynccontextmanager
from src.api.exceptions.exception_handlers import (
    general_exception_handler,
    qdrant_exception_handler,
    validation_exception_handler,
)
from src.api.middleware.logging_middleware import LoggingMiddleware
from src.api.routes.agreement_routes import router as agreement_router
from src.api.routes.health_routes import router as health_router
from src.api.routes.search_routes import router as search_router
from src.api.routes.voice_routes import router as voice_router
from src.api.routes.tts_routes import router as tts_router
from src.api.routes.report_routes import router as report_router
from src.api.services.document_storage_service import start_cleanup_task
from src.infrastructure.qdrant.qdrant_vectorstore import AsyncQdrantVectorStore
from src.utils.logger_util import setup_logging

dotenv.load_dotenv()

logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to handle startup and shutdown events.
    Initializes the Qdrant vector store on startup and ensures proper cleanup on shutdown.

    Args:
        app (FastAPI): The FastAPI application instance.
    Yields:
        None

    Exceptions:
        Raises exceptions if initialization or cleanup fails.
    """
    cache_dir = "/tmp/fastembed_cache"
    os.makedirs(cache_dir, exist_ok=True)  
    
    logger.info(f"HF_HOME: {os.environ.get('HF_HOME', 'Not set')}")
    logger.info(f"Cache dir: {cache_dir}, Writable: {os.access(cache_dir, os.W_OK)}")
    cache_contents = os.listdir(cache_dir) if os.path.exists(cache_dir) else "Empty"
    logger.info(f"Cache contents before: {cache_contents}")
    try:
        app.state.vectorstore = AsyncQdrantVectorStore(cache_dir=cache_dir)
        start_cleanup_task()
        logger.info("Started background cleanup task for uploaded documents")
        
    except Exception as e:
        logger.exception("Failed to initialize QdrantVectorStore")
        raise e
    yield
    try:
        await app.state.vectorstore.client.close()
    except Exception:
        logger.exception("Failed to close Qdrant client")

app = FastAPI(
    title="Lauya-mi Legal Assistant API",
    version="2.0",
    description="""
    AI-powered legal assistant for analyzing tenancy agreements and answering legal questions.
    
    ## Features
    
    * **Document Analysis**: Upload tenancy agreements (PDF/images) and get AI-powered risk analysis
    * **Multi-language Support**: Query in Yoruba, Hausa, Igbo, or Nigerian Accented English
    * **Voice Queries**: Ask questions using voice with automatic speech recognition (ASR)
    * **RAG-powered Search**: Hybrid dense + sparse vector search over Lagos State Tenancy Law 2011
    * **Streaming Responses**: Real-time streaming for faster user experience
    
    ## Technology Stack
    
    * **LLM**: N-ATLaS (Nigerian-accented LLM)
    * **Vector Database**: Qdrant (hybrid search with BM25 + embeddings)
    * **Database**: Supabase PostgreSQL
    * **ASR**: N-ATLaS speech recognition models
    
    ## API Endpoints
    
    * `/search/unique-titles` - Search for unique document sections
    * `/search/ask/stream` - Ask questions and get streaming answers
    * `/agreement/upload-agreement/stream` - Upload and analyze agreements
    * `/voice/ask-with-voice` - Voice-based question answering
    * `/tts/synthesize` - Text-to-speech synthesis
    * `/report/generate` - Generate PDF analysis reports
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
common_dev_ports = ["http://localhost:8080", "http://localhost:3000", "http://localhost:5173"]

for port in common_dev_ports:
    if port not in allowed_origins:
        allowed_origins.append(port)

vercel_pattern = re.compile(r"^https://lauyami-[a-z0-9]+-hamzat-tiamiyus-projects\.vercel\.app$")


def is_origin_allowed(origin: str) -> bool:
    """Check if an origin is allowed, including Vercel deployment URLs."""
    if origin in allowed_origins:
        return True
    if vercel_pattern.match(origin):
        logger.debug(f"Allowing Vercel deployment URL: {origin}")
        return True
    return False

logger.info(f"CORS allowed origins: {allowed_origins} (plus Vercel deployment URLs matching pattern)")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://lauyami-[a-z0-9]+-hamzat-tiamiyus-projects\.vercel\.app", 
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  
    allow_headers=["Authorization", "Content-Type"],
)

app.add_middleware(LoggingMiddleware)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(UnexpectedResponse, qdrant_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(search_router, prefix="/search", tags=["search"])
app.include_router(agreement_router, prefix="/agreement", tags=["agreement"])
app.include_router(voice_router, prefix="/voice", tags=["voice"])
app.include_router(tts_router, prefix="/tts", tags=["text-to-speech"])
app.include_router(report_router, prefix="/report", tags=["reports"])
app.include_router(health_router, tags=["health"])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=True,  #
    )

