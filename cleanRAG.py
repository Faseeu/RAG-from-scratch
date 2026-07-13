from storage import load, store

from ingest import ingest

ingest()
data = load()
for i, vector in enumerate(data):
    chunk = vector["chunk"]
    chunk= chunk.replace("\n","")
    # chunk = "".join([char for char in chunk if char != "\n"])
    print(chunk)
    data[i]["chunk"] = chunk
    print(data[0])

store(data)