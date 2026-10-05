#!/usr/bin/env python3
"""Local UI + JSON API. Thin layer over db.py (the same write path as the CLI)."""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

import db  # noqa: E402

UI = Path(__file__).resolve().parent / "ui" / "index.html"
REPO_ROOT = Path(__file__).resolve().parents[2]
_LIST_COLS = ("id", "company", "title", "source", "seniority", "location", "remote",
              "status", "match_score", "score_rationale", "gap_skills_json",
              "verdict", "duplicate_of", "followup_at", "next_action", "applied_at",
              "apply_method", "notes", "url")


def _with_stage(conn, rows: list) -> list:
    """Attach the derived agent-pipeline `stage` (no stage column)."""
    has_cv = {r["job_id"] for r in conn.execute(
        "SELECT DISTINCT job_id FROM cv_versions WHERE job_id IS NOT NULL")}
    out = []
    for r in rows:
        d = dict(r)
        has_prep = (REPO_ROOT / "prep" / f"{r['id']}.md").exists()
        d["stage"] = db.stage_of(r, r["id"] in has_cv, has_prep)
        out.append(d)
    return out


def _jobs(conn, q) -> list:
    where, params = [], []
    for col in ("status", "source", "seniority", "run"):
        val = (q.get(col) or [""])[0]
        if not val:
            continue
        if col == "run":
            where.append("id IN (SELECT job_id FROM run_items WHERE run_id = ?)")
        else:
            where.append(f"{col} = ?")
        params.append(val)
    sql = ("SELECT id, company, title, source, seniority, location, remote, status, "
           "match_score, score_rationale, gap_skills_json, verdict, duplicate_of, "
           "followup_at, next_action, applied_at, apply_method, notes, url "
           "FROM jobs")
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY match_score DESC, id"
    return _with_stage(conn, conn.execute(sql, params).fetchall())


def _job_detail(conn, job_id: str) -> dict | None:
    row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if row is None:
        return None
    d = dict(row)
    cvs = [dict(r) for r in conn.execute(
        "SELECT lang, path, created_at, is_current FROM cv_versions "
        "WHERE job_id = ? ORDER BY is_current DESC, created_at DESC", (job_id,))]
    prep = REPO_ROOT / "prep" / f"{job_id}.md"
    d["has_cv"] = bool(cvs)
    d["cvs"] = cvs
    d["prep_path"] = f"prep/{job_id}.md" if prep.exists() else ""
    d["prep"] = db.get_prep(conn, job_id)
    d["stage"] = db.stage_of(row, bool(cvs), prep.exists())
    raw = REPO_ROOT / "jobs" / f"{job_id}.md"
    d["raw_jd"] = raw.read_text(encoding="utf-8") if raw.exists() else ""
    return d


class Handler(BaseHTTPRequestHandler):
    db_path = None

    def log_message(self, *a):  # keep the console quiet
        pass

    def _conn(self):
        return db.connect(self.db_path)  # per-request: ThreadingHTTPServer + sqlite

    def _send(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        u = urlparse(self.path)
        if u.path in ("/", "/index.html"):
            body = UI.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if u.path == "/api/report":
            return self._send(db.report(self._conn()))
        if u.path == "/api/jobs":
            return self._send(_jobs(self._conn(), parse_qs(u.query)))
        parts = [p for p in u.path.split("/") if p]  # api jobs <id> | api cv <id>
        if len(parts) == 3 and parts[:2] == ["api", "jobs"]:
            d = _job_detail(self._conn(), parts[2])
            return self._send(d) if d else self._send({"error": "not found"}, 404)
        if len(parts) == 3 and parts[:2] == ["api", "cv"]:
            return self._cv_content(parts[2])
        if len(parts) == 3 and parts[:2] == ["api", "prep"]:
            return self._prep_content(parts[2])
        self._send({"error": "not found"}, 404)

    def _prep_content(self, job_id: str):
        row = self._conn().execute("SELECT path FROM prep WHERE job_id = ?",
                                   (job_id,)).fetchone()
        default = REPO_ROOT / "prep" / f"{job_id}.md"
        rel = row["path"] if row else (f"prep/{job_id}.md" if default.exists() else "")
        if not rel:
            return self._send({"error": "no prep"}, 404)
        path = (REPO_ROOT / rel).resolve()
        if not str(path).startswith(str(REPO_ROOT) + "/") or not path.exists():
            return self._send({"error": "prep file missing"}, 404)
        return self._send({"path": rel, "markdown": path.read_text(encoding="utf-8")})

    def _cv_content(self, job_id: str):
        conn = self._conn()
        row = conn.execute("SELECT path FROM cv_versions WHERE job_id = ? "
                           "ORDER BY is_current DESC, created_at DESC LIMIT 1",
                           (job_id,)).fetchone()
        if row is None:
            return self._send({"error": "no cv"}, 404)
        path = (REPO_ROOT / row["path"]).resolve()
        if not str(path).startswith(str(REPO_ROOT)) or not path.exists():
            return self._send({"error": "cv file missing"}, 404)
        return self._send({"path": row["path"], "markdown": path.read_text(encoding="utf-8")})

    def do_POST(self):
        u = urlparse(self.path)
        parts = [p for p in u.path.split("/") if p]  # api jobs <id> <action>
        if len(parts) == 4 and parts[:2] == ["api", "jobs"]:
            job_id, action = parts[2], parts[3]
            conn = self._conn()
            try:
                body = self._read_json()
                if action == "status":
                    extra = {k: body[k] for k in ("applied_at", "apply_method",
                             "followup_at", "next_action", "next_action_date") if k in body}
                    db.set_status(conn, job_id, body["to"],
                                  at=body.get("at"), note=body.get("note", ""), **extra)
                    return self._send({"ok": True})
                if action == "duplicate":
                    dup = body.get("duplicate_of", "")
                    conn.execute("UPDATE jobs SET duplicate_of = ? WHERE id = ?",
                                 (dup, job_id))
                    conn.commit()
                    return self._send({"ok": True, "duplicate_of": dup})
                if action == "prep":
                    db.set_prep_status(conn, job_id, body["to"])
                    return self._send({"ok": True, "prep_status": body["to"]})
                if action == "prep-round":
                    rid = db.add_prep_round(conn, job_id, body.get("type", "mock"),
                                            at=body.get("at"), notes=body.get("notes", ""),
                                            went_well=body.get("went_well", ""),
                                            to_fix=body.get("to_fix", ""))
                    return self._send({"ok": True, "round_id": rid})
            except KeyError:
                return self._send({"error": f"unknown job {job_id}"}, 404)
            except Exception as e:  # surface, don't crash the server
                return self._send({"error": str(e)}, 400)
        self._send({"error": "not found"}, 404)


def main(argv=None) -> int:
    import argparse
    p = argparse.ArgumentParser(prog="jc-serve")
    p.add_argument("--db", default=str(db.DEFAULT_DB))
    p.add_argument("--port", type=int, default=8765)
    a = p.parse_args(argv)
    Handler.db_path = a.db
    db.init_schema(db.connect(a.db))  # self-init if DB missing
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    print(f"jobcopilot UI: http://127.0.0.1:{a.port}  (db={a.db})  Ctrl-C to stop")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
