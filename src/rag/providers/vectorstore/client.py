from qdrant_client import QdrantClient

from rag.config import settings

client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
