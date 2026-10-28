"""Application-facing abstractions. No SDK imports, I/O, or implementations.

Methods use internal dataclasses. Future adapters own external Pydantic
payloads and conversion. Provider configuration belongs to concrete clients.
"""

from abc import ABC, abstractmethod

from .data import (
    Chunk,
    CollectionRef,
    CollectionSpec,
    Document,
    Embedding,
    EmbeddingBatch,
    GenerationRequest,
    GenerationResult,
    Page,
    ScrollPage,
    ScrollRequest,
    SearchHit,
    SearchQuery,
    UpsertBatch,
)


class VectorDB(ABC):
    """Application port: ingestion writes and retrieval reads → external DB adapter.

    Methods use internal dataclasses.
    """

    @abstractmethod
    def collection_exists(self, collection: CollectionRef) -> bool:
        ...

    @abstractmethod
    def create_collection(self, collection: CollectionSpec) -> None:
        ...

    @abstractmethod
    def delete_collection(self, collection: CollectionRef) -> None:
        ...

    @abstractmethod
    def upsert(self, batch: UpsertBatch) -> None:
        ...

    @abstractmethod
    def search(self, query: SearchQuery) -> list[SearchHit]:
        ...

    @abstractmethod
    def scroll(self, request: ScrollRequest) -> ScrollPage:
        """Read a corpus page; next_cursor=None marks the end."""
        ...


class AIClient(ABC):
    """Application port: query planning/answer generation → AI adapter. Jev decisions use a

    separate contract.
    """

    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate a result for the supplied internal request."""
        ...


class PDFLoader(ABC):
    """Ingestion port: Document → extracted Pages; no chunking or embedding responsibility."""

    @abstractmethod
    def load(self, document: Document) -> list[Page]:
        """Load a PDF into pages; page numbers are one-based."""
        ...


class TextChunker(ABC):
    """Ingestion port: Pages → canonical Chunks with source metadata intact."""

    @abstractmethod
    def split(self, pages: list[Page]) -> list[Chunk]:
        ...


class EmbeddingClient(ABC):
    """Shared port: ingestion passages or retrieval queries → indexed Embeddings."""

    @abstractmethod
    def embed(self, batch: EmbeddingBatch) -> list[Embedding]:
        """Return one indexed embedding per input text."""
        ...

# class
