import uuid

from chunker import token_chunk
from qdrant_client import QdrantClient, models

from core.embedding import embed
from core.loader import load_textfile
from core.pdf_loader import PDFParser
from core.text_chunker import split_into_chunks

client = QdrantClient(host="localhost", port=6333)
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
        text=None,
        mode="text",
        collection_name="atomic_habits",
        filename="basic_ai.txt",
        batch_size=128,
    ):

        self.text = text
        self.collection_name = collection_name
        self.filename = filename
        if mode == "pdf":
            parser = PDFParser(self.filename)
            self.parsed = parser.parse()
            self.collection_name = parser.book_title
            print(self.collection_name)

        self.mode = mode

        self.batch_size = batch_size

    def ingest_text(self):

        if self.text is None:
            text: str = load_textfile(self.filename)
        chunks: list[str] = split_into_chunks(text)
        all_embeddings: list[list[float]] = self._batch_embed(chunks)
        # chunks_with_vectors: list[dict] = []

        if not client.collection_exists(collection_name=self.collection_name):
            print(f"Collection '{self.collection_name}' doesn't exist.")
            client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=512, distance=models.Distance.COSINE
                ),
            )

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
        chunked = token_chunk(self.parsed)
        chunks = []
        for chunk in chunked:
            chunks.append(chunk["page_text"])
        all_embeddings = self._batch_embed(chunks)
        # vectorized  = []

        if not client.collection_exists(collection_name=self.collection_name):
            print(f"Collection '{self.collection_name}' doesn't exist.")
            client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=512, distance=models.Distance.COSINE
                ),
            )

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
        print(len(chunked))

        # for batch

    def _batch_embed(self, chunks):
        all_embeddings = []
        for i in range(0, len(chunks), self.batch_size):
            batch: list[str] = chunks[i : i + self.batch_size]
            batch_embeddings = embed(batch, "retrieval.passage")
            all_embeddings.extend(batch_embeddings)
        return all_embeddings


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


filename = "data/Asimov_the_foundation.pdf"
i = Ingest(mode="pdf", filename=filename)
i.ingest_pdf()
