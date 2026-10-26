import re


def sanitize_name(name: str):
    name = name.lower().strip()

    name = re.sub(r"[^a-z0-9_-]+", "_", name)
    return name.strip("_")
