from dataclasses import dataclass

from core.register_collection import collections_index
from embedding.embedding import embed
from qdrantDB.client import client
from settings import settings


@dataclass
class Chunk:
    text: str
    metadata: dict


def retrieve(
    query: str,
    filter=None,
    threshold=0.5,
    top_k: int = settings.retrieval_top_k,
    collection_name: str | None = None,
):
    if collection_name is None:
        collection_name = settings.collection_name
    col: str
    for collection in collections_index.catalog:
        if collection["collection_name"] == collection_name:
            col = collection
            break

    if col is None:
        raise RuntimeError(f"'{collection_name}' not in registry. Ingest first.")

    if col["embedding_model"] != settings.embedding_model:
        raise RuntimeError(
            f"Collection built with {col.get('embedding_model')}, "
            f"querying with {settings.embedding_model}. Delete collection + registry row, re-ingest."
        )

    # if filter is None:
    #     filter = {"title": "The Foundation Trilogy"}
    # filterKey: str
    # filterValue: str
    # for key, value in filter.items():
    #     filterKey = key
    #     filterValue = value

    query_embed = embed([query], task="retrieval.query", mode="local")[0]
    results = client.query_points(
        collection_name=collection_name,
        query=query_embed,
        # query_filter=models.Filter(
        #     must=[
        #         models.FieldCondition(
        #             key=filterKey, match=models.MatchValue(value=filterValue)
        #         )
        #     ]
        # ),
        score_threshold=threshold,
        limit=top_k,
    )
    # chunks: list[str] = []
    # metadata: list[dict] = []
    chunks_data = []
    for point in results.points:
        print(point.score, point.payload.get("page_no"))
        payload = point.payload.copy()
        text = payload.pop("page_text")
        chunks_data.append(Chunk(text=text, metadata=payload))
        # chunks.append(point.payload["page_text"])
        # metadata.append(point.payload)
    return chunks_data


def get_corpus_from_qdrant(collection_name: str | None = None):
    if collection_name is None:
        collection_name = settings.collection_name

    all_chunks = []
    next_page = None
    while True:
        records, next_page = client.scroll(
            collection_name=collection_name,
            limit=10000,
            with_payload=True,
            with_vectors=False,
            offset=next_page,
        )
        all_chunks.extend([r.payload["page_text"] for r in records])

        if next_page is None:
            break
    return all_chunks


if __name__ == "__main__":
    # query = "who is the emperor, and what is the small kingdoms within the empire"
    # chunks, meta = retrieve(query)
    # print(meta)
    # print(chunks)
    # print(len(chunks))
    print(get_corpus_from_qdrant("The Foundation Trilogy"))
