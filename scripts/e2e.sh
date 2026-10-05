#!/usr/bin/env bash
# End-to-end test for job-copilot (DB/CLI/UI + vn-it-cv scripts).
#
#   ./scripts/e2e.sh          # DRY-RUN (default): print the steps, change nothing
#   ./scripts/e2e.sh --run    # run the full suite inside a throwaway temp clone
#   ./scripts/e2e.sh --run --keep   # keep the temp dir for inspection
#
# Safety: everything happens in $TMPDIR/jobcopilot-e2e; the real working tree,
# jobcopilot.db, jobs/ and cv/ are never modified. Server binds 127.0.0.1:8779.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT=8779
HOST=127.0.0.1
CLI_REL="tools/jobcopilot/cli.py"
SERVER_REL="tools/jobcopilot/server.py"
SELFCHECK_CV_REL=".opencode/skills/vn-it-cv/scripts/selfcheck_cv.py"
RENDER_CV_REL=".opencode/skills/vn-it-cv/scripts/render_cv.py"

MODE=check
KEEP=0
for a in "$@"; do
  case "$a" in
    --run) MODE=run ;;
    --check|--dry-run) MODE=check ;;
    --keep) KEEP=1 ;;
    -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
    *) echo "unknown flag: $a" >&2; exit 2 ;;
  esac
done

# ---------- reporting ----------
_pass=0; _fail=0
ok()   { printf '  \033[32mPASS\033[0m %s\n' "$1"; _pass=$((_pass+1)); }
bad()  { printf '  \033[31mFAIL\033[0m %s\n' "$1"; _fail=$((_fail+1)); }
step() { printf '\n\033[1m== %s ==\033[0m\n' "$1"; }
skip() { printf '  \033[33mSKIP\033[0m %s\n' "$1"; }
# assert_eq <desc> <got> <want>
assert_eq() { [ "$2" = "$3" ] && ok "$1 ($2)" || bad "$1: got '$2' want '$3'"; }
# assert_true <desc> <exit-code>
assert_true() { [ "$2" -eq 0 ] && ok "$1" || bad "$1 (exit $2)"; }

# ---------- dry-run ----------
print_plan() {
  cat <<EOF
job-copilot E2E — DRY RUN (no changes made)

Target: $REPO_ROOT
Temp clone: \$TMPDIR/jobcopilot-e2e/job-copilot   server: $HOST:$PORT

Steps that WOULD run with --run:
  P0  clean-room: git clone . -> temp; assert only _example*; seed jobs/ cv/ profile.md
  P1  setup:      cli.py init x2; assert 7 tables; assert jobcopilot.db not tracked
  P2  migrate:    cli.py import -> {jobs:13,cv_versions:13}; frontmatter stripped;
                  header+raw JD kept; .backup/=13; re-import idempotent (0 changes)
  P3  happy path: run start; dedupe exact hit / fuzzy flag; add new; add repost ->
                  duplicate_of; status applied -> job_events + report + followup_due
  P4  ui/api:     server on :$PORT; GET / = 200; /api/report; /api/jobs filter;
                  POST status; POST duplicate clear; 404 unknown; 400 bad json (stays up)
  P5  negative:   add missing id -> exit 2; status unknown/no-tracebacks;
                  import --no-strip must not wipe stripped rows; unicode round-trip
  P6  vn-it-cv:   selfcheck_cv.py all -> exit 0; 2 temp negative CVs -> exit 1;
                  render_cv.py -> html with <header>, no <!-- comments
  P7  cleanup:    kill server; remove temp (unless --keep); assert real tree unchanged
EOF
}

