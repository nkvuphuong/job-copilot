#!/usr/bin/env python3
"""Check `sync/<platform>.md` profile packs: field char limits + evidence ids.

Pack format: a field is a `## Name  <!-- limit: N -->` heading followed by one
fenced block (```). Blocks under a heading without `<!-- limit -->` are not
length-checked. Every `[eNNN]` inside a checked block must exist in profile.md.

Usage:
    python3 pack_check.py                    # check every sync/*.md
    python3 pack_check.py sync/linkedin.md   # check one pack
Exit 1 on any violation.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
HEAD = re.compile(r"^##\s+(?P<name>.+?)\s*(?:<!--\s*limit:\s*(?P<limit>\d+)\s*-->)?\s*$")
EVID = re.compile(r"\[(e\d{3})\]")


def parse_pack(text: str) -> list[dict]:
    """Yield {name, limit, body} for each field that has a fenced block."""
    fields, current, buf, in_fence = [], None, [], False
    for line in text.splitlines():
        if line.startswith("```"):
            if in_fence:
                fields.append({**current, "body": "\n".join(buf)})
                buf = []
                in_fence = False
            else:
                in_fence = True
            continue
        if in_fence:
            buf.append(line)
            continue
        m = HEAD.match(line)
        if m:
            limit = m.group("limit")
            current = {"name": m.group("name"), "limit": int(limit) if limit else None}
    return fields


def check(pack: Path, profile_ids: set[str]) -> list[str]:
    problems = []
    for f in parse_pack(pack.read_text(encoding="utf-8")):
        body = f["body"]
        if f["limit"] is not None and len(body) > f["limit"]:
            problems.append(f"{pack.name} · {f['name']}: {len(body)}/{f['limit']} chars")
        for ev in EVID.findall(body):
            if ev not in profile_ids:
                problems.append(f"{pack.name} · {f['name']}: unknown evidence [{ev}]")
    return problems


def main(argv: list[str]) -> int:
    profile = REPO / "profile.md"
    if not profile.exists():
        print("error: profile.md not found", file=sys.stderr)
        return 1
    profile_ids = set(re.findall(r"e\d{3}", profile.read_text(encoding="utf-8")))

    packs = [Path(a) for a in argv] or [
        p for p in sorted((REPO / "sync").glob("*.md"))
        if not p.name.endswith(".before.md") and not p.name.startswith("_")
    ]  # *.before.md = snapshot for restore; _*.md = the committed example. Neither is a pack.
    if not packs:
        print("error: no packs found in sync/", file=sys.stderr)
        return 1

    problems, total = [], 0
    for pack in packs:
        fields = parse_pack(pack.read_text(encoding="utf-8"))
        for f in fields:
            total += 1
            limit = f" / {f['limit']}" if f["limit"] else ""
            print(f"{pack.name:16} {f['name'][:28]:28} {len(f['body']):>5}{limit}")
        problems += check(pack, profile_ids)

    print(f"\n{total} fields, {len(packs)} pack(s), profile ids: {len(profile_ids)}")
    if problems:
        print("\nFAIL:")
        for p in problems:
            print("  -", p)
        return 1
    print("PACK CHECK OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
