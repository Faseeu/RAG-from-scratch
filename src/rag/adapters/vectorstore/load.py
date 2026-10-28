import uuid

from qdrant_client import QdrantClient, models

client = QdrantClient(host="localhost", port=6333)

client.create_collection(
    collection_name="atomic_habits",
    vectors_config=models.VectorParams(size=4, distance=models.Distance.COSINE),
)

# client.upsert(
#     collection_name="test_1",
#     points=[
#         models.PointStruct(
#             id=1, vector=[0.1, 0.3, 0.2, 0.5], payload={"topic": "cooking"}
#         ),
#         models.PointStruct(
#             id=2, vector=[0.7, 0.6, 0.2, 0.5], payload={"topic": "eating"}
#         ),
#     ],
# )

# results = client.query_points(
#     collection_name="test_1", query=[0.3, 0.6, 0.3, 0.8], limit=2
# )
# print(results)


# client.create_collection(
#     collection_name="test_4",
#     vectors_config=models.VectorParams(size=4, distance=models.Distance.COSINE),
# )


NAMESPACE = uuid.UUID(
    "12345678-1234-5678-1234-567812345678"
)  # any fixed constant, made up once, never changed


def generate_id(text: str) -> str:
    return str(uuid.uuid5(NAMESPACE, text))


# def id_gen():
#     return str(uuid.uuid4())


# client.upsert(
#     collection_name="test_4",
#     points=[
#         models.PointStruct(
#             id=id_gen(), vector=[0.1, 0.2, 0.4, 0.2], payload={"label": "animal"}
#         ),
#         models.PointStruct(
#             id=id_gen(), vector=[0.5, 0.88, 0.3, 0.1], payload={"label": "machine"}
#         ),
#         models.PointStruct(
#             id=id_gen(),
#             vector=[0.99, 0.28, 0.7, 0.14],
#             payload={
#                 "text": "the actual chunk text goes right here",
#                 "source": "atomic_habits.txt",
#                 "chunk_index": 5,
#             },
#         ),
#     ],
# )

# results = client.query_points(
#     collection_name="test_4", query=[0.9, 0.3, 0.6, 0.1], limit=1
# )

# client.create_collection(
#     collection_name="toy_2",
#     vectors_config=models.VectorParams(size=4, distance=models.Distance.COSINE),
# )
client.upsert(
    collection_name="toy_2",
    points=[
        models.PointStruct(
            id=generate_id("this is the tittle of the book"),
            vector=[0.99, 0.28, 0.7, 0.14],
            payload={
                "text": "this is the tittle of the book",
                "source": "atomic_habits.txt",
                "chunk_index": 0,
            },
        ),
        models.PointStruct(
            id=generate_id("this is the page 124"),
            vector=[0.1, 0.2, 0.3, 0.14],
            payload={
                "text": "this is the page 124",
                "source": "atomic_habits.txt",
                "chunk_index": 1,
            },
        ),
        models.PointStruct(
            id=generate_id("this is the title of the chp 1"),
            vector=[0.99, 0.1, 0.2, 0.3],
            payload={
                "text": "this is the title of the chp 1",
                "source": "atomic.txt",
                "chunk_index": 2,
            },
        ),
    ],
)

results = client.query_points(
    collection_name="toy_2",
    query=[0.5, 0.2, 0.1, 0.4],
    query_filter=models.Filter(
        must=[
            models.FieldCondition(
                key="source", match=models.MatchValue(value="atomic_habits.txt")
            )
        ]
    ),
    limit=2,
)
print(results.points[0].payload["text"])
