"""Plain dataclasses for data passed between application functions."""

from dataclasses import dataclass, field
from typing import Literal

@dataclass
class MemTurn:
    question: str = ""
    answer: str = ""
    mem: dict = field(default_factory=dict)


@dataclass
class Query:
    """Internal: validated user input → contextualization/planning → retrieval."""

    text: str
    collection_name: str
    session_id: str | None = None


@dataclass
class Document:
    """Internal: validated document reference → loader; does not read the file."""

    document_id: str
    source: str
    format: Literal["pdf", "text"]


@dataclass
class Page:
    """Internal: PDF loader → chunker; preserve source and one-based page number."""

    document_id: str
    page_text: str
    page_no: int
    source: str
    book_title: str | None = None
    confidence: float | None = None


@dataclass
class Chunk:
    """Canonical internal chunk: chunker → indexing; retrieval → fusion → reranking →

    context. Preserve identity and provenance instead of making per-stage copies.
    """

    chunk_id: str
    document_id: str
    text: str
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class EmbeddingBatch:
    """Internal: query/chunk text → embedding client; task distinguishes query from passage."""

    texts: list[str]
    task: Literal["retrieval.query", "retrieval.passage"]


@dataclass
class Embedding:
    """Internal: embedding adapter → query search or chunk/vector pairing; index identifies

    the batch item.
    """

    index: int
    vector: list[float]
    model: str


@dataclass
class EmbeddedChunk:
    """Internal: ingestion pairs a canonical Chunk with its Embedding → vector DB adapter."""

    chunk: Chunk
    embedding: Embedding


@dataclass
class SearchQuery:
    """Internal: query embedding → vector retrieval; scores remain backend-specific."""

    collection_name: str
    vector: list[float]
    top_k: int = 5
    score_threshold: float | None = None


@dataclass
class SearchHit:
    """Internal: retrieval/reranking → candidate selection. Reuse Chunk; a score is

    meaningful only with its producing stage/configuration.
    """

    chunk: Chunk
    score: float


@dataclass
class CollectionSpec:
    """Internal: ingestion configuration → vector collection creation; model and dimensions

    must agree.
    """

    name: str
    embedding_model: str
    embedding_dim: int
    distance: Literal["cosine", "dot", "euclidean"] = "cosine"


@dataclass
class CollectionRef:
    """Internal: ingestion collection lookup/deletion → vector DB adapter."""

    name: str


@dataclass
class UpsertBatch:
    """Internal: ingestion → vector DB adapter; serialization happens at the external

    boundary.
    """

    collection_name: str
    chunks: list[EmbeddedChunk]


@dataclass
class ScrollRequest:
    """Internal: lexical corpus loading → paginated vector DB reads."""

    collection_name: str
    limit: int = 1000
    cursor: str | int | None = None


@dataclass
class ScrollPage:
    """Internal: DB adapter → lexical corpus/index construction; None cursor ends

    pagination.
    """

    chunks: list[Chunk]
    next_cursor: str | int | None = None


@dataclass
class GenerationRequest:
    """Internal: query planning or evidence prompt → AI client; not an external provider

    payload.
    """

    user_prompt: str


@dataclass
class GenerationResult:
    """Internal: AI adapter → structured parsing/verification; raw content is not yet a

    verified Answer.
    """

    content: str | None


@dataclass
class SourceCitation:
    """Canonical internal citation: evidence assembly/verification → Answer; retain durable

    chunk identity.
    """

    chunk_id: str
    source: str
    page_no: int | None = None
    quote: str | None = None


@dataclass
class Answer:
    """Internal: generation parsing → verification → outgoing Response; dataclass

    construction does not prove grounding.
    """

    text: str
    citations: list[SourceCitation] = field(default_factory=list)
    session_id: str | None = None
