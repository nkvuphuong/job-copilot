#!/usr/bin/env python3
"""Simulate an ATS text-extraction pass over a tailored CV.

Renders the CV Markdown exactly like the PDF export does, reduces the HTML to
plain text (what a parser sees after copy/paste), and checks the fields an ATS
keys on. Stdlib only — no pdftotext / pdfminer dependency.

    python3 ats_check.py                 # all cv/*.md except templates (_*)
    python3 ats_check.py cv/foo-en.md

Gating checks (exit 1 on failure):
  1. required sections present and in order (Summary < Skills < Experience < Education)
  2. email, VN phone and at least one profile URL (github/linkedin)
  3. every `### ...` Experience heading carries a parseable MM/YYYY start date
  4. no placeholder/comment leak in the header

Warn-only (best-effort, never fails):
  5. if a sibling .pdf exists, it is a real PDF with an embedded font and not
     older than the .md (a stale or rasterized export)
  6. glued-token heuristic on the extracted text (page-break artefacts)
"""

import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_cv  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]

_SECTION_ALIASES = {
    "summary": ("summary", "mục tiêu", "objective"),
    "skills": ("skills", "kỹ năng"),
    "experience": ("experience", "kinh nghiệm"),
    "education": ("education", "học vấn"),
}

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(r"(?:\+?84|0)\d[\d .\-]{7,}\d")
_URL = re.compile(r"(?:https?://|github\.com/|linkedin\.com/in/)")
_GLUE = re.compile(r"[a-z]\.[A-Z0-9]")


def _to_text(html_str: str) -> str:
    s = re.sub(r"<br\s*/?>", "\n", html_str)
    s = re.sub(r"</(?:p|li|h1|h2|h3|div|section)>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"[ \t]+", " ", s)


def _section_order_problems(md: str):
    heads = [h.strip().lower() for h in re.findall(r"^##\s+(.*)$", md, re.M)]
    found = {}
    for key, aliases in _SECTION_ALIASES.items():
        for i, h in enumerate(heads):
            if any(a in h for a in aliases):
                found[key] = i
                break
    problems = [f"missing section: {k}" for k in _SECTION_ALIASES if k not in found]
    order = ["summary", "skills", "experience", "education"]
    present = [k for k in order if k in found]
    for a, b in zip(present, present[1:]):
        if found[a] > found[b]:
            problems.append(f"section order: '{a}' should come before '{b}'")
    return problems


def _experience_date_problems(md: str):
    m = re.search(r"##\s+(?:Experience|Kinh nghiệm làm việc)\s*\n(.*?)(?=\n##\s|\Z)", md, re.S | re.I)
    if not m:
        return ["no Experience section found"]
    heads = re.findall(r"^###\s+(.*)$", m.group(1), re.M)
    if not heads:
        return ["Experience section has no entries"]
    return [f"Experience heading has no MM/YYYY date: {h.strip()}"
            for h in heads if not re.search(r"\d{2}/\d{4}", h)]


def _header_problems(md: str):
    m = re.search(r"\A(.*?)(?=\n##\s)", md, re.S)
    header = m.group(1) if m else md
    return [f"header still contains {bad!r}"
            for bad in ("[", "]", "<!--", "TODO") if bad in header]


def check(cv: Path):
    md = cv.read_text(encoding="utf-8")
    text = _to_text(render_cv.render(cv))
    problems = _section_order_problems(md) + _experience_date_problems(md) + _header_problems(md)
    if not _EMAIL.search(text):
        problems.append("no email found in extracted text")
    if not _PHONE.search(text):
        problems.append("no VN phone found in extracted text")
    if not _URL.search(text):
        problems.append("no profile URL (github/linkedin) found in extracted text")

    warnings = []
    pdf = cv.with_suffix(".pdf")
    if pdf.exists():
        if pdf.stat().st_mtime < cv.stat().st_mtime:
            warnings.append("PDF is older than the .md — re-export before sending")
        data = pdf.read_bytes()
        if data[:5] != b"%PDF-" or b"/Font" not in data:
            warnings.append("PDF has no embedded text layer (rasterized?) — check the export")
    glued = sorted(set(_GLUE.findall(text)))
    if glued:
        warnings.append(f"possible glued tokens (page-break artefact?): {', '.join(glued)}")
    return problems, warnings


def main(argv):
    targets = [Path(a) for a in argv] or sorted(
        p for p in (ROOT / "cv").glob("*.md") if not p.name.startswith("_")
    )
    failed = False
    for cv in targets:
        problems, warnings = check(cv)
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
