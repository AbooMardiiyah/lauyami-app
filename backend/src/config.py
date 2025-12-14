import os
from typing import ClassVar

import yaml
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.models.document_models import DocumentConfig


# -----------------------------
# Supabase database settings
# -----------------------------
class SupabaseDBSettings(BaseModel):
    table_name: str = Field(default="legal_documents", description="Supabase table name")
    host: str = Field(default="localhost", description="Database host")
    name: str = Field(default="postgres", description="Database name")
    user: str = Field(default="postgres", description="Database user")
    password: SecretStr = Field(default=SecretStr("password"), description="Database password")
    port: int = Field(default=6543, description="Database port")
    test_database: str = Field(default="lauyami_test", description="Test database name")


# -----------------------------
# Document ingestion settings
# -----------------------------
class DocumentSettings(BaseModel):
    batch_size: int = Field(
        default=5, description="Number of documents to ingest in a batch"
    )
    documents_config_path: str = Field(
        default="src/configs/legal_documents.yaml",
        description="Path to YAML file containing legal document configurations"
    )


# -----------------------------
# Qdrant settings
# -----------------------------
# BAAI/bge-large-en-v1.5 (1024), BAAI/bge-base-en-v1.5 (HF, 768). BAAI/bge-base-en (Fastembed, 768)
class QdrantSettings(BaseModel):
    url: str = Field(default="", description="Qdrant API URL")
    api_key: str = Field(default="", description="Qdrant API key")
    collection_name: str = Field(
        default="legal_documents_collection", description="Qdrant collection name"
    )
    dense_model_name: str = Field(default="BAAI/bge-base-en", description="Dense model name")
    sparse_model_name: str = Field(
        default="Qdrant/bm25", description="Sparse model name"
    )  # prithivida/Splade_PP_en_v1 (larger)
    vector_dim: int = Field(
        default=768,
        description="Vector dimension",  # 768, 1024 with Jina or large HF
    )
    document_batch_size: int = Field(
        default=5, description="Number of documents to parse and ingest in a batch"
    )
    sparse_batch_size: int = Field(default=32, description="Sparse batch size")
    embed_batch_size: int = Field(default=50, description="Dense embedding batch")
    upsert_batch_size: int = Field(default=50, description="Batch size for Qdrant upsert")
    max_concurrent: int = Field(default=2, description="Maximum number of concurrent tasks")


# -----------------------------
# Text splitting
# -----------------------------
class TextSplitterSettings(BaseModel):
    chunk_size: int = Field(default=4000, description="Size of text chunks in characters")
    chunk_overlap: int = Field(
        default=400, description="Number of overlapping characters between chunks (10% of chunk_size for legal docs)"
    )
    separators: list[str] = Field(
        default_factory=lambda: [
            " 1. ", " 2. ", " 3. ", " 4. ", " 5. ", " 6. ", " 7. ", " 8. ", " 9. ",
            " 10. ", " 11. ", " 12. ", " 13. ", " 14. ", " 15. ", " 16. ", " 17. ", " 18. ", " 19. ",
            " 20. ", " 21. ", " 22. ", " 23. ", " 24. ", " 25. ", " 26. ", " 27. ", " 28. ", " 29. ",
            "\n1. ", "\n2. ", "\n3. ", "\n4. ", "\n5. ", "\n6. ", "\n7. ", "\n8. ", "\n9. ",
            "\n10. ", "\n11. ", "\n12. ", "\n13. ", "\n14. ", "\n15. ", "\n16. ", "\n17. ", "\n18. ", "\n19. ",
            "\n20. ", "\n21. ", "\n22. ", "\n23. ", "\n24. ", "\n25. ", "\n26. ", "\n27. ", "\n28. ", "\n29. ",
            ".\n",  
            ". ",
            "! ",
            "? ",
            "\n",  
            " ",
            "",
        ],
        description="List of separators for text splitting in order of preference. Optimized for Lagos State Tenancy Law structure (numbered paragraphs like '1. Item 2. Item').",
    )


# -----------------------------
# Jina Settings
# -----------------------------
class JinaSettings(BaseModel):
    api_key: str = Field(default="", description="Jina API key")
    url: str = Field(default="https://api.jina.ai/v1/embeddings", description="Jina API URL")
    model: str = Field(default="jina-embeddings-v3", description="Jina model name")  # 1024


