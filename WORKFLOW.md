# Workflow

The fixed pipeline. Each phase has an input, an output, and the tool/skill that runs it.
Data flows left to right; you can jump in at any phase.

```
0 Setup ─▶ 1 Scope ─▶ 2 Scan ─▶ 3 Extract & Score ─▶ 4 Tailor CV ─▶ 5 Apply ─▶ 6 Track ─▶ 7 Offers ─▶ 8 Onboard
                                                                                                        │
                                                                        ◀────────────── Loop ────────────┘
```

| # | Phase | Input | Output | Tool / skill |
|---|---|---|---|---|
| 0 | **Setup** | CV PDF / your answers | `profile.md` | `vn-it-cv` + interview |
| 1 | **Scope** | `profile.md` Targeting | scan parameters | `question` tool |
| 2 | **Scan** | source + filters | keep-list (Jev-filtered) | `chrome-devtools` MCP + `jev` |
| 3 | **Extract & Score** | each JD `keep` | `jobs/<id>.md` | `references/<source>.md` |
| 4 | **Tailor CV** | `profile.md` + JD | `cv/<file>.md` (+ `.html`) | `vn-it-cv` + `selfcheck_cv.py` |
| 5 | **Apply** | tailored CV | `status: applied` | **human** (no auto-apply) |
| 6 | **Track** | application events | frontmatter updates | `rg` reports |
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
5. Save to `jobs/YYYY-MM-<source>-<company-slug>-<role-slug>.md` (schema: `jobs/_example.md`), after dedupe (`rg --no-ignore -l '<url>' jobs/`).

## Phase 4 — Tailor CV

Load `vn-it-cv`, run GENERATE with `profile.md` + JD. Constraints: only bullets from the profile, each keeps `<!-- e0xx -->`.

**Mandatory self-check before the CV leaves your machine:**
```bash
python3 .opencode/skills/vn-it-cv/scripts/selfcheck_cv.py cv/<file>.md   # must print ok
python3 .opencode/skills/vn-it-cv/scripts/render_cv.py cv/<file>.md     # md -> print HTML
```
Then open the `.html` and print to PDF (`Cmd/Ctrl+P` → A4, background graphics on).

## Phase 5 — Apply

A human reviews the PDF and submits. **The agent never auto-applies.** Record `apply_method`.

## Phase 6 — Track

Log every event in the job frontmatter (no separate event file):

| Event | Write |
|---|---|
| Submitted | `status: applied`, `applied_at: <date>`, `apply_method: …`, `followup_at: <applied_at + 7d>` |
| Response / screen | `status: screen`, update `next_action` + `next_action_date` |
| Tech / on-site | `status: tech` / `onsite`, `next_action` = what to prepare |
| Rejected / ghosted | `status: rejected` / `ghosted`, clear `next_action` |

Reports (plain `rg`):
```bash
rg --no-ignore --no-filename -o '^status: \w+' jobs/ | sort | uniq -c   # funnel
rg --no-ignore -l '^applied_at: ""' jobs/ | wc -l                       # backlog (not yet applied)
rg --no-ignore -l '^followup_at: 2026-01' jobs/                         # follow-ups this month
rg --no-ignore -l '^referral: true' jobs/                               # referred applications
```
On session start, if any `followup_at` ≤ today and status unchanged → the agent flags it.

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
| Duplicate JD | `rg --no-ignore -l '<url>' jobs/` before writing |
| DOM changed | prefer parsing `body.innerText` over hard selectors |

## Non-goals (YAGNI)

No auto-apply · no DB/UI (Markdown + `rg`) · no bespoke crawler (use the MCP session) · no grounding service (structural constraints + `selfcheck_cv.py`) — add only if a real hallucination slips through.
