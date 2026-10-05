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
_LIST_COLS = ("id", "company", "title", "source", "seniority", "location",
              "status", "match_score", "verdict", "duplicate_of", "followup_at",
              "next_action", "applied_at", "apply_method")


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
    sql = f"SELECT {', '.join(_LIST_COLS)} FROM jobs"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY match_score DESC, id"
    return [dict(r) for r in conn.execute(sql, params)]


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
        self._send({"error": "not found"}, 404)

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
