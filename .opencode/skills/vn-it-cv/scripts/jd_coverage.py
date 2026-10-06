#!/usr/bin/env python3
"""JD keyword coverage report: which JD-required skills your CV shows, omits, or
lists only in Skills. Advisory only — never blocks, never adds anything.

    python3 jd_coverage.py cv/foo-en.md jobs/foo.md
    python3 jd_coverage.py --job 2026-10-topcv-vexere-fullstack-developer-reactjs-nodejs

Sources (both optional):
  --jd <path>   parse a JD file for keywords (vocab = profile.md §3 skills + aliases)
  --job <id>    read the DB: cv path (cv_versions), JD (jobs/<id>.md) and the
                curated gap_skills_json from the score step

Output buckets:
  ADD       JD wants it, you have it confirmed, but the CV omits it → consider adding
  CONTEXT   it is in Skills but in no Experience bullet → put it in a role/Tech line
  UNCONF    in profile.md §3 but `confirmed: false` → do NOT list until evidenced
  GAP       JD wants it and you do not have it (DB gap_skills) → real gap, never fabricate
"""

import json
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import selfcheck_cv as sc  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
PROFILE = ROOT / "profile.md"
DB = ROOT / "jobcopilot.db"


def _profile_skills(profile_text: str):
    """[(skill_name, confirmed_bool)] from profile.md §3."""
    out = []
    m = re.search(r"##\s+3\.\s+Skills\s*\n(.*?)(?=\n##\s|\Z)", profile_text, re.S)
    if not m:
        return out
    for row in m.group(1).splitlines():
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) >= 7 and cells[0].startswith("s"):
            out.append((cells[1], cells[5].lower() == "true"))
    return out


def _section(text: str, name: str) -> str:
    m = re.search(rf"##\s+{name}\s*\n(.*?)(?=\n##\s|\Z)", text, re.S | re.I)
    return m.group(1) if m else ""


def _wanted(tokens, jd_stems) -> bool:
    return any(sc._match(t, jd_stems) for t in tokens)


def _in(tokens, stems) -> bool:
    return any(sc._match(t, stems) for t in tokens)


def _job_from_db(job_id: str):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cv = conn.execute(
        "SELECT path FROM cv_versions WHERE job_id=? AND is_current=1 ORDER BY id DESC LIMIT 1",
        (job_id,)).fetchone()
    job = conn.execute("SELECT gap_skills_json FROM jobs WHERE id=?", (job_id,)).fetchone()
    conn.close()
    gap = []
    if job and job["gap_skills_json"]:
        try:
            gap = json.loads(job["gap_skills_json"])
        except json.JSONDecodeError:
            gap = []
    return (cv["path"] if cv else None), gap


def report(cv_path: Path, jd_path: Path | None, gap=None):
    profile = PROFILE.read_text(encoding="utf-8")
    cv = cv_path.read_text(encoding="utf-8")
    jd_text = jd_path.read_text(encoding="utf-8").lower() if jd_path and jd_path.exists() else ""
    jd_stems = sc._entry_stems(jd_text)

    cv_skills_stems = sc._entry_stems(_section(cv, "Skills"))
    cv_exp_stems = sc._entry_stems(_section(cv, "Experience"))

    skills = _profile_skills(profile)
    confirmed_stems = set()
    for name, confirmed in skills:
        if confirmed:
            confirmed_stems |= sc._entry_stems(name)
    # a DB gap that is now a confirmed profile skill is stale — drop it
    gap = [g for g in (gap or []) if not _in(list(sc._skills_tokens(g)), confirmed_stems)]

    add, context, unconf, covered = [], [], [], []
    for name, confirmed in skills:
        tokens = list(sc._skills_tokens(name))
        if not tokens or not _wanted(tokens, jd_stems):
            continue
        if not confirmed:
            unconf.append(name)
            continue
        in_sk = _in(tokens, cv_skills_stems)
        in_ex = _in(tokens, cv_exp_stems)
        if in_ex:
            covered.append(name)
        elif in_sk:
            context.append(name)
        else:
            add.append(name)

    lines = [f"# JD coverage — {cv_path.name}",
             f"JD: {jd_path.name if jd_path and jd_path.exists() else '(none)'}", ""]
    if add:
        lines += ["## ADD — you have it, CV omits (consider adding)"] + [f"- {s}" for s in add] + [""]
    if context:
        lines += ["## CONTEXT — in Skills only, no Experience bullet"] + [f"- {s}" for s in context] + [""]
    if unconf:
        lines += ["## UNCONF — confirmed:false, do NOT list yet"] + [f"- {s}" for s in unconf] + [""]
    if gap:
        lines += ["## GAP — JD wants it, you do not have it (never fabricate)"] + [f"- {s}" for s in gap] + [""]
    if covered:
        lines += ["## Covered (in Experience)"] + [f"- {s}" for s in covered] + [""]
    if not (add or context or unconf or gap):
        lines += ["No JD-relevant gaps found (or no JD given).", ""]
    print("\n".join(lines))


def main(argv):
    job = jd = None
    pos = []
    i = 0
    while i < len(argv):
        if argv[i] == "--job":
            job = argv[i + 1]; i += 2
        elif argv[i] == "--jd":
            jd = argv[i + 1]; i += 2
        else:
            pos.append(argv[i]); i += 1

    gap = []
    if job:
        cv_path_str, gap = _job_from_db(job)
        if not cv_path_str:
            print(f"no current CV for job {job}", file=sys.stderr)
            return 2
        cv_path = ROOT / cv_path_str
        jd_path = Path(jd) if jd else ROOT / "jobs" / f"{job}.md"
    elif len(pos) >= 1:
        cv_path = Path(pos[0])
        jd_path = Path(pos[1]) if len(pos) > 1 else None
    else:
        print(__doc__)
        return 2
    report(cv_path, jd_path, gap)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
