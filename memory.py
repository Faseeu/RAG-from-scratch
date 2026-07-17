import json
from pprint import pprint


def _read_memory(filename):
    """Reads memory from file. Returns [] if file doesn't exist yet."""
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def conMemory(mode="store", memory=None, filename="conversation_memory.json"):
    if mode == "store":
        full_memory = _read_memory(filename)  # step 1: get old memory
        full_memory.append(memory)  # step 2: add new turn
        with open(filename, "w") as f:
            json.dump(full_memory, f)  # step 3: save it all back
        # pprint("Memory has been saved!!")

    elif mode == "load":
        full_memory = _read_memory(filename)
        # pprint(full_memory[:-5])
        return full_memory[-5:]


conMemory("load")
