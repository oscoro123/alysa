import fitz  # PyMuPDF
import re
from typing import List, Dict

SKALL_TERMS = [
    "skall", "ska", "måste", "krävs", "åligger", "får ej", "icke", "förbinder sig att"
]

BOR_TERMS = [
    "bör", "borde", "önskvärt", "meriterande", "eftersträvas", "ser gärna", "bedöms positivt"
]


def split_into_sentences(text: str) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 10]


def classify_sentence(sentence: str):
    lowered = sentence.lower()

    matched_skall = [t for t in SKALL_TERMS if t in lowered]
    matched_bor = [t for t in BOR_TERMS if t in lowered]

    if matched_skall:
        return "SKALL", matched_skall
    if matched_bor:
        return "BÖR", matched_bor

    return None, []


def extract_requirements_from_pdf(pdf_path: str) -> Dict:
    doc = fitz.open(pdf_path)

    requirements = []
    used_ocr = False
    req_counter = 1

    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)
        page_text = page.get_text().strip()
        source = "text"

        if len(page_text) < 50:
            # OCR fallback placeholder
            used_ocr = True
            page_text = ""
            source = "ocr"

        sentences = split_into_sentences(page_text)

        for sentence in sentences:
            classification, matched_terms = classify_sentence(sentence)
            if not classification:
                continue

            requirements.append({
                "id": f"p{page_index + 1}_r{req_counter:02d}",
                "page": page_index + 1,
                "source": source,
                "text": sentence,
                "classification": classification,
                "matched_terms": matched_terms
            })
            req_counter += 1

    return {
        "page_count": doc.page_count,
        "used_ocr": used_ocr,
        "requirements": requirements
    }
