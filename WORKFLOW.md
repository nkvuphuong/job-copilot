# Workflow

The fixed pipeline. Each phase has an input, an output, and the tool/skill that runs it.
Data flows left to right; you can jump in at any phase.

```
0 Setup ─▶ 1 Scope ─▶ 2 Scan ─▶ 3 Extract & Score ─▶ 4 Tailor CV ─▶ 5 Apply ─▶ 5.5 Prep ─▶ 6 Track ─▶ 7 Offers ─▶ 8 Onboard
                                                                                    │                              │
                                                                                    ◀────────── Loop ─────────────┘
```

| # | Phase | Input | Output | Tool / skill |
|---|---|---|---|---|
| 0 | **Setup** | CV PDF / your answers | `profile.md` | `vn-it-cv` + interview |
| 1 | **Scope** | `profile.md` Targeting | scan parameters | `question` tool |
| 2 | **Scan** | source + filters | keep-list (Jev-filtered) | `chrome-devtools` MCP + `jev` |
| 3 | **Extract & Score** | each JD `keep` | `jobs/<id>.md` (raw JD) + row in DB | `references/<source>.md` + `jc` |
| 4 | **Tailor CV** | `profile.md` + JD | `cv/<file>.md` (+ `.html`) + `cv_versions` | `vn-it-cv` + `selfcheck_cv.py` |
| 5 | **Apply** | tailored CV | `jobs` row: `status: applied` | **human** — UI / `jc status` |
| 5.5 | **Interview Prep** | `profile.md` + JD + (optional web) | `prep/<job-id>.md` | `references/interview-prep.md` |
| 6 | **Track** | application events | `job_events` + `jobs.status` | **human** — UI / `jc report` |
| 7 | **Offers** | offer details | `offers/<id>.md` + scorecard | scoring vs Targeting |
| 8 | **Onboard & Loop** | accepted offer | checklist + archive | manual + `rg` |

---

## Phase 0 — Setup

Produce `profile.md` (the source of truth). Three ways:

1. **From an existing CV (PDF).** The model cannot read PDFs directly. Extract text first, then fill the profile.
   ```bash
   uv run --quiet --with pypdf python -c "from pypdf import PdfReader; print('\n'.join(p.extract_text() for p in PdfReader('cv.pdf').pages))"
   ```
   (`uv` installs nothing system-wide.) Then map each experience bullet to an `evidence_id` (`e001`, …).
2. **By hand.** `cp profile.example.md profile.md`, replace every `[...]`.
3. **Agent-assisted.** Ask the agent to interview you cluster by cluster: experience → skills (level/years) → targeting (weights, must-have, nice-to-have). It writes the file and marks anything unconfirmed as `[confirm: ...]`.

**Exit criteria:** `profile.md` has Meta + Targeting + ≥1 Experience with evidence ids. Skills with no proving bullet are marked "list only".

**State store (one-time):** `python3 tools/jobcopilot/cli.py init` creates `jobcopilot.db`
(gitignored). It holds lifecycle/identity/run state; `profile.md` and content files
stay as-is. Existing Markdown is imported once with `cli.py import` (see `ROADMAP.md`).

## Phase 1 — Scope

