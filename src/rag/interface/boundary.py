"""Pydantic payloads at external edges, not internal pipeline objects.

Future adapters will validate/serialize these and convert to/from dataclasses.
These are application-owned envelopes, not copies of provider SDK schemas.
"""

from typing import Literal

from pydantic import BaseModel, Field, FiniteFloat, JsonValue


class UserQuery(BaseModel):
    """Input boundary: user/API → validation → internal Query."""

    text: str = Field(min_length=1)
    collection_name: str
    session_id: str | None = None


class DocumentInput(BaseModel):
    """Input boundary: file reference → validation → internal Document; no file is opened

    here.
    """

    document_id: str
    source: str = Field(min_length=1)
    format: Literal["pdf", "text"]


class EmbeddingRequest(BaseModel):
    """Output boundary: embedding adapter → external embedding provider."""

    texts: list[str]
    model: str
    task: Literal["retrieval.query", "retrieval.passage"]


class EmbeddingInput(BaseModel):
    """Input boundary: external embedding provider → validation → internal Embedding,

    correlated by batch index.
    """

    index: int = Field(ge=0)
    vector: list[FiniteFloat] = Field(min_length=1)
    model: str


class Citation(BaseModel):
    """Output boundary: internal SourceCitation → citation nested in the user Response."""

    chunk_id: str
    source: str
    page_no: int | None = Field(default=None, ge=1)
    quote: str | None = None


class Response(BaseModel):
    """Output boundary: internal Answer → serialized user/API response."""

    text: str
    citations: list[Citation] = Field(default_factory=list)
    session_id: str | None = None


class ChunkPayload(BaseModel):
    """Shared external chunk fields for vector writes and reads; one definition for

    identity, text, and metadata.
    """

    chunk_id: str
    document_id: str
    text: str
    metadata: dict[str, JsonValue] = Field(default_factory=dict)


class ChunkWithEmbedding(ChunkPayload):
    """Output boundary: internal EmbeddedChunk → outgoing vector record; DB-specific ID

    encoding belongs to the adapter.
    """

    vector: list[FiniteFloat] = Field(min_length=1)


class VectorUpsertRequest(BaseModel):
    """Output boundary: internal UpsertBatch → vector DB write."""

    collection_name: str
    chunks: list[ChunkWithEmbedding]


class VectorSearchRequest(BaseModel):
    """Output boundary: internal SearchQuery → vector DB query."""

    collection_name: str
    vector: list[FiniteFloat] = Field(min_length=1)
    top_k: int = Field(default=5, gt=0)
    score_threshold: float | None = None


class VectorSearchHit(ChunkPayload):
    """Input boundary: vector DB result → validation → internal SearchHit and canonical

    Chunk.
    """

    score: FiniteFloat


class AIRequest(BaseModel):
    """Output boundary: AI adapter → generation provider; includes provider model

    configuration.
    """

    user_prompt: str
    model: str
    max_tokens: int = Field(gt=0)
    output_schema: dict[str, JsonValue] | None = None


class AIResponse(BaseModel):
    """Input boundary: generation provider → validation → internal GenerationResult;

    structured parsing follows.
    """

    content: str | None
