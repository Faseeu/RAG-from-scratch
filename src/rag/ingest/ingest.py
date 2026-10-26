from rag.ingest.chunkers.text import split_into_chunks
from rag.ingest.loaders.text import load_textfile
from rag.providers.vectorstore.storage import store
from rag.providers.embeddings.batch_embed import _batch_embed
from rag.config import settings


def ingest(filename="./basic_ai.txt", batch_size=None):
    if batch_size is None:
        batch_size = settings.batch_size

    text: str = load_textfile(filename)
    chunks: list[str] = split_into_chunks(text)
    all_embeddings: list[list[float]] = _batch_embed()
    chunks_with_vectors: list[dict] = []

    # for i in range(0, len(chunks), batch_size):
    #     batch: list[str] = chunks[i : i + batch_size]
    #     batch_embeddings = embed(batch, "retrieval.passage")
    #     all_embeddings.extend(batch_embeddings)

    for chunk, embedding in zip(chunks, all_embeddings):
        chunks_with_vectors.append({"chunk": chunk, "embedding": embedding})

    store(chunks_with_vectors)