Ask (don't assume): source, keyword/role, level, location/remote, how many pages/items.
Defaults come from `profile.md` Targeting. See `job-hunt` skill Phase 1.

## Phase 2 — Scan

Pick a source reference in `.opencode/skills/job-hunt/references/`:

| Source | Reference | Status |
|---|---|---|
| ITViec | `references/itviec.md` | ✅ verified |
| LinkedIn | `references/linkedin.md` | 🟡 skeleton |
| TopCV | `references/topcv.md` | 🟡 skeleton |
| VietnamWorks | `references/vietnamworks.md` | 🟡 skeleton |
| **Import / paste** | (no reference) | ✅ paste a JD or point to a file |

For board sources: extract a compact list, run one **Jev preview-screen** request to decide which items to open, then open only the keepers.
For **import**: skip the board entirely — paste the JD text or give a file path, go straight to Phase 3.

## Phase 3 — Extract & Score

Parse the JD into structured fields, then score against `profile.md` Targeting:

1. **Must-have gate first.** Violation (fresher-level / on-site in an excluded city / excluded language) → `status: rejected`, `match_score: 0`, log the reason.
2. **`match_score`** = weighted average of the 5 Targeting criteria (0–100). Nice-to-have adds at most +5.
3. **`score_rationale`** = one line auditing the number, e.g. `skill 90 · sen 100 · loc 85 · sal 70 · dom 60 → 83`.
4. `gap_skills[]` = JD skills with no evidence in the profile.
5. **Dedupe + save (DB is the state store):**
   ```bash
   # 1) already known? (exact = auto-block; fuzzy = flag for human confirm)
   python3 tools/jobcopilot/cli.py dedupe-check '<url>' --source <src> --company '<c>' --title '<t>' --location '<l>'
   # 2) write the raw JD to jobs/<id>.md (header: title/company/url, then verbatim JD)
   # 3) register the structured row (score, skills, gaps) — status defaults to saved
   python3 tools/jobcopilot/cli.py add --json '{"id":"<id>","title":"…","company":"…","source":"…","url":"…",
     "location":"…","remote":"…","seniority":"…","match_score":83,"score_rationale":"…",
     "skills_required":[…],"skills_nice":[…],"gap_skills":[…],"run_id":<id>}'
   ```
   `dedupe-check` exact hit → skip. Fuzzy hit → `add` sets `duplicate_of`; a **human
   confirms** on the UI (tier-2 is never auto-skipped). File naming stays
   `jobs/<id>.md`, `id = YYYY-MM-<source>-<company-slug>-<role-slug>`.

## Phase 4 — Tailor CV

Load `vn-it-cv`, run GENERATE with `profile.md` + JD. Constraints: only bullets from the profile, each keeps `<!-- e0xx -->`.

**Pre-tailor gate (EN / international targets):** if the JD is English or remote/international **and**
`profile.md` §1 Meta still has `[confirm: ...]` for Languages or Work authorization → **stop and ask the
user** before generating. These two lines are screened first by overseas employers; a CV missing them is
weak, and the agent must never invent a level.

**Skills rule:** only list skills marked `confirmed: true` in `profile.md` §3. Skills marked
`confirmed: false` (list-only / exploring, e.g. Kafka) **must not** appear in the CV — the self-check
enforces this.

**Mandatory self-check before the CV leaves your machine:**
```bash
python3 .opencode/skills/vn-it-cv/scripts/selfcheck_cv.py cv/<file>.md   # must print ok
python3 .opencode/skills/vn-it-cv/scripts/render_cv.py cv/<file>.md     # md -> print HTML
```
Summary metrics are checked **warn-only** by default (use `--strict-summary` to fail on them).
Then open the `.html` and print to PDF (`Cmd/Ctrl+P` → A4, background graphics on).

## Phase 5 — Apply

A human reviews the PDF and submits. **The agent never auto-applies.** Record it on the UI
or via CLI:
```bash
python3 tools/jobcopilot/cli.py status <id> --to applied \
  --at 2026-10-05 --method portal --followup-at 2026-10-12
```

## Phase 5.5 — Interview Prep

Once a job is `applied` (or later, when a round is scheduled), build `prep/<job-id>.md`
(schema: `prep/_example.md`; guide: `.opencode/skills/job-hunt/references/interview-prep.md`).
It is a **cue card** to review before each round — not a script to memorise, not an answer key.

Four blocks:
1. **JD digest** — must-have vs nice-to-have; the stack the JD *repeats* (what they care about); seniority signals (own/lead/design/mentor); 2–3 core responsibilities `[jd]`.
2. **Company brief** — only from the JD + official pages **if fetched** (`webfetch` / MCP browser); product/business model, size/domain, surfaced stack, values, recent news (with date). Unknown → `[confirm: ...]`, never invented.
3. **Technical prep** — map each JD requirement → `profile.md` evidence (strong/ok/weak) → `[gap: study X]`; likely questions by stack (a cue line, not a written answer); a **STAR story bank** drawn from 3–5 existing profile bullets, each with its `evidence_id`. No new claims, no invented stories.
4. **Non-technical prep** — working process (Agile/review/CI-CD/on-call), problem-solving, communication, teamwork; **3–5 questions to ask them**; logistics.

**Every line is source-tagged:** `[jd]` · `[web: <url>]` · `[profile: e0xx]` · `[guess]` · `[confirm: ...]`.
Web access is opt-in; offline, fill from the JD and mark the rest `[confirm: ...]`.
Update `prep_status` (`draft→ready→done`) and log each round in the "mock round log". Record `prep_ref` on the job.

**Mock interview (optional sub-step).** Say "mock interview" / "phỏng vấn thử" / "quiz me" and the agent plays
interviewer for one round: one question at a time, using only the prep file's questions and the `profile.md`
story bank (it must not invent company facts). It stays in role, gives no answers mid-round, then delivers
per-answer feedback and updates the mock round log. Details + anti-patterns: `references/interview-prep.md`.

## Phase 6 — Track

State lives in the DB; every transition is logged to `job_events` (no frontmatter).
Do it on the UI, or via CLI:

| Event | Write |
|---|---|
| Submitted | `jc status <id> --to applied --at <date> --method … --followup-at <applied+7d>` |
| Response / screen | `jc status <id> --to screen --next-action … --next-action-date …` |
| Tech / on-site | `jc status <id> --to tech` (or `onsite`); build/update `prep/<job-id>.md` |
| Rejected / ghosted | `jc status <id> --to rejected` (`ghosted`) |

Reports come from the DB (CLI or UI dashboard — **no folder scan**):
```bash
python3 tools/jobcopilot/cli.py report        # funnel + backlog + follow-up due
python3 tools/jobcopilot/server.py            # UI: http://127.0.0.1:8765
```
On session start, run `cli.py report`; if `followup_due` is non-empty → the agent flags it.

## Phase 7 — Offers

When an offer lands: create `offers/<id>.md` (schema: `offers/_example.md`) with base/bonus/equity/benefits/level/growth/risk/deadline, and fill the weighted scorecard using your Targeting weights. Set the job's `status: offer`.

## Phase 8 — Onboard & Loop

- **Onboard:** a checklist once you accept (paperwork, equipment, 30/60/90-day goals).
- **Loop:** archive closed applications (`status: closed`), keep `profile.md` as the base for the next hunt. The profile only improves over time.

---

## Error handling

| Problem | Fix |
|---|---|
| `list_pages` shows only `about:blank` / "browser already running" | kill the stale MCP Chrome profile, retry, log in inside the MCP window |
| Logged out mid-scan | detect the login form → ask the user to log in |
| Missing list items | ITViec paginates via `?page=N` (not virtualized) — loop pages, dedupe by link |
| `jev` 401/5xx/timeout | log `jev-error`, fall back to structural keyword filtering, don't block the scan |
| Duplicate JD | `cli.py dedupe-check '<url>'` before writing (exact auto-block, fuzzy → human confirm) |
| DOM changed | prefer parsing `body.innerText` over hard selectors |

## Non-goals (YAGNI)

No auto-apply · **DB/UI đang triển khai từng phần** (state + dedupe + run trong SQLite, xem `ROADMAP.md`; bước 5–6 còn lại) · no bespoke crawler (use the MCP session) · no grounding service (structural constraints + `selfcheck_cv.py`) · **no written interview answer keys** (prep is a cue card) — add only if a real hallucination slips through.
