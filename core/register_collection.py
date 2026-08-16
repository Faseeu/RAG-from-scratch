import json
from datetime import datetime
from pathlib import Path


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

    def register_collection(
        self,
        collection_name: str,
        display_name: str,
        source_file: str,
        file_hash: str,
        chunk_count: int,
        created_at=datetime.now().isoformat(),
    ):
        # full_catalog = self.show()

        collection = {
            "collection_name": collection_name,
            "display_name": display_name,
            "source_file": source_file,
            "file_hash": file_hash,
            "chunk_count": chunk_count,
            "created_at": created_at,
        }

        existing_collections = [
            collection["collection_name"] for collection in self.catalog
        ]

        if collection_name not in existing_collections:
            self.catalog.append(collection)
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.catalog, f, indent=2)


collections_index = CollectionsIndex()
