from loader import load_textfile
from text_chunker import split_into_chunks
from embedding import embed
from storage import store


def ingest(filename="./basic_ai.txt", batch_size=128):
    text: str = load_textfile(filename)
    chunks: list[str] = split_into_chunks(text)
    all_embeddings: list[list[float]] = []
    chunks_with_vectors: list[dict] = []

    for i in range(0, len(chunks), batch_size):
        batch: list[str] = chunks[i : i + batch_size]
        batch_embeddings = embed(batch, "retrieval.passage")
        all_embeddings.extend(batch_embeddings)

    for chunk, embedding in zip(chunks, all_embeddings):
        chunks_with_vectors.append({"chunk": chunk, "embedding": embedding})

    store(chunks_with_vectors)
