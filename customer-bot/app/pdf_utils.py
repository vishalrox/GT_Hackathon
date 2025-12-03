# app/pdf_utils.py
from pypdf import PdfReader
import re

EMAIL_RE = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
PHONE_RE = re.compile(r"""(
    (?:(?:\+?\d{1,3})?[-.\s(]*)?   # optional country code
    (?:\(?\d{2,4}\)?[-.\s]*)?      # optional area code
    \d{3,4}[-.\s]*\d{3,4}          # main number parts
)""", re.VERBOSE)
AADHAAR_RE = re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b")

def extract_pdf_text(path) -> str:
    text_parts = []
    try:
        reader = PdfReader(str(path))
        for p in reader.pages:
            txt = p.extract_text()
            if txt:
                text_parts.append(txt)
    except Exception:
        return ""
    return "\n".join(text_parts)

def mask_text_simple(text: str) -> str:
    """
    Conservative masking of PII inside docs before indexing.
    """
    masked = text
    masked = EMAIL_RE.sub("<EMAIL_MASK>", masked)
    masked = AADHAAR_RE.sub("<ID_MASK>", masked)
    phones = PHONE_RE.findall(masked)
    seen = []
    for p in phones:
        p_clean = p.strip()
        if not p_clean:
            continue
        if p_clean not in seen:
            seen.append(p_clean)
            masked = masked.replace(p_clean, "<PHONE_MASK>")
    return masked
