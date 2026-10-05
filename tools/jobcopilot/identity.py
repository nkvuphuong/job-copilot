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
