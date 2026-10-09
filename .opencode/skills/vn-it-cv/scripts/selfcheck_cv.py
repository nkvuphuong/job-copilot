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
4. experience order: `## Experience` entries must be reverse-chronological
   (newest start date first) — catches a newer role appended below older ones.
5. per-role Tech line: every tech in a `**Tech:**` line must be backed by that
   role's own bullets, OR by another bullet of the SAME company in profile.md §4
   (company-scoped union), OR be a `confirmed: true` skill in profile.md §3.
   A tech backed ONLY by a global `confirmed` skill (not this company's evidence)
   is reported as a warning (warn-first) — surfaces cross-role leakage without
   blocking legitimate union lines.
6. header scope: the header (name/title/contact) must not leak template
   placeholders/comments (`[`, `]`, `<!--`, `TODO`).
7. coverage (profile -> CV, warn-only, whole-set runs only): evidence ids defined
   in profile.md §4/§5 that appear on NO CV and are not declared
   `<!-- omit: e0xx (reason) -->` are reported. This is the reverse of check #1 —
   it catches evidence silently dropped from every CV (e.g. an enriched bullet
   that never made it onto a CV).

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
    "large", "scale", "distributed", "practices", "core", "tech",
}
# tokens allowed even without a literal profile match (common resume vocabulary)
_ALLOW = {"agile", "microservices"}

# mechanical spelling variants (JS/JS, K8s/Kubernetes…) so a CV writing one form
# still matches a profile/confirmed skill written in another. Not personal data.
_ALIAS_GROUPS = (
    {"javascript", "js"},
    {"typescript", "ts"},
    {"kubernetes", "k8s"},
    {"postgresql", "postgres"},
    {"node.js", "nodejs", "node"},
    {"spring boot", "springboot"},
    {"react", "reactjs", "react.js"},
    {"angular", "angularjs"},
    {"elasticsearch", "elastic search"},
)
_ALIAS_MAP = {t: grp for grp in _ALIAS_GROUPS for t in grp}


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


_EXP_HEADING = re.compile(r"^###\s+(.*)$", re.M)
_EXP_START = re.compile(r"(\d{2})/(\d{4})\s*[–-]")


def _experience_order_problems(text: str):
    """Experience entries must run reverse-chronological (newest start date first).

    Catches the class of bug where a newer role is appended below older ones
    (e.g. a just-added company landing at the bottom of profile.md / the CV),
    which renders the timeline wrong.
    """
    problems = []
    m = re.search(r"##\s+Experience\s*\n(.*?)(?=\n##\s|\Z)", text, re.S)
    if not m:
        return problems
    dated = []
    for h in _EXP_HEADING.findall(m.group(1)):
        d = _EXP_START.search(h)
        if d:
            company = h.split("—")[0].split("·")[0].strip()
            dated.append((int(d.group(2)), int(d.group(1)), company))
    for (y0, m0, c0), (y1, m1, c1) in zip(dated, dated[1:]):
        if (y0, m0) < (y1, m1):
            problems.append(
                f"experience order: '{c0}' (start {m0:02d}/{y0}) is older than "
                f"'{c1}' (start {m1:02d}/{y1}) — expected newest first")
    return problems


def _confirmed_tokens(profile_text: str):
    """Token stems of every §3 Skills row marked `confirmed: true`."""
    toks = set()
    m = re.search(r"##\s+3\.\s+Skills\s*\n(.*?)(?=\n##\s|\Z)", profile_text, re.S)
    if not m:
        return toks
    for row in m.group(1).splitlines():
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) >= 7 and cells[0].startswith("s") and cells[5].lower() == "true":
            for w in re.findall(r"[a-z0-9+#.]+", cells[1].lower()):
                toks.update((w, _stem(w), _stem(w)[:6]))
    return toks


def _entry_stems(entry: str):
    stems = set()
    for w in re.findall(r"[a-z0-9+#.]+", entry.lower()):
        stems.update((w, _stem(w), _stem(w)[:6]))
    return stems


def _variants(w: str):
    return _ALIAS_MAP.get(w, (w,))


def _match(w: str, stems) -> bool:
    for v in _variants(w):
        if v in _ALLOW or v in stems or _stem(v) in stems or _prefixes(_stem(v)) in stems:
            return True
        parts = [p for p in re.split(r"[-/]", v) if p]
        if parts and all(p in stems or _stem(p) in stems or _prefixes(_stem(p)) in stems for p in parts):
            return True
    return False


def _company_key(heading: str) -> str:
    """First significant token of a company heading, for CV↔profile matching."""
    name = heading.split("—")[0]
    name = re.sub(r"[^a-zA-Z0-9 .]", " ", name).lower()
    toks = [t for t in name.split() if t]
    return toks[0] if toks else ""


def _profile_company_stems(profile_text: str):
    """Map company-key -> stems of every §4 bullet of that company (union).

    Lets a CV role's `**Tech:**` line be backed by any bullet of the SAME company
    (the role's true stack is the union across its projects), not only the subset
    of bullets displayed in that one CV."""
    out = {}
    m = re.search(r"##\s+\d+\.\s+Experiences\s*\n(.*?)(?=\n##\s|\Z)", profile_text, re.S)
    if not m:
        return out
    for blk in re.split(r"\n(?=###\s)", m.group(1)):
        h = re.match(r"###\s+(.*)", blk)
        if not h:
            continue
        key = _company_key(h.group(1))
        if key:
            out.setdefault(key, set()).update(_entry_stems(blk))
    return out


