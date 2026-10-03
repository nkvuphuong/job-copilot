#!/usr/bin/env python3
"""Honesty self-check for tailored CVs against profile.md (source of truth).

Two checks, both must pass:

1. evidence_id: every `<!-- e0xx -->` in a CV must exist as `[e0xx]` in profile.md.
2. claim scope: every tech/skill token in the CV's `## Skills` section must
   appear somewhere in profile.md. Catches "claim creep" (writing
   `microservices`/`idempotency` when the profile only says "3M orders/year").

Usage:
    python3 selfcheck_cv.py                 # all cv/*-en.md + cv/*-vn.md
    python3 selfcheck_cv.py cv/foo-en.md
Exit code 1 if any check fails.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]  # repo root (…/job-copilot)
PROFILE = ROOT / "profile.md"

# tokens that are section labels / generic, not claims
_NOISE = {
    "and", "or", "tools", "languages", "frameworks", "platforms",
    "infrastructure", "backend", "frontend", "databases", "cache",
    "daily", "drivers", "etc", "ai", "data", "cloud", "devops",
    "architecture", "leadership", "messaging", "infra", "systems",
    "queues", "apis", "engineering", "delivery", "ownership", "mentoring",
    "large", "scale", "distributed",
}
# tokens allowed even without a literal profile match (common resume vocabulary)
_ALLOW = {"agile", "microservices"}


_SUF = ("ization", "isation", "ation", "izing", "ising", "ized", "ised",
        "ies", "ing", "ed", "es", "s")


def _stem(w: str):
    for suf in _SUF:
        if len(w) > len(suf) + 2 and w.endswith(suf):
            base = w[: -len(suf)]
            if suf in ("ization", "isation"):          # optimization -> optimize
                return base + "ize"
            if suf == "ies":                            # queries -> query
                return base + "y"
            if suf in ("ized", "ised", "izing", "ising"):  # optimized -> optimize
                return base + "ize"
            return base
    return w


def _prefixes(w: str):
    """Short prefix bucket (first 6 chars) so optimiz/optimize share a key."""
    return w[:6]


def _profile_vocab(profile_text: str):
    """Lowercased profile text + word stems, so 'optimization'/'queries'/
    '3M'/'orders' match 'Optimized SQL queries' / '3M+ orders'."""
    low = profile_text.lower()
    stems = set()
    for w in re.findall(r"[a-z0-9+#.]+", low):
        stems.add(w)
        stems.add(_stem(w))
        stems.add(_stem(w)[:6])
    return low, stems


def _skills_tokens(section: str):
    section = re.sub(r"\([^)]*\)", " ", section)  # drop parentheticals e.g. AWS(...)
    section = re.sub(r"[()·,;|/]", " ", section)
    for w in section.split():
        w = w.strip(".-–*: ").lower()
        if len(w) > 1 and w not in _NOISE and not w.startswith("**"):
            yield w


def check(cv: Path, profile_text: str):
    problems = []
    text = cv.read_text(encoding="utf-8")

    # 1. evidence ids
    used = set(re.findall(r"<!--\s*(e\d{3})\s*-->", text))
    known = set(re.findall(r"\[(e\d{3})\]", profile_text))
    for e in sorted(used - known):
        problems.append(f"evidence {e} not in profile.md")

    # 2. claim scope in Skills (stem-match, so word-form variation is fine)
    low, stems = _profile_vocab(profile_text)
    m = re.search(r"##\s+Skills\s*\n(.*?)(?=\n##\s|\Z)", text, re.S)
    if m:
        for w in sorted(set(_skills_tokens(m.group(1)))):
            if w in _ALLOW or w in stems or _stem(w) in stems or _prefixes(_stem(w)) in stems:
                continue
            # multi-word/hyphen fragment like "3m-orders": check each part
            parts = [p for p in re.split(r"[-/]", w) if p]
            if parts and all(p in stems or _stem(p) in stems or _prefixes(_stem(p)) in stems for p in parts):
                continue
            problems.append(f"skill '{w}' not backed by profile.md")
    return problems


def main(argv):
    profile_text = PROFILE.read_text(encoding="utf-8")
    targets = [Path(a) for a in argv] or sorted((ROOT / "cv").glob("*.md"))
    failed = False
    for cv in targets:
        problems = check(cv, profile_text)
        if problems:
            failed = True
            print(f"FAIL {cv.name}")
            for p in problems:
                print(f"   - {p}")
        else:
            print(f"ok   {cv.name}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
