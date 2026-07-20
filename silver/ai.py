"""Silver — assistant helpers (rule-based for the MVP).

These are transparent heuristics, not an external LLM: they suggest a section,
keywords and a title for a post, and flag potentially sensitive info before
publishing. Nothing is ever published automatically. A production deployment
can swap these for a real model behind the same functions.
"""
import re

# keyword → category slug
CATEGORY_KEYWORDS = {
    "tech": ["تقنية", "برمجة", "كمبيوتر", "هاتف", "جوال", "تطبيق", "ذكاء", "tech", "code", "app", "ai", "software", "phone"],
    "cars": ["سيارة", "سيارات", "محرك", "قيادة", "car", "cars", "engine", "drive"],
    "travel": ["سفر", "رحلة", "طيران", "فندق", "سياحة", "travel", "trip", "flight", "hotel"],
    "photography": ["تصوير", "صورة", "كاميرا", "عدسة", "photo", "camera", "lens"],
    "gaming": ["لعبة", "ألعاب", "قيمنق", "بلايستيشن", "game", "gaming", "playstation", "xbox"],
    "sports": ["رياضة", "كرة", "مباراة", "تمرين", "sport", "football", "match", "gym"],
    "education": ["تعليم", "دراسة", "جامعة", "دورة", "study", "course", "learn", "university"],
    "entertainment": ["ترفيه", "فيلم", "مسلسل", "موسيقى", "movie", "series", "music", "fun"],
    "business": ["عمل", "مشروع", "تجارة", "تسويق", "business", "startup", "marketing"],
}

SENSITIVE_PATTERNS = [
    (r"\b\d{10,16}\b", "رقم طويل قد يكون رقم هاتف أو بطاقة / long number (phone or card?)"),
    (r"[^@\s]+@[^@\s]+\.[^@\s]+", "بريد إلكتروني ظاهر / visible email address"),
    (r"(كلمة المرور|password|passwd)\s*[:=]", "كلمة مرور ظاهرة / visible password"),
]


def suggest_category(text: str) -> str | None:
    low = (text or "").lower()
    best, best_hits = None, 0
    for slug, words in CATEGORY_KEYWORDS.items():
        hits = sum(1 for w in words if w in low)
        if hits > best_hits:
            best, best_hits = slug, hits
    return best


def suggest_section(text: str, has_category: bool, city: str) -> str:
    """Suggest the most fitting section slug for a post."""
    low = (text or "").lower()
    if any(w in low for w in ["أصدقائي", "خاص", "عائلتي", "friends only", "private"]):
        return "circle"
    if has_category or suggest_category(text):
        return "interests"
    if city and any(w in low for w in [city.lower(), "حي", "مدينت", "قريب", "nearby", "local"]):
        return "nearby"
    return "front"


def suggest_keywords(text: str, max_kw: int = 5) -> list[str]:
    words = re.findall(r"[\w؀-ۿ]{4,}", text or "")
    seen, out = set(), []
    for w in words:
        lw = w.lower()
        if lw not in seen:
            seen.add(lw)
            out.append(w)
        if len(out) >= max_kw:
            break
    return out


def suggest_title(text: str) -> str:
    first = (text or "").strip().split("\n")[0]
    return first[:60] + ("…" if len(first) > 60 else "")


def sensitive_warnings(text: str) -> list[str]:
    hits = []
    for pattern, label in SENSITIVE_PATTERNS:
        if re.search(pattern, text or "", re.IGNORECASE):
            hits.append(label)
    return hits