def _tech_line_problems(text: str, profile_text: str):
    """Each `**Tech:**` line must be backed by (a) that role's own CV bullets,
    (b) the SAME company's profile evidence (union across its bullets), or
    (c) a `confirmed: true` skill. Backing by (c) alone is warn-only."""
    problems = []
    warnings = []
    m = re.search(r"##\s+Experience\s*\n(.*?)(?=\n##\s|\Z)", text, re.S)
    if not m:
        return problems, warnings
    confirmed = _confirmed_tokens(profile_text)
    company_stems = _profile_company_stems(profile_text)
    for entry in re.split(r"\n(?=###\s)", m.group(1)):
        tech = re.search(r"\*\*Tech:\*\*\s*(.+)", entry)
        if not tech:
            continue
        h = re.match(r"###\s+(.*)", entry)
        cstems = company_stems.get(_company_key(h.group(1)), set()) if h else set()
        entry_stems = _entry_stems(entry.replace(tech.group(0), ""))
        for w in sorted(set(_skills_tokens(tech.group(1)))):
            role_ok = _match(w, entry_stems)
            comp_ok = _match(w, cstems)
            conf_ok = _match(w, confirmed)
            if role_ok or comp_ok:
                continue
            if conf_ok:
                warnings.append(
                    f"tech '{w}' in Tech line only globally confirmed — not in this company's evidence")
            else:
                problems.append(f"tech '{w}' in Tech line not backed by this role/company/confirmed")
    return problems, warnings


def _header_problems(text: str):
    """Header (name/title/contact) must not leak template placeholders/comments."""
    m = re.search(r"\A(.*?)(?=\n##\s)", text, re.S)
    header = m.group(1) if m else text
    return [f"header still contains placeholder/comment {bad!r}"
            for bad in ("[", "]", "<!--", "TODO") if bad in header]


def check(cv: Path, profile_text: str, strict_summary: bool = False):
    problems = []
    warnings = []
    text = cv.read_text(encoding="utf-8")

    # 1. evidence ids (support multi-id comments like `<!-- e010,e025 -->`)
    used = set()
    for blk in re.findall(r"<!--(.*?)-->", text, re.S):
        if re.match(r"\s*omit:", blk):
            continue
        used |= set(re.findall(r"\be\d{3}\b", blk))
    known = set(re.findall(r"\be\d{3}\b", profile_text))
    for e in sorted(used - known):
        problems.append(f"evidence {e} not in profile.md")

    # 2. claim scope in Skills (stem-match against the *evidence* scope)
    low, stems = _profile_vocab(profile_text)
    m = re.search(r"##\s+Skills\s*\n(.*?)(?=\n##\s|\Z)", text, re.S)
    if m:
        for w in sorted(set(_skills_tokens(m.group(1)))):
            if _match(w, stems):
                continue
            problems.append(f"skill '{w}' not backed by profile.md (evidence/confirmed)")

    # 3. summary (warn-only by default)
    for w in _summary_warnings(text, profile_text):
        (problems if strict_summary else warnings).append(w)

    # 4. experience order: newest start date first
    problems.extend(_experience_order_problems(text))

    # 5. per-role `**Tech:**` lines backed by role/company evidence (confirmed-only -> warn)
    tp, tw = _tech_line_problems(text, profile_text)
    problems.extend(tp)
    warnings.extend(tw)

    # 6. header must not leak template placeholders / comments
    problems.extend(_header_problems(text))
    return problems, warnings


def main(argv):
    strict = "--strict-summary" in argv
    argv = [a for a in argv if a != "--strict-summary"]
    profile_text = PROFILE.read_text(encoding="utf-8")
    # default: every real tailored CV. Skip `_*` (templates/examples shipped in the repo).
    run_all = not argv
    targets = [Path(a) for a in argv] or sorted(
        p for p in (ROOT / "cv").glob("*.md") if not p.name.startswith("_")
    )
    failed = False
    all_used, all_omitted = set(), set()
    for cv in targets:
        text = cv.read_text(encoding="utf-8")
        for blk in re.findall(r"<!--(.*?)-->", text, re.S):
            if re.match(r"\s*omit:", blk):
                all_omitted |= set(re.findall(r"\be\d{3}\b", blk))
            else:
                all_used |= set(re.findall(r"\be\d{3}\b", blk))
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

    # 7. coverage (profile -> CV): profile evidence on NO CV and not declared omitted.
    #    Only meaningful when the whole CV set is checked (a single CV is a subset).
    if run_all:
        # global omission ledger (coverage is a whole-portfolio property, so
        # deliberate drops are declared once, not per CV)
        ledger = ROOT / "cv" / "_omitted.md"
        if ledger.exists():
            all_omitted |= set(re.findall(r"\be\d{3}\b", ledger.read_text(encoding="utf-8")))
        known = set(re.findall(r"\be\d{3}\b", profile_text))
        orphans = sorted(known - all_used - all_omitted)
        if orphans:
            print(f"warn coverage: {len(orphans)} evidence in profile.md on no CV "
                  f"(add a bullet, or declare in cv/_omitted.md): {', '.join(orphans)}")
        else:
            print("ok   coverage: every profile evidence is on a CV or declared omitted")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
