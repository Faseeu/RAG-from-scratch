import os

import pymupdf

BASE = "data"


def pdf_loader(filename):
    page = pymupdf.open(os.path.join(BASE, filename))
    page_stc = page.get_text("dict")
    print(page_stc)

