import hashlib
import os
import re
import uuid

from qdrant_client import models

from core.loader import load_textfile
from core.pdf_loader import PDFParser
from core.register_collection import collections_index
from core.text_chunker import split_into_chunks
from embedding.batch_embed import _batch_embed
from qdrantDB.chunker import token_chunk
from qdrantDB.client import client
from settings import settings

# sudo docker run -p 6333:6333 -p 6334:6334 \
# -v $(pwd)/qdrant_storage:/qdrant/storage \
# qdrant/qdrant


NAMESPACE = uuid.UUID(
    "12345678-1234-5678-1234-567812345678"
)  # any fixed constant, made up once, never changed


def generate_id(text: str) -> str:
    return str(uuid.uuid5(NAMESPACE, text))


# /home/faseeh/projects/RAG-from-scratch/.venv/bin/python /home/faseeh/projects/RAG-from-scratch/qdrantDB/ingest.py
class Ingest:
    def __init__(
        self,
        # text=None,
        mode="pdf",
        collection_name=settings.collection_name,
        filename=settings.filename,
        batch_size=settings.batch_size,
    ):

        # self.text = text

        self.filename = filename
        self.mode = mode
        self.file_hash = self._compute_hash(self.filename)

        catalog = collections_index.catalog

        for entry in catalog:
            if entry["file_hash"] == self.file_hash:
                print("⚠️ Document already ingested!")
                print(
                    f"   Matches: '{entry['source_file']}' in collection '{entry['collection_name']}'"
                )
                self.collection_name = entry["collection_name"]
                self.is_duplicate = True
                return

        self.batch_size = batch_size

        if mode == "pdf":
            parser = PDFParser(self.filename)
            self.parsed = parser.parse()
            self.book_title = (
                parser.book_title
                or os.path.splitext(os.path.basename(self.filename))[0]
            )

        if collection_name:
            self.collection_name = self._sanitize(collection_name)

        else:
            self.collection_name = self._sanitize(self.book_title)

        settings.collection_name = self.collection_name
        print(f"COLLECTION NAME: {self.collection_name}")

        collections_index.register_collection(
            collection_name=self.collection_name,
            display_name=self.book_title,
            source_file=self.filename,
            file_hash=self.file_hash,
            chunk_count=len(self.parsed),
        )

        if mode == "pdf":
            self.ingest_pdf()

    def ingest_text(self):

        if self.text is None:
            text: str = load_textfile(self.filename)
        chunks: list[str] = split_into_chunks(text)
        all_embeddings: list[list[float]] = _batch_embed(chunks=chunks)
        # chunks_with_vectors: list[dict] = []
        self._print_logs(chunks, all_embeddings)

        self._collection_check()
        # for i in range(0, len(chunks), self.batch_size):
        #     batch: list[str] = chunks[i : i + self.batch_size]
        #     batch_embeddings = embed(batch, "retrieval.passage")
        #     all_embeddings.extend(batch_embeddings)

        for i, (chunk, embedding) in enumerate(zip(chunks, all_embeddings)):
            metadata = {"title": "atomic habits", "author": "james_clear"}
            chunk_index = i
            metadata["chunk_index"] = chunk_index
            metadata["text"] = chunk
            client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=generate_id(chunk),
                        vector=embedding,
                        payload=metadata,
                    )
                ],
            )

    def ingest_pdf(self):
        if self.is_duplicate:
            print("Skipping ingestion: File is already in the database.")
            return

        chunked = token_chunk(self.parsed)
        chunks = []
        for chunk in chunked:
            chunks.append(chunk["page_text"])
        all_embeddings = _batch_embed(chunks=chunks)
        # vectorized  = []
        self._print_logs(chunked, all_embeddings)

        self._collection_check()

        I = 0
        for metadata, (chunk, embedding) in zip(chunked, zip(chunks, all_embeddings)):
            client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=generate_id(chunk),
                        vector=embedding,
                        payload=metadata,
                    )
                ],
            )
            # I += 1
        print(len(chunked))

        # for batch

    # def _batch_embed(self, chunks):
    #     all_embeddings = []
    #     for i in range(0, len(chunks), self.batch_size):
    #         batch: list[str] = chunks[i : i + self.batch_size]
    #         # batch_embeddings = embed(batch, "retrieval.passage")
    #         batch_embeddings = embed(batch, mode="local")
    #         all_embeddings.extend(batch_embeddings)
    #     return all_embeddings

    def _collection_check(self):
        if not client.collection_exists(collection_name=self.collection_name):
            print(f"Collection '{self.collection_name}' doesn't exist.")
            client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=384,
                    distance=models.Distance.COSINE,  # 384 , 512
                ),
            )
        # else:
        #     print(f"COLLECTION: {self.collection_name}\nAlready exists")

    def _compute_hash(self, filepath: str):
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
            return sha256.hexdigest()

    def _sanitize(self, name: str):
        name = name.lower().strip()

        name = re.sub(r"[^a-z0-9_-]+", "_", name)
        return name.strip("_")

    def _print_logs(self, chunked, all_embeddings):
        print(f"""
        COLLECTION NAME:    {self.collection_name}
        MODE:               {self.mode}
        BATCH SIZE:         {self.batch_size}
        Chunked:            {type(chunked), len(chunked)}
        Embeddings:         {type(all_embeddings), len(all_embeddings)}

        """)


# def ingest(
#     text=None,
#     parsed=None,
#     collection_name="atomic_habits",
#     filename="basic_ai.txt",
#     batch_size=128,
#     # overwrite=True,
# ):
#     if text is None:
#         text: str = load_textfile(filename)
#     chunks: list[str] = split_into_chunks(text)
#     all_embeddings: list[list[float]] = []
#     # chunks_with_vectors: list[dict] = []

#     if not client.collection_exists(collection_name=collection_name):
#         print(f"Collection '{collection_name}' doesn't exist.")
#         client.create_collection(
#             collection_name=collection_name,
#             vectors_config=models.VectorParams(
#                 size=512, distance=models.Distance.COSINE
#             ),
#         )

#     for i in range(0, len(chunks), batch_size):
#         batch: list[str] = chunks[i : i + batch_size]
#         batch_embeddings = embed(batch, "retrieval.passage")
#         all_embeddings.extend(batch_embeddings)

#     for i, (chunk, embedding) in enumerate(zip(chunks, all_embeddings)):
#         metadata = {"title": "atomic habits", "author": "james_clear"}
#         chunk_index = i
#         metadata["chunk_index"] = chunk_index
#         metadata["text"] = chunk
#         client.upsert(
#             collection_name=collection_name,
#             points=[
#                 models.PointStruct(
#                     id=generate_id(chunk),
#                     vector=embedding,
#                     payload=metadata,
#                 )
#             ],
#         )

if __name__ == "__main__":
    filename = "data/Asimov_the_foundation.pdf"
    i = Ingest(mode="pdf", filename=filename)
    i.ingest_pdf()
