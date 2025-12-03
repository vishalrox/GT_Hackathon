# app/masking.py
import re
from typing import Tuple, Dict

EMAIL_RE = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
PHONE_RE = re.compile(r"""(
    (?:(?:\+?\d{1,3})?[-.\s(]*)?   # optional country code
    (?:\(?\d{2,4}\)?[-.\s]*)?      # optional area code
    \d{3,4}[-.\s]*\d{3,4}          # main number parts
)""", re.VERBOSE)

def _partial_mask_email(email: str) -> str:
    # vishal.mehta@gmail.com -> v***.m***@g***.com approximate
    try:
        local, domain = email.split("@", 1)
    except ValueError:
        return "<EMAIL_MASK>"
    def pm(s):
        if len(s) <= 2:
            return s[0] + "*"*(len(s)-1)
        return s[0] + "*"*(len(s)-2) + s[-1]
    dom_parts = domain.split(".")
    dom_masked = ".".join([pm(p) for p in dom_parts])
    return pm(local) + "@" + dom_masked

def _partial_mask_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if len(digits) <= 4:
        return "*" * len(digits)
    return "*"*(len(digits)-4) + digits[-4:]

def mask_pii(text: str) -> Tuple[str, Dict[str,str]]:
    """
    Replace emails and phones with tokens: <EMAIL_1>, <PHONE_1>, ...
    Returns masked_text and a mapping {token: original_value}
    """
    mapping = {}
    out = text

    # emails
    emails = EMAIL_RE.findall(out)
    e_seen = []
    for e in emails:
        if e in e_seen:
            continue
        e_seen.append(e)
        token = f"<EMAIL_{len(mapping)+1}>"
        mapping[token] = e
        out = out.replace(e, token)

    # phones
    phones = PHONE_RE.findall(out)
    p_seen = []
    for p in phones:
        p_clean = p.strip()
        if not p_clean:
            continue
        if p_clean in p_seen:
            continue
        p_seen.append(p_clean)
        token = f"<PHONE_{len(mapping)+1}>"
        mapping[token] = p_clean
        out = out.replace(p_clean, token)

    return out, mapping

def unmask_safe(text: str, mapping: Dict[str,str]) -> str:
    """
    Replace tokens like <PHONE_1> with partially masked forms (not original).
    """
    out = text
    for token, original in mapping.items():
        if token.startswith("<EMAIL"):
            safe = _partial_mask_email(original)
        elif token.startswith("<PHONE"):
            safe = _partial_mask_phone(original)
        else:
            safe = "<MASKED>"
        out = out.replace(token, safe)
    return out
