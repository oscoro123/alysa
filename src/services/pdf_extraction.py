import fitz  # PyMuPDF
import re
from typing import List, Dict
from services.requirement_filter import extract_requirement_candidates

SENTENCE_SPLIT_REGEX = re.compile(
    r'(?<=[.!?])\s+(?=[A-ZÅÄÖ])'
)

def split_into_paragraphs(text: str) -> List[str]:
    """
    Enkel men robust styckesdelning:
    - dubbla radbrytningar
    - fallback: långa rader
    """
    raw = re.split(r"\n\s*\n", text)
    paragraphs = [p.replace("\n", " ").strip() for p in raw]
    return [p for p in paragraphs if len(p) > 20]


def extract_pdf_data(pdf_bytes: bytes, filename: str) -> Dict:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    structured_pages = []

    for page_index, page in enumerate(doc):
        text = page.get_text()

        paragraphs = split_into_paragraphs(text)
        para_objs = []

        from services.pdf_extraction import split_into_sentences

        sentence_counter = 1

        for para in paragraphs:
            sentences = split_into_sentences(para)

            for sentence in sentences:
                para_objs.append({
                    "id": f"p{page_index+1}_{sentence_counter:03d}",
                    "text": sentence
                })
                sentence_counter += 1

        structured_pages.append({
            "page": page_index + 1,
            "paragraphs": para_objs
        })

    candidates = extract_requirement_candidates(structured_pages)

    return {
        "filename": filename,
        "page_count": len(doc),
        "used_ocr": False,
        "candidates": candidates
    }

def split_into_sentences(text: str) -> list[str]:
    """
    Delar text i meningar på ett relativt säkert sätt
    för svenska juridiska texter.
    """
    sentences = SENTENCE_SPLIT_REGEX.split(text)
    return [s.strip() for s in sentences if len(s.strip()) > 10]
