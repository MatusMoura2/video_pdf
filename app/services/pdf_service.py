import pdfplumber
from pathlib import Path

def extract_pdf_text_with_metadata(pdf_path: Path):
    """
    Extracts text from PDF preserving basic structural info.
    (Can be expanded later to parse timestamps if present in the PDF)
    """
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                data.append({
                    "page": i + 1,
                    "text": text
                })
    return data
