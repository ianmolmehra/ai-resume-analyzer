import re
from typing import List, Optional


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return text.strip()


def extract_email(text: str) -> Optional[str]:
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    matches = re.findall(pattern, text)
    return matches[0] if matches else None


def extract_phone(text: str) -> Optional[str]:
    patterns = [
        r'\+?1?\s*[-.]?\s*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            phone = re.sub(r'[^\d+]', '', matches[0])
            if len(phone) >= 10:
                return matches[0].strip()
    return None


def extract_linkedin(text: str) -> Optional[str]:
    pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+'
    matches = re.findall(pattern, text, re.IGNORECASE)
    return matches[0] if matches else None


def extract_github(text: str) -> Optional[str]:
    pattern = r'(?:https?://)?(?:www\.)?github\.com/[\w\-]+'
    matches = re.findall(pattern, text, re.IGNORECASE)
    return matches[0] if matches else None


def extract_years_of_experience(text: str) -> float:
    patterns = [
        r'(\d+\.?\d*)\s*\+?\s*years?\s+(?:of\s+)?(?:work\s+)?experience',
        r'(\d+\.?\d*)\s*\+?\s*yrs?\s+(?:of\s+)?(?:work\s+)?experience',
        r'experience\s+of\s+(\d+\.?\d*)\s+years?',
    ]
    years = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            try:
                years.append(float(m))
            except ValueError:
                pass
    return max(years) if years else 0.0


def calculate_date_range(start: str, end: str) -> float:
    """Calculate years between two date strings."""
    import re
    from datetime import datetime

    def parse_date(s: str) -> Optional[datetime]:
        if not s:
            return None
        s = s.strip().lower()
        if s in ("present", "current", "now", "ongoing"):
            return datetime.now()
        formats = ["%b %Y", "%B %Y", "%Y-%m", "%m/%Y", "%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        year_match = re.search(r'\d{4}', s)
        if year_match:
            try:
                return datetime(int(year_match.group()), 1, 1)
            except ValueError:
                pass
        return None

    d1 = parse_date(start)
    d2 = parse_date(end)
    if d1 and d2:
        delta = abs((d2 - d1).days) / 365.25
        return round(delta, 1)
    return 0.0


def tokenize_text(text: str) -> List[str]:
    tokens = re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#.]*\b', text)
    return [t.lower() for t in tokens]
