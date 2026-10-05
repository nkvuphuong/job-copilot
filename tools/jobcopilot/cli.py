#!/usr/bin/env python3
"""jobcopilot CLI. Single entry for agent + human state writes (DB is canonical).

Content stays in files; lifecycle/identity/run live here.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import db  # noqa: E402
from identity import (company_slug, dedupe_key, extract_external_id,  # noqa: E402
                      find_duplicates, title_norm, url_canonical)

_LIST_COLS = {"skills_required": "skills_required_json",
              "skills_nice": "skills_nice_json",
              "gap_skills": "gap_skills_json",
              "lang_req": "lang_req_json"}
_IDENTITY = ("url_canonical", "dedupe_key", "company_slug", "title_norm", "external_id")


def _dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, default=str)


def _row_to_dict(row) -> dict:
    return {k: row[k] for k in row.keys()} if row is not None else None


def cmd_init(args) -> int:
    conn = db.connect(args.db)
    db.init_schema(conn)
    tables = [r["name"] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    print(f"init ok: {args.db}")
    print("tables:", ", ".join(t for t in tables if not t.startswith("sqlite_")))
    return 0


def cmd_import(args) -> int:
    import migrate
    conn = db.connect(args.db)
    root = db.REPO_ROOT
    res = migrate.run(conn, root, root / "jobs", root / "cv", strip=not args.no_strip)
    jobs = conn.execute("SELECT COUNT(*) c FROM jobs").fetchone()["c"]
    cvs = conn.execute("SELECT COUNT(*) c FROM cv_versions").fetchone()["c"]
    print(_dump({**res, "db_jobs": jobs, "db_cv_versions": cvs}))
    return 0


def cmd_dedupe_check(args) -> int:
    conn = db.connect(args.db)
    hits = find_duplicates(conn, source=args.source, external_id=args.external_id,
                           url=args.url, company=args.company, title=args.title,
                           location=args.location)
    print(_dump({"key": dedupe_key(args.source, args.external_id, args.url),
                 "exact": _row_to_dict(hits["exact"]),
                 "fuzzy": [_row_to_dict(r) for r in hits["fuzzy"]]}))
    return 0


def _derive(payload: dict) -> dict:
    row = dict(payload)
    for src, dst in _LIST_COLS.items():
        if src in row:
            row[dst] = json.dumps(row.pop(src), ensure_ascii=False)
    url = str(row.get("url", ""))
    src = str(row.get("source", ""))
    row.setdefault("external_id", extract_external_id(url))
    row["url_canonical"] = url_canonical(url)
    row["dedupe_key"] = dedupe_key(src, row["external_id"], url)
    row["company_slug"] = company_slug(str(row.get("company", "")))
    row["title_norm"] = title_norm(str(row.get("title", "")))
    if "referral" in row:
        row["referral"] = 1 if row["referral"] else 0
    return row


def cmd_add(args) -> int:
    conn = db.connect(args.db)
    payload = json.loads(args.json)
    payload.setdefault("id", "")  # upsert_job requires id
    if not payload["id"]:
        print("error: 'id' required", file=sys.stderr)
        return 2
    run_id = payload.pop("run_id", None)
    row = _derive(payload)
    hits = find_duplicates(conn, source=row.get("source", ""),
                           external_id=row.get("external_id", ""),
                           url=row.get("url", ""), company=row.get("company", ""),
                           title=row.get("title", ""), location=row.get("location", ""))
    if hits["exact"] is not None:
        print(_dump({"status": "duplicate", "exact": hits["exact"]["id"]}))
        return 0
    if hits["fuzzy"] and not row.get("duplicate_of"):
        row["duplicate_of"] = hits["fuzzy"][0]["id"]
    if run_id:
        row["first_run_id"] = run_id
    db.upsert_job(conn, row)
    if run_id:
        db.add_run_item(conn, run_id, row["id"], "new")
    print(_dump({"status": "added", "id": row["id"],
                 "duplicate_of": row.get("duplicate_of", "")}))
    return 0


def cmd_run(args) -> int:
    conn = db.connect(args.db)
    if args.action == "start":
        rid = db.start_run(conn, args.source, args.params or "{}")
        print(_dump({"run_id": rid}))
        return 0
    db.finish_run(conn, args.run_id, args.counts or "{}", args.status)
    print(_dump({"run_id": args.run_id, "status": args.status}))
    return 0


def cmd_status(args) -> int:
    conn = db.connect(args.db)
    extra = {k: v for k, v in {
        "applied_at": args.at, "apply_method": args.method,
        "followup_at": args.followup_at, "next_action": args.next_action,
        "next_action_date": args.next_action_date,
    }.items() if v is not None}
    db.set_status(conn, args.job_id, args.to, note=args.note or "", **extra)
    print(_dump({"job_id": args.job_id, "to": args.to, "updated": list(extra)}))
    return 0


def cmd_prep(args) -> int:
    conn = db.connect(args.db)
    if args.action == "open":
        path = args.path or f"prep/{args.job_id}.md"
        db.open_prep(conn, args.job_id, path)
        print(_dump({"job_id": args.job_id, "path": path, "prep_status": "draft"}))
    elif args.action == "status":
        db.set_prep_status(conn, args.job_id, args.to)
        print(_dump({"job_id": args.job_id, "prep_status": args.to}))
    elif args.action == "round-add":
        rid = db.add_prep_round(conn, args.job_id, args.type, at=args.at,
                                notes=args.notes or "", went_well=args.went_well or "",
                                to_fix=args.to_fix or "")
        print(_dump({"round_id": rid, "job_id": args.job_id, "type": args.type}))
    elif args.action == "show":
        p = db.get_prep(conn, args.job_id)
        print(_dump(p) if p else _dump({"error": "no prep for " + args.job_id}))
    elif args.action == "list":
        rows = conn.execute(
            "SELECT j.id, j.company, j.title, p.prep_status FROM jobs j "
            "LEFT JOIN prep p ON p.job_id = j.id "
            "WHERE j.status IN ('applied','screen','tech','onsite','offer') "
            "ORDER BY j.status, j.id")
        print(_dump([dict(r) for r in rows]))
    return 0


def cmd_report(args) -> int:
    conn = db.connect(args.db)
    print(_dump(db.report(conn)))
    return 0


def _export_rows(conn) -> dict:
    return db.export_data(conn)


def _write_csv_zip(payload: dict, out: str) -> None:
    """One CSV per table inside a single .zip (stdlib csv + zipfile)."""
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for table, rows in payload["tables"].items():
            buf = io.StringIO()
            cols = list(rows[0]) if rows else []
            w = csv.writer(buf)
            w.writerow(cols)
            for r in rows:
                w.writerow(["" if r.get(c) is None else r.get(c) for c in cols])
            z.writestr(f"{table}.csv", buf.getvalue())
        z.writestr("_meta.json", _dump(
            {"schema_version": payload["schema_version"],
             "exported_at": payload["exported_at"], "counts": payload["counts"]}))


def _export_md(conn) -> str:
    rep = db.report(conn)
    lines = ["# job-copilot export", "",
             f"Funnel: " + " · ".join(f"{k}={v}" for k, v in rep["funnel"].items() if v),
             f"Backlog (chưa nộp): {rep['backlog']}", ""]
    rows = conn.execute(
        "SELECT id, status, company, title, match_score, followup_at FROM jobs "
        "ORDER BY match_score DESC, id").fetchall()
    lines += ["| id | status | company | title | score | follow-up |",
              "|---|---|---|---|---|---|"]
    for r in rows:
        lines.append("| {} | {} | {} | {} | {} | {} |".format(
            r["id"], r["status"], r["company"], r["title"],
            r["match_score"] or "", r["followup_at"] or ""))
    due = rep["followup_due"]
    if due:
        lines += ["", "## Follow-up due", ""]
        lines += [f"- {d['id']} — {d['company']} ({d['followup_at']})" for d in due]
    return "\n".join(lines) + "\n"


def cmd_export(args) -> int:
    conn = db.connect(args.db)
    if args.format == "md":
        text = _export_md(conn)
        if args.out:
            Path(args.out).write_text(text, encoding="utf-8")
            print(_dump({"status": "written", "format": "md", "out": args.out}))
        else:
            sys.stdout.write(text)
        return 0
    payload = _export_rows(conn)
    if args.format == "csv":
        if not args.out:
            print("error: --format csv needs --out <file.zip>", file=sys.stderr)
            return 2
        _write_csv_zip(payload, args.out)
        print(_dump({"status": "written", "format": "csv", "out": args.out,
                     "counts": payload["counts"]}))
        return 0
    text = _dump(payload)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(_dump({"status": "written", "format": "json", "out": args.out,
                     "counts": payload["counts"]}))
    else:
        print(text)
    return 0


def cmd_restore(args) -> int:
    payload = json.loads(Path(args.infile).read_text(encoding="utf-8"))
    conn = db.connect(args.into)
    db.init_schema(conn)
    loaded = db.restore_data(conn, payload)
    print(_dump({"status": "restored", "into": args.into, "loaded": loaded}))
    return 0


def cmd_backup(args) -> int:
    dst = db.backup_db(args.db, args.out)
    print(_dump({"status": "backed-up", "out": str(dst)}))
    return 0


# --- selfcheck: smallest runnable check for non-trivial logic (identity/dedupe) ---
_SC = [
    (url_canonical, ("https://ITViec.com/it-jobs/foo-5349?utm_source=x#apply",),
     "https://itviec.com/it-jobs/foo-5349"),
    (url_canonical, ("https://x.com/j?b=2&a=1",), "https://x.com/j?a=1&b=2"),
    (title_norm, ("Senior  Full-Stack Developer (NodeJS)!",),
     "senior full stack developer nodejs"),
    (company_slug, ("Koala Digital, Inc.",), "koala-digital-inc"),
    (extract_external_id, ("https://itviec.com/it-jobs/foo-5349",), "5349"),
    (dedupe_key, ("itviec", "5349", "https://itviec.com/x"), "itviec:5349"),
]


def cmd_selfcheck(args) -> int:
    for i, (fn, inargs, want) in enumerate(_SC, 1):
        got = fn(*inargs)
        assert got == want, f"case {i} {fn.__name__}{inargs} -> {got!r} != {want!r}"
    assert dedupe_key(url="https://a.com/x") == "url:https://a.com/x"
    assert dedupe_key() == ""
    print("SELFCHECK OK")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="jc", description="job-copilot DB/CLI")
    p.add_argument("--db", default=str(db.DEFAULT_DB), help="sqlite path")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="create DB + schema (idempotent)")
    sub.add_parser("selfcheck", help="assert identity/dedupe helpers")
    p_imp = sub.add_parser("import", help="migrate jobs/*.md frontmatter -> DB, strip it")
    p_imp.add_argument("--no-strip", action="store_true", help="import only, keep frontmatter")

    p_dc = sub.add_parser("dedupe-check", help="is this job already known?")
    p_dc.add_argument("url")
    p_dc.add_argument("--source", default="")
    p_dc.add_argument("--external-id", default="")
    p_dc.add_argument("--company", default="")
    p_dc.add_argument("--title", default="")
    p_dc.add_argument("--location", default="")

    p_add = sub.add_parser("add", help="register a scored job from JSON")
    p_add.add_argument("--json", required=True)

    p_run = sub.add_parser("run", help="scan session lifecycle")
    run_sub = p_run.add_subparsers(dest="action", required=True)
    rs = run_sub.add_parser("start")
    rs.add_argument("--source", required=True)
    rs.add_argument("--params", default="{}")
    rf = run_sub.add_parser("finish")
    rf.add_argument("run_id", type=int)
    rf.add_argument("--counts", default="{}")
    rf.add_argument("--status", default="done")

    p_st = sub.add_parser("status", help="transition a job's status")
    p_st.add_argument("job_id")
    p_st.add_argument("--to", required=True)
    p_st.add_argument("--at")
    p_st.add_argument("--method")
    p_st.add_argument("--note")
    p_st.add_argument("--followup-at", dest="followup_at")
    p_st.add_argument("--next-action", dest="next_action")
    p_st.add_argument("--next-action-date", dest="next_action_date")

    sub.add_parser("report", help="funnel + backlog + follow-ups (from DB)")

    p_prep = sub.add_parser("prep", help="interview prep status + mock round log")
    prep_sub = p_prep.add_subparsers(dest="action", required=True)
    po = prep_sub.add_parser("open"); po.add_argument("job_id"); po.add_argument("--path")
    ps = prep_sub.add_parser("status"); ps.add_argument("job_id"); ps.add_argument("--to", required=True)
    pr = prep_sub.add_parser("round-add"); pr.add_argument("job_id"); pr.add_argument("--type", required=True)
    pr.add_argument("--at"); pr.add_argument("--notes"); pr.add_argument("--went-well", dest="went_well")
    pr.add_argument("--to-fix", dest="to_fix")
    psh = prep_sub.add_parser("show"); psh.add_argument("job_id")
    prep_sub.add_parser("list")

    p_ex = sub.add_parser("export", help="dump state: json (round-trip) | csv (zip) | md")
    p_ex.add_argument("--format", choices=["json", "csv", "md"], default="json")
    p_ex.add_argument("--out", help="output file (required for csv)")

    p_rs = sub.add_parser("restore", help="load a JSON export into a DB")
    p_rs.add_argument("--in", dest="infile", required=True)
    p_rs.add_argument("--into", default=None, help="target DB (default jobcopilot-restore.db)")

    p_bk = sub.add_parser("backup", help="online binary copy of the DB")
    p_bk.add_argument("--out", default=None)

    args = p.parse_args(argv)
    if args.cmd == "run":
        args.action = getattr(args, "action", None)
    if args.cmd == "restore" and not args.into:
        args.into = str(db.REPO_ROOT / "jobcopilot-restore.db")
    table = {"init": cmd_init, "selfcheck": cmd_selfcheck, "import": cmd_import,
             "dedupe-check": cmd_dedupe_check, "add": cmd_add, "run": cmd_run,
             "status": cmd_status, "report": cmd_report, "prep": cmd_prep,
             "export": cmd_export, "restore": cmd_restore, "backup": cmd_backup}
    try:
        return table[args.cmd](args)
    except (KeyError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
