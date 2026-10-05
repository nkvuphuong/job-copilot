"""One-time migration: jobs/*.md frontmatter -> DB, then strip frontmatter.

Idempotent: upsert by job id; only rewrites a file that still has frontmatter;
backs up originals to jobs/.backup/ (never overwrites an existing backup).
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import db
from identity import (company_slug, dedupe_key, extract_external_id, title_norm,
                      url_canonical)

SKIP = {"_example.md", ".gitkeep"}


def _unquote(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def _strip_comment(v: str) -> str:
    v = v.strip()
    if v[:1] in ('"', "'"):
        q = v[0]
        end = v.find(q, 1)
        return v[:end + 1] if end != -1 else v
    return v.split(" #", 1)[0].rstrip()


def _value(v: str):
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return [ _unquote(x) for x in inner.split(",") if x.strip() ] if inner else []
    if v[:1] in ('"', "'"):
        return _unquote(v)
    if v in ("true", "false"):
        return v == "true"
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    return v


def parse_frontmatter(text: str):
    if not text.startswith("---"):
        return {}, text
    _, raw, body = text.split("---", 2)
    data = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        data[k.strip()] = _value(_strip_comment(v))
    return data, body.lstrip("\n")


def _lang_of(stem: str) -> str:
    m = re.search(r"-(en|vi|vn)$", stem)
    return m.group(1) if m else ""


def _job_row(data: dict, fid: str) -> tuple[str, dict]:
    url = str(data.get("url", ""))
    source = str(data.get("source", ""))
    ext = extract_external_id(url)
    jid = str(data.get("id", "")).strip() or fid
    return jid, {
        "id": jid,
        "source": source,
        "external_id": ext,
        "url": url,
        "url_canonical": url_canonical(url),
        "dedupe_key": dedupe_key(source, ext, url),
        "company": data.get("company", ""),
        "company_slug": company_slug(str(data.get("company", ""))),
        "title": data.get("title", ""),
        "title_norm": title_norm(str(data.get("title", ""))),
        "location": data.get("location", ""),
        "remote": data.get("remote", ""),
        "seniority": data.get("seniority", ""),
        "salary_min": data.get("salary_min") or 0,
        "salary_max": data.get("salary_max") or 0,
        "currency": data.get("currency", ""),
        "skills_required_json": json.dumps(data.get("skills_required", []), ensure_ascii=False),
        "skills_nice_json": json.dumps(data.get("skills_nice", []), ensure_ascii=False),
        "lang_req_json": json.dumps(data.get("lang_req", []), ensure_ascii=False),
        "posted_date": str(data.get("posted_date", "")),
        "match_score": data.get("match_score") or 0,
        "score_rationale": data.get("score_rationale", ""),
        "gap_skills_json": json.dumps(data.get("gap_skills", []), ensure_ascii=False),
        "verdict": "keep",
        "status": data.get("status", "saved"),
        "referral": 1 if data.get("referral") else 0,
        "referral_contact": data.get("referral_contact", ""),
        "next_action": data.get("next_action", ""),
        "next_action_date": str(data.get("next_action_date", "")),
        "applied_at": str(data.get("applied_at", "")),
        "apply_method": data.get("apply_method", ""),
        "followup_at": str(data.get("followup_at", "")),
        "first_run_id": None,
        "notes": data.get("notes", ""),
    }


def _header(row: dict) -> str:
    return (f"# {row['title']} — {row['company']}\n\n"
            f"Company: {row['company']} · Source: {row['source']}\n"
            f"URL: {row['url']}\n\n")


def _prefix_match(job_ids, stem: str):
    slug = re.sub(r"-(en|vi|vn)$", "", stem)
    for jid in job_ids:
        if jid.endswith(slug) or jid.endswith("-" + slug):
            return jid
    return None


def run(conn, repo_root: Path, jobs_dir: Path, cv_dir: Path, *, strip: bool = True) -> dict:
    db.init_schema(conn)
    backup = jobs_dir / ".backup"
    job_ids, n_jobs, n_stripped, n_cv = [], 0, 0, 0

    for path in sorted(jobs_dir.glob("*.md")):
        if path.name in SKIP:
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue  # already migrated: never overwrite DB from a stripped file
        data, body = parse_frontmatter(text)
        jid, row = _job_row(data, path.stem)
        db.upsert_job(conn, row)
        n_jobs += 1
        if data.get("cv_version"):
            p = str(data["cv_version"])
            db.add_cv_version(conn, jid, _lang_of(Path(p).stem), p)
            n_cv += 1
        if strip:
            backup.mkdir(exist_ok=True)
            dest = backup / path.name
            if not dest.exists():
                shutil.copy2(path, dest)
            path.write_text(_header(row) + body, encoding="utf-8")
            n_stripped += 1

    job_ids = [r["id"] for r in conn.execute("SELECT id FROM jobs")]
    seen = {r["path"] for r in conn.execute("SELECT path FROM cv_versions")}
    for path in sorted(cv_dir.glob("*.md")):
        if path.name in SKIP:
            continue
        rel = f"cv/{path.name}"
        if rel in seen:
            continue
        jid = _prefix_match(job_ids, path.stem)
        if jid:
            db.add_cv_version(conn, jid, _lang_of(path.stem), rel)
            n_cv += 1

    return {"jobs": n_jobs, "stripped": n_stripped, "cv_versions": n_cv,
            "backup": str(backup)}
