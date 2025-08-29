import re
from typing import List

_CFR_RE = re.compile(r"(?:\b\d+\s*CFR\s*)?(\d{3,4}\.\d+)", re.IGNORECASE)

def extract_cfr_codes(text: str) -> List[str]:
    '''
    Return a list of normalized CFR codes, e.g., ["211.22", "211.113", "820.70"]
    '''
    if not text:
        return []
    found = _CFR_RE.findall(text)
    norm = []
    for code in found:
        cleaned = []
        for ch in code:
            if ch.isdigit() or ch == ".":
                cleaned.append(ch)
            else:
                break
        val = "".join(cleaned)
        if val and val not in norm:
            norm.append(val)
    return norm
