import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class Collection:
    collection_name: str
    display_name: str
    source_file: str
    file_hash: str
    chunk_count: int
    embedding_model: str
    embedding_dim: int
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class CollectionsIndex:
    def __init__(self):
        self.filepath = Path("data/document_registry.json")
        self.catalog = self.show()

    def show(self):
        try:
            if self.filepath.exists() is not True:
                self.filepath.touch(exist_ok=True)

            with open(self.filepath, "r") as f:
                full_catalog = json.load(f)
                return full_catalog
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def register_collection(self, collection: Collection):
        # full_catalog = self.show()
        collection.created_at = datetime.now().isoformat()

        # collection = {
        #     "collection_name": collection_name,
        #     "display_name": display_name,
        #     "source_file": source_file,
        #     "file_hash": file_hash,
        #     "chunk_count": chunk_count,
        #     "created_at": created_at,
        # }

        existing_collections = [
            collection["collection_name"] for collection in self.catalog
        ]

        if collection.collection_name not in existing_collections:
            self.catalog.append(asdict(collection))
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.catalog, f, indent=2)

    def list_collections(self):
        self.catalog = self.show()
        print(f"DEBUG: Catalog contains: {self.catalog}")

        collection_names = [
            collection["collection_name"] for collection in self.catalog
        ]

        printable_catalog = f"\n{'_' * 20}\n".join(
            f"{i}:{c}" for i, c in enumerate(collection_names)
        )

        print(printable_catalog)
        return collection_names


collections_index = CollectionsIndex()
