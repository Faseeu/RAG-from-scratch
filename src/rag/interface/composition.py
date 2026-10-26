"""Dependency container only: ingestion uses collaborators, not inheritance."""

from dataclasses import dataclass

from .contracts import EmbeddingClient, PDFLoader, TextChunker, VectorDB


@dataclass
class IngestDependencies:
    """Composition only: loader → chunker → embedder → vector_db. No ingestion execution in

    this container.
    """

    loader: PDFLoader
    chunker: TextChunker
    embedder: EmbeddingClient
    vector_db: VectorDB
