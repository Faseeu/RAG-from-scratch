import json
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

TUNABLE = {
    "embedding_model",
    "embedding_dim",
    "embedding_mode",
    "chunk_size",
    "chunk_overlap",
    "retrieval_top_k",
    "retrieval_threshold",
    "rrf_merge_top_k",
    "rerank_top_k",
    "rerank_threshold",
    "rerank_model",
    "batch_size",
    "default_llm_model",
    "router_llm_model",
    "guard_llm_model",
    "max_tokens",
    "stream_response"
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # API Keys
    groq_api_key: str = ""
    hf_token: str = ""
    jina_api_key: str = ""

    # Database
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # Models & Defaults
    default_llm_model: str = "openai/gpt-oss-120b"
    router_llm_model: str = "openai/gpt-oss-20b"
    guard_llm_model: str = "openai/gpt-oss-20b"
    max_tokens: int = 5000
    stream_response:bool = False

    # Embeddings
    embedding_model: str = "Snowflake/snowflake-arctic-embed-s"
    embedding_dim: int = 384
    embedding_mode: str = "local"

    # RAG Parameters
    chunk_size: int = 450
    chunk_overlap: int = 70
    retrieval_top_k: int = 15
    retrieval_threshold: float = 0.5
    rrf_merge_top_k: int = 10
    # Rerank parameters
    rerank_top_k: int = 5
    rerank_threshold: float = 0.5
    rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # Ingest
    batch_size: int = 128
    filename: str = ""
    mode: str = "pdf"
    collection_name: str = ""

    # BM25 Parameters
    RAG_text_filename: str = "data/RAG.json"

    # Preprocessor Parameters
    embed_cache_store: str = "data/faq_enteries.json"
    hashmap_store: str = "data/basic_greets.json"



    def save(self, path=Path("data/settings.json")):
        data = self.model_dump(include=TUNABLE)
        path.write_text(json.dumps(data, indent=2))


settings = Settings()
p = Path("data/settings.json")
if p.exists():
    settings = settings.model_copy(update=json.loads(p.read_text()))
