#!/usr/bin/env python3
"""Fail if a *tracked* or *staged* file leaks real personal/business data.

Three layers, all over files git would ship:

  1. Path guard -- files under the personal-data dirs (`profile.md`, `sync/`,
                    `cv/`, `jobs/`, `offers/`, `prep/`, `jobcopilot.db*`,
                    `.leak-words.txt`) must never be committed. `gitignore` is
                    the first line of defence; this catches `git add -f`.
  2. Denylist   -- `.leak-words.txt` at repo root (gitignored), one real
                    employer/client/school/project name per line.
  3. Patterns   -- shapes only real data produces: data sizes, business
                    multipliers, email, phone, LinkedIn vanity URL.
Mark a line as intentional with a `leak-ok` comment on it (or the line above).

Modes:
    (default)   every tracked file
    --staged    the index (what the next commit would contain) -- for pre-commit
    --history   every commit ever made, denylist only (no `leak-ok` there).
                Manual: it only ever grows with the repo.

Usage: python3 scripts/leak_check.py [--staged|--history] [paths...]
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TEXT_EXT = {".md", ".py", ".sh", ".html", ".json", ".yml", ".yaml", ".txt"}

PATTERNS = [
    (r"\b\d[\d.,]*\s?(?:GB|TB)\b", "data size from a real system"),
    (r"\b\d[\d.,]*\s?[MK]?\+?\s*(?:orders|users|clients|customers|invoices|employees|devs|engineers)\b",
     "real business metric"),
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "email address"),
    (r"(?<!\d)0\d{9}(?!\d)", "phone number"),
    (r"linkedin\.com/in/(?!username|yourname|your-name|profile)[A-Za-z0-9-]{3,}", "personal LinkedIn URL"),
]

# --- path guard: the gitignored "bring your own data" areas -------------------
LOCAL_DIRS = ("sync/", "cv/", "jobs/", "offers/", "prep/")
LOCAL_FILES = ("profile.md", ".leak-words.txt")
# The *_example* files are the shipped templates; .gitkeep keeps the dir.
LOCAL_ALLOWED = {"sync/_example.md", "jobs/_example.md", "cv/_example-en.md",
                 "offers/_example.md", "prep/_example.md"}


def is_local(rel: str) -> bool:
    if rel.endswith("/.gitkeep") or rel in LOCAL_ALLOWED:
        return False
    return (rel.startswith(LOCAL_DIRS) or rel in LOCAL_FILES
            or rel.startswith("jobcopilot.db"))


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout


def denylist() -> list[str]:
    wl = REPO / ".leak-words.txt"
    if not wl.exists():
        return []
    return [w.strip() for w in wl.read_text(encoding="utf-8").splitlines()
            if w.strip() and not w.startswith("#")]


def paths(staged: bool) -> list[str]:
    if staged:
        return git("diff", "--cached", "--name-only", "--diff-filter=ACM").splitlines()
    return git("ls-files").splitlines()


def text_of(rel: str, staged: bool) -> str | None:
    try:
        if staged:
            blob = subprocess.run(["git", "show", f":{rel}"], cwd=REPO, capture_output=True)
            return blob.stdout.decode("utf-8")
        return (REPO / rel).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def scan(rel: str, text: str, words: list[str]) -> list[str]:
    problems = []
    lines = text.splitlines()
    for n, line in enumerate(lines, 1):
        if "leak-ok" in line or (n > 1 and "leak-ok" in lines[n - 2]):
            continue
        for w in words:
            if re.search(re.escape(w), line, re.IGNORECASE):
                problems.append(f"{rel}:{n}: denylisted term `{w}`")
        for pat, why in PATTERNS:
            if re.search(pat, line, re.IGNORECASE):
                problems.append(f"{rel}:{n}: {why} -> {line.strip()[:90]}")
    return problems


def history(words: list[str]) -> int:
    if not words:
        print("no .leak-words.txt -> nothing to scan in history (add your real names first)")
        return 0
    pat = "|".join(re.escape(w) for w in words)
    revs = git("rev-list", "--all").split()
    out = git("grep", "-I", "-i", "-n", "-E", pat, *revs)
    hits = [h for h in out.splitlines() if h]
    print(f"scanned {len(revs)} commit(s) for {len(words)} denylisted term(s)")
    if hits:
        uniq: dict[str, set[str]] = {}
        for h in hits:
            sha, rest = h.split(":", 1)
            uniq.setdefault(rest, set()).add(sha[:7])
        print(f"\nFAIL: {len(uniq)} historical line(s) contain a real name (rewrite history to remove):")
        for rest, shas in list(uniq.items())[:40]:
            print(f"  - {rest[:130]}  ({len(shas)} commit(s))")
        if len(uniq) > 40:
            print(f"  ... {len(uniq) - 40} more")
        return 1
    print("HISTORY CHECK OK")
    return 0


def main(argv: list[str]) -> int:
    staged = "--staged" in argv
    args = [a for a in argv if not a.startswith("--")]
    words = denylist()

    if "--history" in argv:
        return history(words)

    rels = args or paths(staged)
    problems = [f"{rel}: local-data path must never be committed (gitignore or a mistake)"
                for rel in rels if is_local(rel)]

    scanned = 0
    for rel in rels:
        if args or Path(rel).suffix in TEXT_EXT:
            text = text_of(rel, staged)
            if text is not None:
                scanned += 1
                problems += scan(rel, text, words)

    where = "staged" if staged else "tracked"
    print(f"scanned {scanned} {where} file(s), {len(words)} denylisted term(s)")
    if problems:
        print("\nFAIL:")
        for p in problems:
            print("  -", p)
        return 1
    print("LEAK CHECK OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
