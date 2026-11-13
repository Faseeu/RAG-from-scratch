"""Legacy pipeline contracts retained for compatibility with the original scaffold.

These contracts are not aliases to contracts.VectorDB or internal_models.Chunk:
their method signatures and payload fields differ. Keep their shapes stable until
callers deliberately migrate; do not silently change them.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class ChunkPayload:
    """Legacy internal: parsed/chunked text → ingestion, with explicit page fields."""

    text: str
    page_no: int
    title: str
    source: str
    token_count: int
    confidence: float
    chunk_index: int


class Chunk(BaseModel):
    """Legacy boundary: external chunk payload, preserving main's chunk_text key."""

    chunk_id: str
    chunk_text: str
    metadata: dict


class Ingest(ABC):
    """Legacy ingestion collaborator; composed into a DB rather than executed here."""

    mode: str
    collection_name: str | None = None
    filename: str | None = None
    batch_size: int | None = None

    @abstractmethod
    def ingest(self, chunks):
        ...


class Chunker(BaseModel):
    """Legacy empty configuration envelope; main did not define execution methods."""


class VectorDB(ABC):
    """Legacy DB port: connect/ingest/retrieve; preserves main's subclass contract."""

    name: str
    # Type annotations must not instantiate abstract collaborators at import time.
    ingest: Ingest
    chunker: Chunker
    host: str | None = None
    port: str | None = None

    @abstractmethod
    def connect(self):
        ...

    @abstractmethod
    def ingest(self, chunk):
        ...

    @abstractmethod
    def retrieve(self, query):
        ...


class Load_doc(ABC):
    """Legacy loading scaffold: document location → future extraction step."""

    filepath: str


class Step(ABC):
    """Legacy pipeline-step marker; main did not define behavior."""
