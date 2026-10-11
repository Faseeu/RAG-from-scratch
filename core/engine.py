from settings import settings


class Engine:
    name: str = "RAG system"

    def __init__(self, filename: str | None = None, collection_name: str | None = None):

        self.filename = settings.filename if filename is None else filename
        self.collection_name = (
            settings.collection_name if collection_name is None else collection_name
        )

    def ingest(self):
        pass

    def retrieve(self):
        pass

    def generate(self):
        pass

    def preprocess(self):
        pass
