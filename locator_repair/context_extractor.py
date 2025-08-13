import re
from bs4 import BeautifulSoup

from locator_repair.helpers.signInPage import PREFERRED_CLASS_KEYS, PREFERRED_TAGS, ATTR_KEYS, SYNONYMS, FILLER_WORDS

def _keywords_from_description(desc: str) -> set[str]:
    if not desc:
        return set()
    d = re.sub(r"[^a-z0-9\s_-]+", " ", desc.lower())
    parts = {p for p in re.split(r"\s+", d) if p and p not in FILLER_WORDS}
    # expand synonyms
    expanded = set(parts)
    for p in list(parts):
        if p in SYNONYMS:
            expanded |= SYNONYMS[p]
    # multiword variant
    # if "user" in parts and "name" in parts:
    #     expanded.add("user name")
    return expanded

def _tag_matches_keywords(tag, keywords: set[str]) -> bool:
    # inner text
    if any(k in (tag.get_text(strip=True) or "").lower() for k in keywords):
        return True
    # attributes
    for a in ATTR_KEYS:
        if tag.has_attr(a):
            v = tag.get(a)
            v = " ".join(v) if isinstance(v, list) else str(v)
            if any(k in v.lower() for k in keywords):
                return True
    return False

def _pick_context(tag):
    # Prefer a nearby ancestor whose classes suggest a form group
    cur = tag
    while cur and getattr(cur, "name", None):
        classes = set(cur.get("class", []))
        if classes & PREFERRED_CLASS_KEYS:
            return cur
        cur = cur.parent
    # Fallback: nearest preferred tag
    node = tag.find_parent(PREFERRED_TAGS)
    return node or tag.parent

def extract_relevant_html(dom: str, description: str, max_matches: int = 3) -> str:
    soup = BeautifulSoup(dom, "html.parser")
    keywords = _keywords_from_description(description)

    matches = []
    for tag in soup.find_all(True):
        try:
            if _tag_matches_keywords(tag, keywords):
                matches.append(tag)
                if len(matches) >= max_matches:
                    break
        except Exception:
            continue

    if not matches:
        # last resort, return the top of the DOM
        return dom[:10000]

    snippets = []
    for t in matches:
        ctx = _pick_context(t)
        snippets.append(str(ctx))

    return ("\n<!-- match -->\n".join(snippets))[:10000]

