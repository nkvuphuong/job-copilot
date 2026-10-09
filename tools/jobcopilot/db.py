"""SQLite store. Single write path for state (CLI + server both call this). Pure: no HTTP."""
from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = REPO_ROOT / "jobcopilot.db"
SCHEMA_VERSION = 2

STATUSES = ("saved", "applied", "screen", "tech", "onsite",
            "offer", "rejected", "ghosted", "closed")

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  started_at TEXT NOT NULL,
  source TEXT,
  params_json TEXT,
  status TEXT NOT NULL DEFAULT 'running',
  counts_json TEXT
);
CREATE TABLE IF NOT EXISTS jobs (
  id TEXT PRIMARY KEY,
  source TEXT, external_id TEXT, url TEXT, url_canonical TEXT, dedupe_key TEXT,
  company TEXT, company_slug TEXT, title TEXT, title_norm TEXT,
  location TEXT, remote TEXT, seniority TEXT,
  salary_min INTEGER, salary_max INTEGER, currency TEXT,
  skills_required_json TEXT, skills_nice_json TEXT, lang_req_json TEXT,
  posted_date TEXT,
  match_score INTEGER, score_rationale TEXT, gap_skills_json TEXT,
  verdict TEXT, verdict_reason TEXT, duplicate_of TEXT,
  status TEXT NOT NULL DEFAULT 'saved',
  applied_at TEXT, apply_method TEXT, followup_at TEXT,
  next_action TEXT, next_action_date TEXT,
  referral INTEGER DEFAULT 0, referral_contact TEXT,
  first_run_id INTEGER REFERENCES runs(id),
  notes TEXT, created_at TEXT, updated_at TEXT
);
CREATE TABLE IF NOT EXISTS job_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id TEXT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  at TEXT NOT NULL, type TEXT, from_status TEXT, to_status TEXT, note TEXT
);
CREATE TABLE IF NOT EXISTS run_items (
  run_id INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
  job_id TEXT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  disposition TEXT,
  PRIMARY KEY (run_id, job_id)
);
CREATE TABLE IF NOT EXISTS cv_versions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id TEXT REFERENCES jobs(id) ON DELETE CASCADE,
  lang TEXT, path TEXT, created_at TEXT, hash TEXT, profile_ver TEXT,
  is_current INTEGER DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_jobs_dedupe ON jobs(dedupe_key);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_events_job ON job_events(job_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_cv_unique ON cv_versions(job_id, path);
CREATE TABLE IF NOT EXISTS prep (
  job_id TEXT PRIMARY KEY REFERENCES jobs(id) ON DELETE CASCADE,
  path TEXT, prep_status TEXT NOT NULL DEFAULT 'draft',
  rounds_json TEXT, format TEXT, interviewers_json TEXT, sources_json TEXT,
  updated_at TEXT
);
CREATE TABLE IF NOT EXISTS prep_rounds (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id TEXT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  at TEXT, round_type TEXT, notes TEXT, went_well TEXT, to_fix TEXT
);
CREATE INDEX IF NOT EXISTS idx_prep_rounds_job ON prep_rounds(job_id);
"""

PREP_STATUSES = ("draft", "ready", "done")


def connect(path=DEFAULT_DB) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    _migrate(conn)
    conn.commit()


def _migrate(conn: sqlite3.Connection) -> None:
    """Add columns introduced after the first schema (idempotent)."""
    cols = {r["name"] for r in conn.execute("PRAGMA table_info(cv_versions)")}
    if "profile_ver" not in cols:
        conn.execute("ALTER TABLE cv_versions ADD COLUMN profile_ver TEXT")


def profile_ver(profile_text: str) -> str:
    """Hash of the *projection-relevant* parts of profile.md — the sections CVs
    are built from: §1b Positioning, §3 Skills, §4 Experiences, §5 Projects.
    Edits to unrelated prose (§0 notes, §2 wording) do NOT change this hash, so
    CVs are only flagged stale when the material they project from actually moved."""
    import hashlib
    import re
    parts = []
    for head in ("Positioning", "Skills", "Experiences", "Projects"):
        m = re.search(rf"##\s+\d+b?\.\s+{head}[^\n]*\n(.*?)(?=\n##\s|\Z)", profile_text, re.S)
        if m:
            parts.append(m.group(1))
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()[:12]


def stale_cvs(conn: sqlite3.Connection, current_ver: str) -> list[dict]:
    """CVs of still-active jobs whose stored `profile_ver` differs from now.
    Archived/rejected jobs are ignored (their CVs are not maintained)."""
    rows = conn.execute(
        "SELECT cv.job_id, cv.path, cv.profile_ver, cv.hash, j.company, j.title, j.status "
        "FROM cv_versions cv JOIN jobs j ON j.id = cv.job_id "
        "WHERE j.status NOT IN ('closed', 'rejected', 'ghosted') "
        "AND COALESCE(cv.profile_ver, '') <> ? "
        "ORDER BY cv.job_id", (current_ver,)).fetchall()
    return [dict(r) for r in rows]


def upsert_job(conn: sqlite3.Connection, fields: dict) -> str:
    """Insert or update a job by id. Caller supplies identity-normalized fields."""
    now = date.today().isoformat()
    fields = dict(fields)
    fields.setdefault("created_at", now)
    fields["updated_at"] = now
    cols = list(fields)
    placeholders = ", ".join("?" for _ in cols)
    updates = ", ".join(f"{c}=excluded.{c}" for c in cols if c != "id")
    sql = (f"INSERT INTO jobs ({', '.join(cols)}) VALUES ({placeholders}) "
           f"ON CONFLICT(id) DO UPDATE SET {updates}")
    conn.execute(sql, [fields[c] for c in cols])
    conn.commit()
    return fields["id"]


def get_job(conn: sqlite3.Connection, job_id: str):
    return conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()


def delete_job(conn: sqlite3.Connection, job_id: str) -> bool:
    """Delete a job row; children (job_events / run_items / cv_versions / prep /
    prep_rounds) go with it via ON DELETE CASCADE. Returns False if not found.

    Content files (`jobs/*.md`, `prep/*.md`) are NOT touched here — the caller
    (cli `rm --files`) removes them explicitly. DB state only."""
    row = conn.execute("SELECT id FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if row is None:
        return False
    conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    return True


def set_status(conn, job_id: str, to: str, *, at: str | None = None,
               kind: str = "status", note: str = "", **extra) -> None:
    if to not in STATUSES:
        raise ValueError(f"unknown status: {to}")
    row = conn.execute("SELECT status FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if row is None:
        raise KeyError(job_id)
    at = at or date.today().isoformat()
    sets = ["status = ?", "updated_at = ?"] + [f"{k} = ?" for k in extra]
    conn.execute(f"UPDATE jobs SET {', '.join(sets)} WHERE id = ?",
                 [to, at, *extra.values(), job_id])
    conn.execute(
        "INSERT INTO job_events (job_id, at, type, from_status, to_status, note) "
        "VALUES (?,?,?,?,?,?)",
        (job_id, at, kind, row["status"], to, note),
    )
    conn.commit()


def start_run(conn, source: str, params_json: str = "{}", *, at: str | None = None) -> int:
    at = at or date.today().isoformat()
    cur = conn.execute(
        "INSERT INTO runs (started_at, source, params_json, status) VALUES (?,?,?, 'running')",
        (at, source, params_json),
    )
    conn.commit()
    return cur.lastrowid


def finish_run(conn, run_id: int, counts_json: str = "{}", status: str = "done") -> None:
    conn.execute("UPDATE runs SET status = ?, counts_json = ? WHERE id = ?",
                 (status, counts_json, run_id))
    conn.commit()


def add_run_item(conn, run_id: int, job_id: str, disposition: str) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO run_items (run_id, job_id, disposition) VALUES (?,?,?)",
        (run_id, job_id, disposition),
    )
    conn.commit()


def add_cv_version(conn, job_id: str, lang: str, path: str, *,
                   created_at: str | None = None, sha: str = "",
                   profile_ver: str = "", is_current: int = 1) -> int:
    """Idempotent on (job_id, path): re-running never duplicates a CV row.
    `profile_ver` records which profile version this CV was built from (drift check)."""
    created_at = created_at or date.today().isoformat()
    if is_current:
        conn.execute("UPDATE cv_versions SET is_current = 0 WHERE job_id = ?", (job_id,))
    row = conn.execute("SELECT id FROM cv_versions WHERE job_id = ? AND path = ?",
                       (job_id, path)).fetchone()
    if row:
        conn.execute("UPDATE cv_versions SET lang=?, created_at=?, hash=?, profile_ver=?, "
                     "is_current=? WHERE id=?",
                     (lang, created_at, sha, profile_ver, is_current, row["id"]))
        cid = row["id"]
    else:
        cid = conn.execute(
            "INSERT INTO cv_versions (job_id, lang, path, created_at, hash, profile_ver, "
            "is_current) VALUES (?,?,?,?,?,?,?)",
            (job_id, lang, path, created_at, sha, profile_ver, is_current),
        ).lastrowid
    conn.commit()
    return cid


def open_prep(conn, job_id: str, path: str, *, rounds_json: str = "[]",
              fmt: str = "", interviewers_json: str = "[]",
              sources_json: str = "[]") -> None:
    """Register (or refresh) the prep row for a job. Content stays in `path`."""
    now = date.today().isoformat()
    conn.execute(
        "INSERT INTO prep (job_id, path, prep_status, rounds_json, format, "
        "interviewers_json, sources_json, updated_at) VALUES (?,?, 'draft',?,?,?,?,?) "
        "ON CONFLICT(job_id) DO UPDATE SET path=excluded.path, rounds_json=excluded.rounds_json, "
        "format=excluded.format, interviewers_json=excluded.interviewers_json, "
        "sources_json=excluded.sources_json, updated_at=excluded.updated_at",
        (job_id, path, rounds_json, fmt, interviewers_json, sources_json, now))
    conn.commit()


def set_prep_status(conn, job_id: str, to: str, *, at: str | None = None) -> None:
    if to not in PREP_STATUSES:
        raise ValueError(f"unknown prep_status: {to}")
    cur = conn.execute("UPDATE prep SET prep_status=?, updated_at=? WHERE job_id=?",
                       (to, at or date.today().isoformat(), job_id))
    if cur.rowcount == 0:
        raise KeyError(job_id)
    conn.commit()


def add_prep_round(conn, job_id: str, round_type: str, *, at: str | None = None,
                   notes: str = "", went_well: str = "", to_fix: str = "") -> int:
    at = at or date.today().isoformat()
    cur = conn.execute(
        "INSERT INTO prep_rounds (job_id, at, round_type, notes, went_well, to_fix) "
        "VALUES (?,?,?,?,?,?)", (job_id, at, round_type, notes, went_well, to_fix))
    conn.commit()
    return cur.lastrowid


def get_prep(conn, job_id: str) -> dict | None:
    row = conn.execute("SELECT * FROM prep WHERE job_id = ?", (job_id,)).fetchone()
    if row is None:
        return None
    d = dict(row)
    d["rounds"] = [dict(r) for r in conn.execute(
        "SELECT * FROM prep_rounds WHERE job_id = ? ORDER BY at, id", (job_id,))]
    return d


_APPLIED_STATUSES = {"applied", "screen", "tech", "onsite", "offer"}


def stage_of(row, has_cv: bool, has_prep: bool) -> list[str]:
    """Agent-side pipeline stage, DERIVED from existing data (no stage column).

    Returns the ordered list of stages this job has reached. Always includes
    'scanned' (the row exists); later stages only if their artifact exists.
    """
    stages = ["scanned"]
    if (row["match_score"] or 0) > 0 or (row["verdict"] or ""):
        stages.append("scored")
    if has_cv:
        stages.append("cv")
    if has_prep:
        stages.append("prep")
    if (row["status"] or "") in _APPLIED_STATUSES:
        stages.append("applied")
    return stages


def report(conn) -> dict:
    """Funnel + backlog + follow-ups due. Reads DB only."""
    today = date.today().isoformat()
    funnel = {s: 0 for s in STATUSES}
    for r in conn.execute("SELECT status, COUNT(*) c FROM jobs GROUP BY status"):
        funnel[r["status"]] = r["c"]
    backlog = conn.execute(
        "SELECT COUNT(*) c FROM jobs WHERE applied_at IS NULL OR applied_at = ''"
    ).fetchone()["c"]
    due = conn.execute(
        "SELECT id, company, title, followup_at FROM jobs "
        "WHERE followup_at <> '' AND followup_at IS NOT NULL AND followup_at <= ? "
        "ORDER BY followup_at", (today,)
    ).fetchall()
    return {"funnel": funnel, "backlog": backlog,
            "followup_due": [dict(r) for r in due]}


# --- B7: export / restore / backup -----------------------------------------
# FK-safe restore order: parents before children.
TABLE_ORDER = ("runs", "jobs", "cv_versions", "prep",
               "job_events", "prep_rounds", "run_items")


def export_data(conn) -> dict:
    """Full state dump, round-trippable by restore_data(). Reads only."""
    from datetime import datetime
    tables = {t: [dict(r) for r in conn.execute(f"SELECT * FROM {t}")]
              for t in TABLE_ORDER}
    return {"schema_version": SCHEMA_VERSION,
            "exported_at": datetime.now().isoformat(timespec="seconds"),
            "counts": {t: len(rows) for t, rows in tables.items()},
            "tables": tables}


def restore_data(conn, payload: dict) -> dict:
    """Load an export_data() payload. INSERT OR REPLACE, parents first.

    Never touches content files (`jobs/*.md`, `cv/*`) — DB state only.
    """
    if not isinstance(payload, dict) or "tables" not in payload:
        raise ValueError("not an export payload (missing 'tables')")
    ver = payload.get("schema_version")
    if ver is not None and ver > SCHEMA_VERSION:
        raise ValueError(f"export schema_version {ver} > supported {SCHEMA_VERSION}")
    loaded = {}
    for t in TABLE_ORDER:
        rows = payload["tables"].get(t, [])
        if not rows:
            loaded[t] = 0
            continue
        cols = list(rows[0])
        sql = (f"INSERT OR REPLACE INTO {t} ({', '.join(cols)}) "
               f"VALUES ({', '.join('?' for _ in cols)})")
        conn.executemany(sql, [[r.get(c) for c in cols] for r in rows])
        loaded[t] = len(rows)
    conn.commit()
    return loaded


def backup_db(src_path=DEFAULT_DB, dst_path=None) -> Path:
    """Online binary backup via sqlite3 backup API (safe while DB is open)."""
    from datetime import datetime
    src = Path(src_path)
    if dst_path is None:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        dst_path = src.with_name(f"{src.name}.bak-{stamp}")
    dst = Path(dst_path)
    with sqlite3.connect(str(src)) as s, sqlite3.connect(str(dst)) as d:
        s.backup(d)
    return dst
