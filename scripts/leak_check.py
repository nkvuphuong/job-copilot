#!/usr/bin/env python3
"""Fail if a *tracked* file leaks real personal/business data.

Rules (all files listed by `git ls-files`, so gitignored local data is exempt):
  1. Denylist  -- `.leak-words.txt` at repo root (gitignored), one term per line.
                  Put real employer / client / school / project names there, never in git.
  2. Patterns  -- shapes that only real profile data produces: data sizes, business
                  multipliers, big counts next to a business noun, email, phone,
                  LinkedIn vanity URL.
Mark a line as intentional with a `leak-ok` comment on it (or the line above).

Usage: python3 scripts/leak_check.py [paths...]
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TEXT_EXT = {".md", ".py", ".sh", ".html", ".json", ".yml", ".yaml", ".txt"}
SKIP = {".opencode/skills/profile-sync/references/writing-style.md"}  # placeholder examples only

PATTERNS = [
    (r"\b\d[\d.,]*\s?(?:GB|TB)\b", "data size from a real system"),
    (r"\b\d[\d.,]*\s?[MK]?\+?\s*(?:orders|users|clients|customers|invoices|employees|devs|engineers)\b",
     "real business metric"),
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "email address"),
    (r"(?<!\d)0\d{9}(?!\d)", "phone number"),
    (r"linkedin\.com/in/(?!username|yourname|your-name|profile)[A-Za-z0-9-]{3,}", "personal LinkedIn URL"),
]


def tracked() -> list[Path]:
    out = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True).stdout
    paths = []
    for rel in out.splitlines():
        if rel in SKIP:
            continue
        p = REPO / rel
        if p.suffix in TEXT_EXT and p.is_file():
            paths.append(p)
    return paths


def main(argv: list[str]) -> int:
    files = [Path(a) for a in argv] or tracked()
    words: list[str] = []
    wl = REPO / ".leak-words.txt"
    if wl.exists():
        words = [w.strip() for w in wl.read_text(encoding="utf-8").splitlines() if w.strip() and not w.startswith("#")]

    problems = []
    for f in files:
        try:
            lines = f.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for n, line in enumerate(lines, 1):
            if "leak-ok" in line or (n > 1 and "leak-ok" in lines[n - 2]):
                continue
            for w in words:
                if re.search(re.escape(w), line, re.IGNORECASE):
                    problems.append(f"{f.relative_to(REPO)}:{n}: denylisted term `{w}`")
            for pat, why in PATTERNS:
                if re.search(pat, line, re.IGNORECASE):
                    problems.append(f"{f.relative_to(REPO)}:{n}: {why} -> {line.strip()[:90]}")

    print(f"scanned {len(files)} tracked file(s), {len(words)} denylisted term(s)")
    if problems:
        print("\nFAIL:")
        for p in problems:
            print("  -", p)
        return 1
    print("LEAK CHECK OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
