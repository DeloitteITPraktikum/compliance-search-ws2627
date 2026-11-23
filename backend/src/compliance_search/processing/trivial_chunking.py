"""Trivial chunking: split the text of each PDF into chunks of fixed size with overlap."""
import re
from pathlib import Path

from pypdf import PdfReader

# Path to one test PDF, seen from the backend folder
PDF_PATH = Path("../data/pdfs/active/32025R0532_DE.pdf")

CHUNK_SIZE = 2000  # characters per chunk (about 500 tokens)
OVERLAP = 200 # characters of overlap between chunks (10 %)

def clean (text : str) -> str:
    """Replace line breaks and multiple spaces with a single space."""
    return re.sub(r"\s+", " ", text).strip()

# Open the PDF
reader = PdfReader(PDF_PATH)

# Go through all pages and print the page number and the length of the text
for page_number, page in enumerate(reader.pages, start=1):
    text = clean(page.extract_text())
    print (page_number, len(text))

