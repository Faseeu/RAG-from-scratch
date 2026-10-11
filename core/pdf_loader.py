# BASE = "data"
# def pdf_loader(filename):
#     frequency = {}
#     all_pages = pymupdf.open(os.path.join(BASE, filename))
#     limit = len(all_pages)
#     print(limit)
#     structure = []
#     for l in range(limit):
#         page_no = l
#         page_stc = all_pages[page_no].get_text("dict")
#         # print(page_no)
#         size, struct = organize(page_stc)
#         structure.extend(struct)
#         for s, num in size.items():
#             s = round(s, 0)
#             frequency[s] = frequency.get(s, 0) + num
#     # print(frequency)
#     # big_heading = max(frequency.keys())
#     # # heading = frequency[1]
#     body = max(frequency, key=frequency.get)
#     # print(big_heading,body)
#     heading_sizes = sorted(
#         [s for s in frequency if s > body],
#         reverse=True,
#     )
#     # print(heading_sizes)
#     size_to_level = {s: i for i, s in enumerate(heading_sizes)}
#     # print(size_to_level)
#     cl = classify(structure, body, size_to_level)
#     # cl = classify(all_pages, body, size_to_level)
#     # print(cl)
#     paragraphs = paragraphy(cl, size_to_level)
#     # print(paragraphs)
#     # print(page_stc)
#     chunked_paragraphs = []
#     for paragraph in paragraphs:
#         chunked = chunker(paragraph["body"])
#         for chunk in chunked:
#             chunked_paragraphs.append({"heading": paragraph["heading"], "body": chunk})
#     for level in size_to_level.values():
#         for paragrapgh in cl:
#             # print(level)
#             # print(paragrapgh)
#             pl = paragrapgh["level"]
#             if level == pl:
#                 print(f" LEVEL: {level},    PARAGRAPH: {paragrapgh['text']}")
#     print(len(chunked_paragraphs))
#     print(type(chunked_paragraphs))
# def organize(all_pages):
#     structure = []
#     sizes = {}
#     for block in all_pages["blocks"]:
#         if block.get("type") == 0 and "lines" in block:
#             for line in block["lines"]:
#                 for span in line["spans"]:
#                     text = span["text"]
#                     size = span["size"]
#                     sizes[size] = sizes.get(size, 3) + 1
#                     dct = {"text": text, "size": size}
#                     structure.append(dct)
#     # print(len(structure))
#     # print(sizes)
#     return sizes, structure
# def classify(all_pages, body_size, size_to_level):
#     classified = []
#     # for page in all_pages:
#     #     page = page.get_text("dict")
#     #     for block in page["blocks"]:
#     #         if block.get("type") == 0 and "lines" in block:
#     #             for line in block["lines"]:
#     #                 for span in line["spans"]:
#     #                     text = span["text"]
#     #                     size = span["size"]
#     #                     classified.append(
#     #                         {
#     #                             "text": text,
#     #                             "is_heading": size > body_size,
#     #                             "level": size_to_level.get(size, 0),
#     #                         }
#     #                     )
#     for span in all_pages:
#         text = span.get("text", "")
#         size = round(span.get("size", 0), 0)
#         classified.append(
#             {
#                 "text": text,  # span["text"]
#                 "is_heading": size > body_size,  # span["size"]
#                 "level": size_to_level.get(size, 0),  # span["size"]
#             }
#         )
#     # print(size_to_level)
#     print(len(classified))
#     return classified
# def paragraphy(classified, size_to_level):
#     paragrapghs = []
#     current = {
#         "book_name": "UNTITLED",
#         "chapter": "UNTITLED",
#         "section": "UNTITLED",
#         "heading": "UNTITLED",
#         "body": "",
#     }
#     for span in classified:
#         text = span["text"]
#         # if span["level"] >
#         if span["is_heading"]:
#             if current["body"].strip():
#                 paragrapghs.append(current)
#             current = {"heading": text, "body": ""}
#         elif not span["is_heading"]:
#             if current["body"]:
#                 current["body"] = current["body"] + " " + text
#             else:
#                 current["body"] = text
#             # print(latest)
#     if current["body"].strip():
#         paragrapghs.append(current)
#     return paragrapghs
# def chunker(text: str, size: int = 200, overlap: int = 20) -> list[str]:
#     chunks: list[str] = []
#     words: list[str] = text.split()
#     step: int = size - overlap
#     i = 0
#     while i < len(words):
#         # start: int = max(0, i - overlap)
#         # end: int = start + size
#         start: int = i
#         end: int = i + size
#         chunk_words: list[str] = words[start:end]
#         chunk_text: str = " ".join(chunk_words)
#         chunks.append(chunk_text)
#         i += step
#     return chunks
# def _get_span(all_pages):
#     for block in all_pages["blocks"]:
#         if block.get("type") == 0 and "lines" in block:
#             for line in block["lines"]:
#                 for span in line["spans"]:
#                     text = span["text"]
#                     size = span["size"]
import time
from dataclasses import dataclass

import pymupdf
import pymupdf4llm

from settings import settings


@dataclass
class Payload:
    page_no: int
    page_text: str
    book_title: str
    confidence: float
    source: str


class PDFParser:
    def __init__(self, filename=settings.filename):
        self.filename = filename

        # self.doc = pymupdf.open(self.filename)
        self.book_title = "UNTITLED"
        # print(self.doc.get_toc())
        # print(self.doc.metadata)

        self.parsed_book = None

    def parse(self):
        if self.parsed_book is not None:  # return cached
            return self.parsed_book
        self.parsed_book = []
        t = time.time()
        self.doc = pymupdf.open(self.filename)
        # toc = self.doc.get_toc()
        metadata = self.doc.metadata
        self.book_title = metadata.get("title")
        # print(metadata, self.book_title)

        for i, page in enumerate(self.doc):
            text = pymupdf4llm.to_markdown(self.doc, pages=[i]).strip()
            # payload = {
            #     "page_no": i + 1,
            #     "page_text": text,
            #     "book_title": self.book_title,
            #     # "table_of_contents": toc,
            #     "confidence": 1.0 if len(text) > 100 else 0.0,
            #     "source": self.filename,
            # 0
            payload = Payload(
                page_no=i + 1,
                page_text=text,
                book_title=self.book_title,
                confidence=1.0 if len(text) > 100 else 0.0,
                source=self.filename,
            )
            # self.payload
            self.parsed_book.append(payload)

        # md = pmp.to_markdown(self.filename, pages=range(100))
        # print(len(md))
        # print(self.parsed_book)
        print(len(self.parsed_book))
        time_taken = time.time() - t
        print("parse took", time_taken)
        return self.parsed_book


# # pdf_loader("Asimov_the_foundation.pdf")
# # pdf_loader("Muhammad Messenger of Allah - Ash-shifa of Qadi Iyad.pdf")

# parser = PDFParser("data/Asimov_the_foundation.pdf")
# # print(parser.parse())
# parser.parse()
# print(parser.book_title)
# # import time

# doc = pymupdf.open("data/Asimov_the_foundation.pdf")

# t = time.time()
# txt = ""
# for p in doc[:100]:  # only 100 pages
#     txt += p.get_text("text")
# print("pymupdf text 5 pages:", time.time() - t, "len", len(txt))

# t = time.time()
# md = pmp.to_markdown("data/Asimov_the_foundation.pdf", pages=range(100))
# print("pmp 5 pages:", time.time() - t, "len", len(md))
