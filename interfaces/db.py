from abc import ABC, abstractmethod
from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class ChunkPayload:
    text: str
    page_no: int
    title: str
    source: str
    token_count: int
    confidence: float
    chunk_index: int


class Chunk(BaseModel):
    chunk_id: str
    chunk_text: str
    metadata: dict


class Ingest(ABC):
    mode: str
    collection_name: str | None = None
    filename: str | None = None
    batch_size: int | None = None

    @abstractmethod
    def ingest(self, chunks):
        pass

class Chunker(BaseModel):
    pass


class VectorDB(ABC):
    name: str
    ingest: Ingest()
    chunker: Chunker()
    host: str | None = None
    port: str | None = None



    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def ingest(self, chunk):
        pass

    @abstractmethod
    def retrieve(self, query):
        pass


class Load_doc(ABC):
    filepath:str


class Step(ABC):
    pass


