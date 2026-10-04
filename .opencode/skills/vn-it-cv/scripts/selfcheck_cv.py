#!/usr/bin/env python3
"""Honesty self-check for tailored CVs against profile.md (source of truth).

Checks (all must pass):

1. evidence_id: every `<!-- e0xx -->` in a CV must exist as `[e0xx]` in profile.md.
2. claim scope: every tech/skill token in the CV's `## Skills` section must be
   backed by an *evidence-bearing* part of profile.md — i.e. it must appear in a
   §4 Experiences / §5 Projects bullet, OR be the name of a skill whose §3 row has
   `confirmed: true`. Tokens only listed in the §3 table with `confirmed: false`
   (list-only / exploring) do NOT count. This closes the "claim creep" hole where
   PostgreSQL/Golang/Kafka leaked into CVs while the profile only listed them.
3. summary scope (warn-only by default): numbers/metrics in the CV `## Summary`
   should trace to profile.md. Reported as warnings unless --strict-summary.

Usage:
    python3 selfcheck_cv.py                 # all cv/*-en.md + cv/*-vn.md
    python3 selfcheck_cv.py cv/foo-en.md
    python3 selfcheck_cv.py --strict-summary
Exit code 1 if any check fails (summary warnings do not fail unless --strict-summary).
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


def _evidence_scope(profile_text: str) -> str:
    """The parts of profile.md that count as *backing* for claims.

    = every bullet under §4 Experiences / §5 Projects (lines starting with `- `,
    which carry the `[e0xx]` evidence), PLUS the name column of every §3 Skills
    row whose `confirmed` cell is `true`. Deliberately EXCLUDES:
      - non-bullet prose (headings, company context, positioning lines),
      - skill rows marked `confirmed: false` (list-only / exploring).
    """
    chunks = []

    # §3 Skills rows with confirmed: true -> take the skill token(s)
    m = re.search(r"##\s+3\.\s+Skills\s*\n(.*?)(?=\n##\s|\Z)", profile_text, re.S)
    if m:
        for row in m.group(1).splitlines():
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            if len(cells) >= 7 and cells[0].startswith("s"):
                skill, confirmed = cells[1], cells[5].lower()
                if confirmed == "true":
                    chunks.append(skill)

    # §4 + §5 bullets (evidence-bearing)
    for sec in ("Experiences", "Projects"):
        m = re.search(rf"##\s+\d+\.\s+{sec}\s*\n(.*?)(?=\n##\s|\Z)", profile_text, re.S)
        if m:
            for line in m.group(1).splitlines():
                if line.strip().startswith("- "):
                    chunks.append(line)

    return "\n".join(chunks)


def _profile_vocab(profile_text: str):
    """Lowercased evidence-scoped text + word stems, so 'optimization'/'queries'/
    '3M'/'orders' match 'Optimized SQL queries' / '3M+ orders'."""
    low = _evidence_scope(profile_text).lower()
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


def _summary_warnings(cv_text: str, profile_text: str):
    """Warn on distinctive metrics in the CV Summary that do not trace to profile.

    Only multi-char numeric tokens ($, %, k/M numbers, ratios) are checked, to
    keep false positives low. This is warn-only unless --strict-summary.
    """
    warns = []
    m = re.search(r"##\s+Summary\s*\n(.*?)(?=\n##\s|\Z)", cv_text, re.S)
    if not m:
        return warns
    summary = m.group(1)
    low = profile_text.lower()
    # numbers with a metric signal: $10,000  20%  3M  60-98%  90%
    for tok in sorted(set(re.findall(r"\$?\d[\d,\.]*\s*(?:%|k\+?|m\+?)|[+-]?\d+%", summary, re.I))):
        t = tok.strip()
        bare = re.sub(r"[%$,+\s]", "", t).lower()
        if not bare:
            continue
        if bare in low or t.lower() in low:
            continue
        warns.append(f"summary metric '{t}' not found in profile.md")
    return warns


def check(cv: Path, profile_text: str, strict_summary: bool = False):
    problems = []
    warnings = []
    text = cv.read_text(encoding="utf-8")

    # 1. evidence ids
    used = set(re.findall(r"<!--\s*(e\d{3})\s*-->", text))
    known = set(re.findall(r"\[(e\d{3})\]", profile_text))
    for e in sorted(used - known):
        problems.append(f"evidence {e} not in profile.md")

    # 2. claim scope in Skills (stem-match against the *evidence* scope)
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
            problems.append(f"skill '{w}' not backed by profile.md (evidence/confirmed)")

    # 3. summary (warn-only by default)
    for w in _summary_warnings(text, profile_text):
        (problems if strict_summary else warnings).append(w)
    return problems, warnings


def main(argv):
    strict = "--strict-summary" in argv
    argv = [a for a in argv if a != "--strict-summary"]
    profile_text = PROFILE.read_text(encoding="utf-8")
    # default: every real tailored CV. Skip `_*` (templates/examples shipped in the repo).
    targets = [Path(a) for a in argv] or sorted(
        p for p in (ROOT / "cv").glob("*.md") if not p.name.startswith("_")
    )
    failed = False
    for cv in targets:
        problems, warnings = check(cv, profile_text, strict)
        for w in warnings:
            print(f"warn {cv.name}: {w}")
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
