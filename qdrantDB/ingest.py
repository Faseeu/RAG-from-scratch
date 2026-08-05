import uuid

from qdrant_client import QdrantClient, models

from core.embedding import embed
from core.loader import load_textfile
from core.text_chunker import split_into_chunks

client = QdrantClient(host="localhost", port=6333)


NAMESPACE = uuid.UUID(
    "12345678-1234-5678-1234-567812345678"
)  # any fixed constant, made up once, never changed


def generate_id(text: str) -> str:
    return str(uuid.uuid5(NAMESPACE, text))


def ingest(
    text=None,
    collection_name="atomic_habits",
    filename="basic_ai.txt",
    batch_size=128,
    # overwrite=True,
):
    if text is None:
        text: str = load_textfile(filename)
    chunks: list[str] = split_into_chunks(text)
    all_embeddings: list[list[float]] = []
    # chunks_with_vectors: list[dict] = []

    if not client.collection_exists(collection_name=collection_name):
        print(f"Collection '{collection_name}' doesn't exist.")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=512, distance=models.Distance.COSINE
            ),
        )

    for i in range(0, len(chunks), batch_size):
        batch: list[str] = chunks[i : i + batch_size]
        batch_embeddings = embed(batch, "retrieval.passage")
        all_embeddings.extend(batch_embeddings)

    for i, (chunk, embedding) in enumerate(zip(chunks, all_embeddings)):
        metadata = {"title": "atomic habits", "author": "james_clear"}
        chunk_index = i
        metadata["chunk_index"] = chunk_index
        metadata["text"] = chunk
        client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=generate_id(chunk),
                    vector=embedding,
                    payload=metadata,
                )
            ],
        )
