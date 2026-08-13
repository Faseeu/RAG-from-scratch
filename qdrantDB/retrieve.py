from qdrant_client import QdrantClient

from core.embedding import embed

client = QdrantClient(host="localhost", port=6333)


def retrieve(
    query: str,
    filter=None,
    threshold=0.5,
    top_k: int = 10,
    collection_name="The Foundation Trilogy",
):
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
    chunks: list[str] = []
    metadata: list[dict] = []
    for point in results.points:
        chunks.append(point.payload["page_text"])
        metadata.append(point.payload)
    return chunks, metadata


def get_corpus_from_qdrant(collection_name):
    all_chunks = []
    next_page = None
    while True:
        records, next_page = client.scroll(
            collection_name=collection_name,
            limit=10000,
            with_payload=True,
            with_vectors=False,
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