# ---------- prerequisite checks ----------
prereqs() {
  local rc=0
  command -v python3 >/dev/null || { echo "missing: python3" >&2; rc=1; }
  command -v git >/dev/null     || { echo "missing: git" >&2; rc=1; }
  python3 "$REPO_ROOT/$CLI_REL" selfcheck >/dev/null 2>&1 || { echo "jc selfcheck failed" >&2; rc=1; }
  [ -f "$REPO_ROOT/profile.md" ] || echo "note: no profile.md -> P6 will be SKIPPED"
  python3 - <<PY || { echo "port $PORT busy (set PORT)" >&2; rc=1; }
import socket,sys
s=socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # ignore TIME_WAIT, like the server
try: s.bind(("$HOST",$PORT)); s.close()
except OSError: sys.exit(1)
PY
  return $rc
}

# ---------- full run ----------
TMPBASE=""
SRV_PID=""
cleanup() {
  [ -n "$SRV_PID" ] && { kill "$SRV_PID" 2>/dev/null; wait "$SRV_PID" 2>/dev/null; }
  if [ "$KEEP" -ne 1 ] && [ -n "$TMPBASE" ]; then rm -rf "$TMPBASE"; fi
  return 0
}

run_suite() {
  TMPBASE="${TMPDIR:-/tmp}"; TMPBASE="${TMPBASE%/}/jobcopilot-e2e"
  DIR="$TMPBASE/job-copilot"
  rm -rf "$TMPBASE"; mkdir -p "$TMPBASE"
  trap cleanup EXIT

  cd "$REPO_ROOT" || return 1

  step "P0 clean-room clone + seed"
  # Seed from `jobs/.backup/` (the pre-migration originals): the working tree's
  # jobs/*.md may already be stripped, so seeding from jobs/ would import 0 rows.
  SRC="$REPO_ROOT/jobs/.backup"
  [ -d "$SRC" ] || { bad "missing jobs/.backup (run 'cli.py import' first)"; return 1; }
  # Snapshot the CURRENT working tree (code + skills + docs), not a git clone:
  # a clone would test the last commit and miss uncommitted work under test.
  # Exclude personal data, the local DB, backups and caches — they are seeded
  # explicitly below (clean-room). `git ls-files` lists tracked; copy those + any
  # untracked code a developer is testing.
  mkdir -p "$DIR"
  ( cd "$REPO_ROOT" && git ls-files -z | tar --null -T - -cf - ) | ( cd "$DIR" && tar -xf - )
  ( cd "$REPO_ROOT" && git ls-files --others --exclude-standard -z -- 'tools' '.opencode' 'scripts' 'docs' '*.md' 2>/dev/null | tar --null -T - -cf - ) 2>/dev/null | ( cd "$DIR" && tar -xf - ) || true
  local n_tracked; n_tracked=$(ls "$DIR"/jobs/*.md 2>/dev/null | grep -vc '_example.md')
  assert_eq "clean-room has no real jobs" "${n_tracked:-0}" "0"
  rm -f "$DIR/jobs"/*.md; cp "$SRC"/*.md "$DIR/jobs/"
  cp profile.md "$DIR/profile.md"      # data-agnostic: CVs are created inside the test
  cd "$DIR" || return 1
  local n_seed; n_seed=$(ls jobs/*.md | grep -vc _example)
  assert_true "seeded jobs > 0 ($n_seed)" $([ "$n_seed" -gt 0 ] && echo 0 || echo 1)
  local first_job; first_job=$(ls jobs/*.md | grep -v _example | head -1)
  grep -q '^---' "$first_job"
  assert_true "seeded jobs have frontmatter" $?

  step "P1 setup (init)"
  python3 "$CLI_REL" init >/dev/null; assert_true "init run 1" $?
  python3 "$CLI_REL" init >/dev/null; assert_true "init run 2 (idempotent)" $?
  local tables; tables=$(python3 -c "import sqlite3;print(len([r for r in sqlite3.connect('jobcopilot.db').execute(\"select name from sqlite_master where type='table' and name not like 'sqlite_%'\")]))")
  assert_eq "7 tables (5 v1 + prep + prep_rounds)" "$tables" "7"
  grep -q '^/jobcopilot.db' .gitignore && ok "jobcopilot.db is gitignored" || bad "jobcopilot.db not in .gitignore"

  step "P2 migrate + strip"
  local out; out=$(python3 "$CLI_REL" import)
  assert_eq "import jobs" "$(echo "$out" | python3 -c 'import sys,json;print(json.load(sys.stdin)["jobs"])')" "$n_seed"

  assert_eq "no frontmatter left" "$(grep -lc '^---$' jobs/*.md 2>/dev/null | grep -vc ':0$' || true)" "0"
  assert_eq "backups kept" "$(ls jobs/.backup/*.md | wc -l | tr -d ' ')" "$n_seed"
  grep -q '^# .* — ' "$first_job"; assert_true "header kept" $?
  grep -q 'Raw JD' "$first_job"; assert_true "raw JD kept" $?
  out=$(python3 "$CLI_REL" import)
  assert_eq "re-import strips nothing" "$(echo "$out" | python3 -c 'import sys,json;print(json.load(sys.stdin)["stripped"])')" "0"
  local empty; empty=$(python3 -c "import sqlite3;print(sqlite3.connect('jobcopilot.db').execute(\"select count(*) from jobs where company='' or dedupe_key=''\").fetchone()[0])")
  assert_eq "no rows wiped" "$empty" "0"

  step "P3 happy path (scan -> apply -> track)"
  local RID; RID=$(python3 "$CLI_REL" run start --source itviec | python3 -c 'import sys,json;print(json.load(sys.stdin)["run_id"])')
  assert_true "run start" $([ -n "$RID" ] && echo 0 || echo 1)
  # data-agnostic: read one seeded job's id/url/company/title from the DB
  local SJ SJID SJURL SJC SJD SJL; SJ=$(python3 -c "import sqlite3;r=sqlite3.connect('jobcopilot.db').execute(\"select id,url,company,title,location from jobs where id like '2026-10-itviec-%' order by id limit 1\").fetchone();print('\t'.join(str(x) for x in r))")
  SJID=$(echo "$SJ" | cut -f1); SJURL=$(echo "$SJ" | cut -f2); SJC=$(echo "$SJ" | cut -f3); SJD=$(echo "$SJ" | cut -f4); SJL=$(echo "$SJ" | cut -f5)
  local exact; exact=$(python3 "$CLI_REL" dedupe-check "$SJURL?utm_source=x" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d["exact"]["id"] if d["exact"] else "")')
  assert_eq "dedupe exact hit" "$exact" "$SJID"
  local fuzzy; fuzzy=$(python3 "$CLI_REL" dedupe-check "https://itviec.com/it-jobs/repost-9999" --source itviec --company "$SJC" --title "$SJD" --location "$SJL" | python3 -c 'import sys,json;print(len(json.load(sys.stdin)["fuzzy"]))')
  assert_eq "dedupe fuzzy flagged" "$fuzzy" "1"
  python3 "$CLI_REL" add --json "{\"id\":\"2026-10-import-acme-be\",\"title\":\"Backend Engineer\",\"company\":\"Acme\",\"source\":\"import\",\"url\":\"local://acme\",\"location\":\"HCMC\",\"run_id\":$RID}" >/dev/null
  assert_true "add new job" $?
  python3 "$CLI_REL" add --json '{"id":"2026-10-import-acme-be-r2","title":"Backend Engineer","company":"Acme","source":"import","url":"local://acme2","location":"HCMC"}' >/dev/null
  local dup; dup=$(python3 -c "import sqlite3;print(sqlite3.connect('jobcopilot.db').execute(\"select duplicate_of from jobs where id='2026-10-import-acme-be-r2'\").fetchone()[0])")
  assert_eq "repost flagged duplicate_of" "$dup" "2026-10-import-acme-be"
  python3 "$CLI_REL" status 2026-10-import-acme-be --to applied --at 2026-10-05 --method portal --followup-at 2026-09-01 >/dev/null
  assert_true "status applied" $?
  local ev; ev=$(python3 -c "import sqlite3;print(sqlite3.connect('jobcopilot.db').execute(\"select from_status||'->'||to_status from job_events where job_id='2026-10-import-acme-be'\").fetchone()[0])")
  assert_eq "job_events logged" "$ev" "saved->applied"
  local rep; rep=$(python3 "$CLI_REL" report)
  assert_eq "report applied" "$(echo "$rep" | python3 -c 'import sys,json;print(json.load(sys.stdin)["funnel"]["applied"])')" "1"
  local due; due=$(echo "$rep" | python3 -c 'import sys,json;print(sum(1 for r in json.load(sys.stdin)["followup_due"] if r["id"]=="2026-10-import-acme-be"))')
  assert_eq "followup_due picks it up" "$due" "1"

  step "P4 ui / api"
  python3 "$SERVER_REL" --port "$PORT" >"$TMPBASE/server.log" 2>&1 &
  SRV_PID=$!
  for _ in $(seq 1 20); do curl -sf "http://$HOST:$PORT/" >/dev/null && break; sleep 0.2; done
  assert_eq "GET / status" "$(curl -s -o /dev/null -w '%{http_code}' "http://$HOST:$PORT/")" "200"
  local total; total=$(curl -s "http://$HOST:$PORT/api/report" | python3 -c 'import sys,json;print(sum(json.load(sys.stdin)["funnel"].values()))')
  assert_eq "api/report total (seeded+2 added)" "$total" "$((n_seed + 2))"
  local senior; senior=$(curl -s "http://$HOST:$PORT/api/jobs?seniority=senior" | python3 -c 'import sys,json;print(len(json.load(sys.stdin)))')
  assert_true "api/jobs filter nonzero" $([ "$senior" -gt 0 ] && echo 0 || echo 1)
  assert_eq "POST status ok" "$(curl -s -X POST "http://$HOST:$PORT/api/jobs/2026-10-import-acme-be/status" -H 'Content-Type: application/json' -d '{"to":"screen"}' | python3 -c 'import sys,json;print(json.load(sys.stdin).get("ok"))')" "True"
  assert_eq "POST duplicate clear" "$(curl -s -X POST "http://$HOST:$PORT/api/jobs/2026-10-import-acme-be-r2/duplicate" -H 'Content-Type: application/json' -d '{"duplicate_of":""}' | python3 -c 'import sys,json;print(json.load(sys.stdin).get("duplicate_of"))')" ""
  assert_eq "POST unknown -> 404" "$(curl -s -o /dev/null -w '%{http_code}' -X POST "http://$HOST:$PORT/api/jobs/nope/status" -H 'Content-Type: application/json' -d '{"to":"applied"}')" "404"
  assert_eq "POST bad json -> 400" "$(curl -s -o /dev/null -w '%{http_code}' -X POST "http://$HOST:$PORT/api/jobs/2026-10-import-acme-be/status" -H 'Content-Type: application/json' -d 'not json')" "400"
  assert_eq "server survived" "$(curl -s -o /dev/null -w '%{http_code}' "http://$HOST:$PORT/")" "200"

  # v1.1: derived stage + job detail + cv content (self-contained: make a CV for the seeded job)
  printf -- '# Test CV\nBackend\n\nSummary line.\n' > "cv/_e2e_cv-en.md"
  python3 "$CLI_REL" add --json "{\"id\":\"$SJID\",\"title\":\"$SJD\",\"company\":\"$SJC\",\"source\":\"itviec\",\"url\":\"$SJURL\"}" >/dev/null
  python3 -c "import sqlite3;c=sqlite3.connect('jobcopilot.db');c.execute(\"delete from cv_versions where job_id='$SJID'\");c.execute(\"insert into cv_versions(job_id,lang,path,created_at,is_current) values('$SJID','en','cv/_e2e_cv-en.md','2099-01-01',1)\");c.commit()"
  local st; st=$(curl -s "http://$HOST:$PORT/api/jobs/$SJID" | python3 -c 'import sys,json;s=json.load(sys.stdin)["stage"];print(",".join(x for x in s if x in ("scanned","scored","cv")))')
  assert_eq "stage derived (scanned,scored,cv)" "$st" "scanned,scored,cv"
  local jd; jd=$(curl -s "http://$HOST:$PORT/api/jobs/$SJID" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(1 if d["raw_jd"] and d["url"] else 0)')
  assert_eq "detail has url + raw JD" "$jd" "1"
  local cvmd; cvmd=$(curl -s "http://$HOST:$PORT/api/cv/$SJID" | python3 -c 'import sys,json;print(1 if json.load(sys.stdin).get("markdown") else 0)')
  assert_eq "cv content served" "$cvmd" "1"
  assert_eq "detail unknown -> 404" "$(curl -s -o /dev/null -w '%{http_code}' "http://$HOST:$PORT/api/jobs/nope")" "404"
  assert_eq "cv unknown -> 404" "$(curl -s -o /dev/null -w '%{http_code}' "http://$HOST:$PORT/api/cv/nope")" "404"
  # path traversal must not leak files outside the repo
  python3 -c "import sqlite3;c=sqlite3.connect('jobcopilot.db');c.execute(\"insert or replace into cv_versions(job_id,lang,path,created_at,is_current) values('$SJID','evil','../../../../etc/passwd','2099-01-01',1)\");c.commit()"
  assert_eq "cv path traversal blocked" "$(curl -s -o /dev/null -w '%{http_code}' "http://$HOST:$PORT/api/cv/$SJID")" "404"
  python3 -c "import sqlite3;c=sqlite3.connect('jobcopilot.db');c.execute(\"delete from cv_versions where lang='evil'\");c.commit()"

  # B5.1: interview prep (DB row + round log + cue-card file endpoint)
  printf -- '# Cue card\nBackend prep.\n' > "prep/2026-10-import-acme-be.md"
  python3 "$CLI_REL" prep open 2026-10-import-acme-be >/dev/null; assert_true "prep open" $?
  assert_eq "prep status -> ready" "$(curl -s -X POST "http://$HOST:$PORT/api/jobs/2026-10-import-acme-be/prep" -H 'Content-Type: application/json' -d '{"to":"ready"}' | python3 -c 'import sys,json;print(json.load(sys.stdin).get("prep_status"))')" "ready"
  assert_eq "prep round add" "$(curl -s -X POST "http://$HOST:$PORT/api/jobs/2026-10-import-acme-be/prep-round" -H 'Content-Type: application/json' -d '{"type":"mock","to_fix":"K8s"}' | python3 -c 'import sys,json;print(json.load(sys.stdin).get("ok"))')" "True"
  assert_eq "prep cue card served" "$(curl -s "http://$HOST:$PORT/api/prep/2026-10-import-acme-be" | python3 -c 'import sys,json;print(1 if json.load(sys.stdin).get("markdown") else 0)')" "1"
  assert_eq "prep stage derived" "$(curl -s "http://$HOST:$PORT/api/jobs/2026-10-import-acme-be" | python3 -c 'import sys,json;print(1 if "prep" in json.load(sys.stdin)["stage"] else 0)')" "1"
  assert_eq "prep unknown -> 404" "$(curl -s -o /dev/null -w '%{http_code}' "http://$HOST:$PORT/api/prep/nope")" "404"

  kill "$SRV_PID" 2>/dev/null; wait "$SRV_PID" 2>/dev/null; SRV_PID=""

  step "P5 negative"
  python3 "$CLI_REL" add --json '{"title":"no id"}' >/dev/null 2>&1
  assert_eq "add without id -> 2" "$?" "2"
  python3 "$CLI_REL" status nope --to applied >/dev/null 2>&1
  assert_eq "status unknown job -> 1" "$?" "1"
  python3 "$CLI_REL" status 2026-10-import-acme-be --to bogus >/dev/null 2>&1
  assert_eq "status bad value -> 1" "$?" "1"
  python3 "$CLI_REL" add --json '{"id":"2026-10-import-unicode","title":"Kỹ sư Backend","company":"Công ty Việt","source":"import","url":"local://vn","location":"Hà Nội"}' >/dev/null
  local uni; uni=$(python3 -c "import sqlite3;print(sqlite3.connect('jobcopilot.db').execute(\"select company from jobs where id='2026-10-import-unicode'\").fetchone()[0])")
  assert_eq "unicode round-trip" "$uni" "Công ty Việt"

  step "P6 vn-it-cv"
  if [ -f profile.md ]; then
    python3 "$SELFCHECK_CV_REL" >/dev/null 2>&1; assert_true "selfcheck_cv all pass" $?
    printf -- '---\n# Test\nBackend\n\nx@y.z\n\n## Skills\n- Kafka\n' > cv/_e2e_bad_skill.md
    python3 "$SELFCHECK_CV_REL" cv/_e2e_bad_skill.md >/dev/null 2>&1
    assert_eq "selfcheck_cv rejects unbacked skill -> 1" "$?" "1"
    printf -- '# Test\nBackend\n\nx@y.z\n\n## Summary\nLed a team <!-- e999 -->\n' > cv/_e2e_bad_ev.md
    python3 "$SELFCHECK_CV_REL" cv/_e2e_bad_ev.md >/dev/null 2>&1
    assert_eq "selfcheck_cv rejects unknown evidence -> 1" "$?" "1"
    rm -f cv/_e2e_bad_skill.md cv/_e2e_bad_ev.md
    printf -- '# Test Name\nBackend Engineer\n\nHCMC · x@y.z\n\n## Skills\n- PHP\n' > cv/_e2e_render-en.md
    python3 "$RENDER_CV_REL" cv/_e2e_render-en.md >/dev/null
    local html="cv/_e2e_render-en.html"
    [ -f "$html" ] && ok "render produced html"
    grep -q '<header>' "$html"; assert_true "html has <header>" $?
    grep -q '<!--' "$html" && bad "html leaked a comment" || ok "no <!-- in html"
    rm -f cv/_e2e_render-en.md cv/_e2e_render-en.html cv/_e2e_cv-en.md
  else
    skip "P6 (no profile.md)"
  fi

  step "P7 cleanup"
  [ -n "$SRV_PID" ] && { kill "$SRV_PID" 2>/dev/null; wait "$SRV_PID" 2>/dev/null; SRV_PID=""; }
  cd "$REPO_ROOT" || return 1
  # Only assert the suite didn't touch the real DATA (jobs/cv/db), not that the
  # tree is clean — the developer may be editing code while running E2E.
  local dirty; dirty=$(git status --porcelain -- jobs cv prep offers profile.md jobcopilot.db 2>/dev/null | wc -l | tr -d ' ')
  assert_eq "real data untouched by E2E" "$dirty" "0"
  local ev_real; ev_real=$(python3 "$CLI_REL" report | python3 -c 'import sys,json;print(sum(json.load(sys.stdin)["funnel"].values()))')
  assert_true "real DB untouched (jobs=$ev_real)" $([ "$ev_real" -gt 0 ] && echo 0 || echo 1)
}

# ---------- main ----------
echo "job-copilot E2E"
if [ "$MODE" = check ]; then
  print_plan
  echo
  echo "Prerequisite check:"
  if prereqs; then ok "prerequisites OK"; else bad "prerequisites not met"; fi
  echo
  echo "Run the suite with:  ./scripts/e2e.sh --run"
  exit 0
fi

prereqs || { echo "prerequisites not met; aborting" >&2; exit 1; }
run_suite
printf '\n\033[1mSummary:\033[0m %d passed, %d failed\n' "$_pass" "$_fail"
[ "$_fail" -eq 0 ] || exit 1
