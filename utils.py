# utils.py
import re
from datetime import datetime
from typing import Optional

from config import KEYWORDS, XINJIANG_TERMS


def is_xinjiang(text: str) -> bool:
    return any(t in text for t in XINJIANG_TERMS)


def has_keyword(title: str) -> bool:
    return any(k in title for k in KEYWORDS)


def is_active(start: Optional[datetime], end: Optional[datetime]) -> bool:
    now = datetime.now()
    if end is None:
        return True
    if start and start > now:
        return False
    return now <= end


def parse_date(text: str) -> Optional[datetime]:
    if not text:
        return None
    text = text.strip()

    patterns = [
        (r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})(?:\s+(\d{1,2}):(\d{1,2}))?", False),
        (r"(\d{4})年(\d{1,2})月(\d{1,2})日(?:\s*(\d{1,2})[时点](\d{1,2})?分?)?", True),
    ]

    for pat, _ in patterns:
        m = re.search(pat, text)
        if m:
            groups = m.groups()
            y, mo, d = int(groups[0]), int(groups[1]), int(groups[2])
            h = int(groups[3]) if groups[3] else 0
            mi = int(groups[4]) if groups[4] else 0
            try:
                return datetime(y, mo, d, h, mi)
            except ValueError:
                continue
    return None