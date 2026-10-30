"""Identity / dedupe helpers. Pure functions, no DB, no HTTP."""
from __future__ import annotations

import re
import unicodedata
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

_TRACKING = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "gclid", "fbclid", "ref", "referrer", "trk", "trk_email", "src",
    "ta_source", "u_sr_id",
}


def url_canonical(url: str) -> str:
    """Lowercase host, strip fragment + tracking params, sort the rest.

    Non-tracking query params are kept: some boards (LinkedIn) put the job id in
    the query, so dropping all of it would merge distinct jobs.
    """
    if not url:
        return ""
    parts = urlsplit(url.strip())
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
             if k.lower() not in _TRACKING]
    query.sort()
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path,
                       urlencode(query), ""))


def _fold(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "").casefold()
    return re.sub(r"\s+", " ", re.sub(r"[^0-9a-z]+", " ", text)).strip()


def title_norm(title: str) -> str:
    return _fold(title)


def company_slug(company: str) -> str:
    return _fold(company).replace(" ", "-")


def extract_external_id(url: str) -> str:
    """Board-specific job id from the url path.

    ITViec: trailing number (…/foo-5349). TopCV: last segment (…/slug/2316742.html).
    """
    path = urlsplit(url or "").path.rstrip("/")
    m = re.search(r"(\d+)\s*$", path)
    if m:
        return m.group(1)
    m = re.search(r"/(\d+)\.html?$", path, re.IGNORECASE)
    return m.group(1) if m else ""


def dedupe_key(source: str = "", external_id: str = "", url: str = "") -> str:
    """Tier-1 key: source:external_id wins, else the canonical url."""
    if source and external_id:
        return f"{source}:{external_id}"
    canon = url_canonical(url)
    return f"url:{canon}" if canon else ""


_NUM = r"\d{1,3}(?:[.,]\d{3})+|\d+"
# "năm" is deliberately absent: "5 năm kinh nghiệm" is boilerplate, not a fingerprint.
_UNIT = r"%|vnd|usd|đ|ngày|tháng|người|phút|giờ|triệu|tỷ"
_NUM_UNIT = re.compile(rf"({_NUM})\s*({_UNIT})(?!\w)", re.IGNORECASE)
_ACRONYM = re.compile(r"\b[A-Za-z][A-Za-z0-9+#.]{2,}\b")
_UNIT_ALIAS = {"đ": "vnd"}
_UNIT_WORDS = {"vnd", "usd", "%"}


def jd_tokens(text: str) -> set[str]:
    """Tokens that survive an agency rewrite: (number, unit) pairs + acronym-ish
    terms (2+ capitals). Wording, sentence order and JD length are ignored — a
    repost is usually re-written from scratch and shares <5% of its 6-grams.

    shortcut: separators always read as thousands ("1,5 tháng" -> 15); fix only
    if a JD starts quoting fractional months/days.
    """
    text = unicodedata.normalize("NFKC", text or "")
    toks = set()
    for num, unit in _NUM_UNIT.findall(text):
        unit = unit.lower()
        n = num.replace(".", "").replace(",", "").lstrip("0") or "0"
        toks.add(f"{n}:{_UNIT_ALIAS.get(unit, unit)}")
    for w in _ACRONYM.findall(text):
        if sum(c.isupper() for c in w) >= 2 and w.lower() not in _UNIT_WORDS:
            toks.add(w.lower())
    return toks


def repost_candidates(text: str, stored, *, min_shared: int = 3, min_numeric: int = 2,
                      min_score: float = 0.35, max_tokens: int = 8) -> list[dict]:
    """Rank stored jobs sharing distinctive JD tokens with `text`. ADVISORY only.

    A repost can still be a different opening (an agency may widen the scope or
    raise the bar), so callers must flag, never auto-link. `stored` is an
    iterable of dicts with id/company/title/text; tokens present in >30% of
    stored JDs are boilerplate and dropped.

    `min_numeric` keeps stack acronyms (GraphQL, RESTful, AWS) from matching on
    their own: a real repost keeps the *numbers* (14 tháng, 170.000, 30 phút).
    """
    rows = list(stored)
    if not rows:
        return []
    toks = [jd_tokens(r.get("text", "")) for r in rows]
    df: dict[str, int] = {}
    for t in toks:
        for tok in t:
            df[tok] = df.get(tok, 0) + 1
    boilerplate = max(2, int(len(rows) * 0.3))
    mine = {t for t in jd_tokens(text) if df.get(t, 0) <= boilerplate}
    if not mine:
        return []
    out = []
    for r, t in zip(rows, toks):
        theirs = {x for x in t if df.get(x, 0) <= boilerplate}
        shared = mine & theirs
        if len(shared) < min_shared:
            continue
        if sum(1 for x in shared if ":" in x) < min_numeric:
            continue
        score = round(len(shared) / max(1, min(len(mine), len(theirs))), 2)
        if score < min_score:
            continue
        out.append({"id": r["id"], "company": r.get("company", ""),
                    "title": r.get("title", ""), "score": score,
                    # rarest first: the evidence a human actually reads
                    "shared_tokens": sorted(shared, key=lambda x: (df.get(x, 0), x))[:max_tokens]})
    out.sort(key=lambda d: (-d["score"], -len(d["shared_tokens"]), d["id"]))
    return out


def find_duplicates(conn, *, source="", external_id="", url="",
                    company="", title="", location=""):
    """Return {'exact': row|None, 'fuzzy': [rows]}.

    Tier-1 (exact) is safe to auto-block; tier-2 (fuzzy company+title+location)
    only flags so a human confirms (a repost can be a new opening).
    """
    key = dedupe_key(source, external_id or extract_external_id(url), url)
    canon = url_canonical(url)
    exact = conn.execute(
        "SELECT * FROM jobs WHERE (dedupe_key = ? AND dedupe_key <> '') "
        "OR (url_canonical = ? AND url_canonical <> '') LIMIT 1",
        (key, canon),
    ).fetchone()
    fuzzy = []
    slug, tnorm = company_slug(company), title_norm(title)
    if slug and tnorm:
        fuzzy = conn.execute(
            "SELECT * FROM jobs WHERE company_slug = ? AND title_norm = ? "
            "AND COALESCE(location, '') = ?",
            (slug, tnorm, location or ""),
        ).fetchall()
        if exact is not None:
            fuzzy = [r for r in fuzzy if r["id"] != exact["id"]]
    return {"exact": exact, "fuzzy": fuzzy}