# -----------------------------
# Hugging Face Settings
# -----------------------------
# Used for:
# 1. Modal services (N-ATLaS LLM & ASR) - downloading models from HF Hub
# 2. FastEmbed - downloading embedding models (BAAI/bge-base-en) from HF Hub
class HuggingFaceSettings(BaseModel):
    api_key: str = Field(default="", description="Hugging Face API key (HF_TOKEN)")
    model: str = Field(default="BAAI/bge-base-en", description="Hugging Face model name")


# -----------------------------
# Opik Observability Settings
# -----------------------------
class OpikObservabilitySettings(BaseModel):
    api_key: str = Field(default="", description="Opik Observability API key")
    project_name: str = Field(default="lauyami-legal-assistant", description="Opik project name")


# -----------------------------
# Modal Services Settings
# -----------------------------
class ModalSettings(BaseModel):
    """Settings for Modal-hosted N-ATLaS services."""
    # N-ATLaS LLM service (The Brain)
    llm_base_url: str = Field(
        default="",
        description="Modal endpoint URL for N-ATLaS LLM WITHOUT /v1 (e.g., https://your-workspace--natlas-vllm-serve.modal.run). The /v1 will be added automatically."
    )
    llm_api_key: str = Field(
        default="not-needed",
        description="API key for N-ATLaS LLM (usually 'not-needed' for Modal)"
    )
    llm_model_name: str = Field(
        default="n-atlas",
        description="Model name for N-ATLaS LLM"
    )
    
    # N-ATLaS ASR service (The Ears)
    asr_base_url: str = Field(
        default="",
        description="Modal endpoint URL for N-ATLaS ASR (e.g., https://your-workspace--natlas-asr-multilingual-api-transcribe.modal.run)"
    )
    
    # Supported language codes
    supported_languages: dict[str, str] = Field(
        default_factory=lambda: {
            "yo": "Yoruba",
            "ha": "Hausa",
            "ig": "Igbo",
            "en": "Nigerian Accented English",
        },
        description="Mapping of language codes to language names"
    )


# -----------------------------
# YarnGPT TTS Settings
# -----------------------------
class YarnGPTSettings(BaseModel):
    """Settings for YarnGPT Text-to-Speech API."""
    api_key: str = Field(
        default="",
        description="YarnGPT API key"
    )
    api_url: str = Field(
        default="https://yarngpt.ai/api/v1/tts",
        description="YarnGPT TTS API endpoint"
    )


# -----------------------------
# Main Settings
# -----------------------------
class Settings(BaseSettings):
    supabase_db: SupabaseDBSettings = Field(default_factory=SupabaseDBSettings)
    qdrant: QdrantSettings = Field(default_factory=QdrantSettings)
    document: DocumentSettings = Field(default_factory=DocumentSettings)
    text_splitter: TextSplitterSettings = Field(default_factory=TextSplitterSettings)

    jina: JinaSettings = Field(default_factory=JinaSettings)
    hugging_face: HuggingFaceSettings = Field(default_factory=HuggingFaceSettings)
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    opik: OpikObservabilitySettings = Field(default_factory=OpikObservabilitySettings)
    modal: ModalSettings = Field(default_factory=ModalSettings)
    yarngpt: YarnGPTSettings = Field(default_factory=YarnGPTSettings)

    # Pydantic v2 model config
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=[".env"],
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
        case_sensitive=False,
        frozen=True,
    )
    
    # Expose YarnGPT settings as top-level properties for easier access
    @property
    def yarngpt_api_key(self) -> str:
        return self.yarngpt.api_key
    
    @property
    def yarngpt_api_url(self) -> str:
        return self.yarngpt.api_url

    @property
    def legal_documents(self) -> list[DocumentConfig]:
        """Load legal documents from YAML configuration file.
        
        Returns:
            list[DocumentConfig]: List of document configurations.
        """
        return load_legal_documents(self.document.documents_config_path)


def load_legal_documents(path: str) -> list[DocumentConfig]:
    """Load legal document configurations from a YAML file.
    
    If the file does not exist or is empty, returns an empty list.

        Args:
        path (str): Path to the YAML file.

        Returns:
        list[DocumentConfig]: List of DocumentConfig instances loaded from the file.
        """
    if not os.path.exists(path):
        return []
    
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        if not data or "documents" not in data:
            return []
        
        document_list = data.get("documents", [])
        return [DocumentConfig(**doc) for doc in document_list]
    except Exception as e:
        # Log error but don't fail startup
        import logging
        logging.warning(f"Failed to load legal documents from {path}: {e}")
        return []


# -----------------------------
# Instantiate settings
# -----------------------------
settings = Settings()
