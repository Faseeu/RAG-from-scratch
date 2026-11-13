from epub_to_text import EpubProcessor
import os

epub_file = "Fluent Python.epub"

# Set output directory to '.' (current directory)
processor = EpubProcessor(epub_file, ".")

# This will create 'book.txt' right next to 'book.epub'
processor.export_single_text()
