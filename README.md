# job-copilot

A repeatable, **honest** job-hunt pipeline that runs inside [opencode](https://opencode.ai): scan job boards → triage → score against your profile → tailor a truthful CV per JD → track applications → compare offers → onboard.

It is **not** an auto-apply bot. A human reviews and submits every application. The value is a controlled pipeline and a CV that never lies.

## The idea in one line

`Setup → Scope → Scan → Extract & Score → Tailor CV → Apply → Interview Prep → Track → Offers → Onboard → Loop`

Full detail: **[WORKFLOW.md](WORKFLOW.md)**.

## Screenshots

The local UI (`http://127.0.0.1:8765`) on throwaway demo data — placeholder companies, no personal data:

![Dashboard: funnel by status, job list with score, derived stage, next action, profile-sync drift](docs/screenshots/dashboard.png)

![Job detail: score breakdown, missing skills, CV versions, interview prep, raw JD](docs/screenshots/job-detail.png)

## What's in the repo

| Path | What it is | Shared? |
|---|---|---|
| `.opencode/skills/job-hunt/` | Orchestration skill (the pipeline) + per-source references | ✅ |
| `.opencode/skills/vn-it-cv/` | CV generate/review/score skill + templates + scripts | ✅ |
| `.opencode/skills/profile-sync/` | `profile.md` → LinkedIn / ITviec / TopCV / GitHub packs (+ prefill guardrails) | ✅ |
| `tools/jobcopilot/` | State store (SQLite) + `jc` CLI + local UI (`docs/spec-db-ui.md`) | ✅ |
| `profile.example.md` | Template for your source-of-truth profile | ✅ |
| `jobs/_example.md` | Job-posting schema (frontmatter + raw JD) | ✅ |
| `cv/_example-en.md` | Tailored-CV shape (with `<!-- e001 -->` trace) | ✅ |
| `offers/_example.md` | Offer-comparison schema | ✅ |
| `prep/_example.md` | Interview-prep cue card (JD digest + company brief + tech/non-tech) | ✅ |
| `sync/_example.md` | Shape of a `sync/<platform>.md` profile pack (generic) | ✅ |
| `WORKFLOW.md` / `ONBOARDING.md` / `PREREQUISITES.md` | Docs | ✅ |
| `profile.md`, `jobs/*`, `cv/*`, `offers/*`, `prep/*`, `sync/*`, `jobcopilot.db*` | **Your personal data** | ❌ gitignored |

Your data stays local. Cloning the repo gives you the tool; you bring your own profile.

## Quickstart

```bash
git clone <this repo> job-copilot
cd job-copilot
git config core.hooksPath .githooks                     # enable the commit leak gate (not cloned)
cp profile.example.md profile.md                       # then fill it (see ONBOARDING.md)
python3 tools/jobcopilot/cli.py init                   # create jobcopilot.db (state store)
python3 tools/jobcopilot/server.py                     # UI at http://127.0.0.1:8765
opencode                                               # run opencode from inside the repo
```

Only Python 3 (stdlib) is needed — no deps. Docker is optional (below). State (status, dedupe,
runs) lives in `jobcopilot.db` (gitignored); content stays in `jobs/`, `cv/`,
`prep/`, `offers/`, `profile.md`. Move your state on the UI; let the agent do the
scanning/tailoring. Existing Markdown is imported once with `cli.py import`.
Before saving a job, `cli.py dedupe-check <url> --jd-file jobs/<id>.md` also flags
cross-channel reposts (an agency copy of a named employer's post) by the numbers
and terms that survive a rewrite, and names the probable employer as `[infer]`.

## Docker

Run the state store + UI + CLI in one container. Content stays in plain files on a
volume, so a host agent and the container can work on the same data.

```bash
docker compose up -d --build      # UI at http://127.0.0.1:8765
docker compose run --rm jc status # CLI on the same DB
docker compose down               # stops it; the volume (and your data) stays
```

Volume `jobcopilot-data` → `/data`, holding `jobcopilot.db` plus `profile.md`,
`jobs/`, `cv/`, `prep/`, `offers/`, `sync/`. First run seeds `profile.md` from
`profile.example.md` and each `_example.md`; nothing existing is overwritten.

- **Image is code only.** `.dockerignore` keeps `jobs/`, `cv/`, `profile.md` and
  `jobcopilot.db*` out of the build context — `docker run --rm jobcopilot:local
  ls /app` shows just `tools/` and `seeds/`.
- **Loopback only** (`127.0.0.1:8765`): the UI has no auth. Publish wider on
  purpose, not by accident. If a host `server.py` already listens on 8765, stop
  it or pick another port: `JC_PUBLISH=8766 docker compose up -d`.
- **CV PDF export stays on the host.** `export_cv.py` drives headless Chrome,
  which is not in the image (Chrome plus fonts would dwarf the code). The PDF
  lands in `cv/`, so the container sees it immediately.
- **Bring existing data in:** `./scripts/docker-import.sh` (uses `cli.py backup`
  for a consistent copy; `--force` to overwrite). `docker compose run --rm jc
  backup` writes a timestamped copy inside the volume.
- **Linux with uid ≠ 1000:** `docker compose build --build-arg UID=$(id -u)
  --build-arg GID=$(id -g)`. To keep the same files visible to a host agent, bind
  mount instead (`./data:/data` in `docker-compose.yml`) and run host commands
  with `JC_DATA=$PWD/data`.

The agent itself (`opencode`, the `chrome-devtools` MCP, `jev`) still runs on the
host — scanning needs a logged-in browser. Docker covers state, UI and CLI.

Then, in opencode, just talk:
- "set up my profile from this CV: /path/to/cv.pdf"
- "scan ITViec for senior backend in HCMC, 3 pages"
- "tailor a CV for that Acme job"
- "I applied to Acme — log it"
- "prep me for the Acme interview"
- "mock interview me for the Acme tech round"
- "update my LinkedIn profile" (pack + prefill; **you** press Save)

The `job-hunt` and `vn-it-cv` skills are project-local, so **you must run opencode from inside the repo**.

## Tests

```bash
./scripts/e2e.sh          # dry-run: prints the steps, changes nothing
./scripts/e2e.sh --run    # full E2E in a throwaway temp clone (DB/CLI/UI + vn-it-cv)
```

Everything runs in `$TMPDIR/jobcopilot-e2e`; your real data and DB are never touched.

## Prerequisites

See **[PREREQUISITES.md](PREREQUISITES.md)** — opencode, the `chrome-devtools` MCP, and the `jev` tool for triage.

## The honesty guarantee

- `profile.md` is the single source of truth; every experience bullet has a stable `evidence_id`.
- A tailored CV may only **select / reorder / reword** — never invent. Every bullet keeps its `<!-- e001 -->` trace.
- `scripts/selfcheck_cv.py` fails if a CV references an unknown evidence id, claims a skill not backed by an evidence bullet / `confirmed: true` skill in `profile.md`, puts an unbacked tech in a role's `**Tech:**` line, or leaks a template placeholder into the header. Summary metrics are warn-only by default.
- `scripts/ats_check.py` simulates ATS text extraction (email / phone / profile URL, section order, per-role dates) and flags a stale or rasterized PDF, a 3-page overflow, or a sparse page 2.
- No auto-apply. Ever.

## License

MIT.
