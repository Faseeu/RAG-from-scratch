def load_textfile(location):
    text: str
    with open(location, "r") as f:
        text = f.read()

    return text
