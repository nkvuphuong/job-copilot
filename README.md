# job-copilot

A repeatable, **honest** job-hunt pipeline that runs inside [opencode](https://opencode.ai): scan job boards → triage → score against your profile → tailor a truthful CV per JD → track applications → compare offers → onboard.

It is **not** an auto-apply bot. A human reviews and submits every application. The value is a controlled pipeline and a CV that never lies.

## The idea in one line

`Setup → Scope → Scan → Extract & Score → Tailor CV → Apply → Interview Prep → Track → Offers → Onboard → Loop`

Full detail: **[WORKFLOW.md](WORKFLOW.md)**.

## What's in the repo

| Path | What it is | Shared? |
|---|---|---|
| `.opencode/skills/job-hunt/` | Orchestration skill (the pipeline) + per-source references | ✅ |
| `.opencode/skills/vn-it-cv/` | CV generate/review/score skill + templates + scripts | ✅ |
| `profile.example.md` | Template for your source-of-truth profile | ✅ |
| `jobs/_example.md` | Job-posting schema (frontmatter + raw JD) | ✅ |
| `cv/_example-en.md` | Tailored-CV shape (with `<!-- e001 -->` trace) | ✅ |
| `offers/_example.md` | Offer-comparison schema | ✅ |
| `prep/_example.md` | Interview-prep cue card (JD digest + company brief + tech/non-tech) | ✅ |
| `WORKFLOW.md` / `ONBOARDING.md` / `PREREQUISITES.md` | Docs | ✅ |
| `profile.md`, `jobs/*`, `cv/*`, `offers/*`, `prep/*` | **Your personal data** | ❌ gitignored |

Your data stays local. Cloning the repo gives you the tool; you bring your own profile.

## Quickstart

```bash
git clone <this repo> job-copilot
cd job-copilot
cp profile.example.md profile.md     # then fill it (see ONBOARDING.md)
opencode                             # run opencode from inside the repo
```

Then, in opencode, just talk:
- "set up my profile from this CV: /path/to/cv.pdf"
- "scan ITViec for senior backend in HCMC, 3 pages"
- "tailor a CV for that Rakus job"
- "I applied to Rakus — log it"
- "prep me for the Acme interview"

The `job-hunt` and `vn-it-cv` skills are project-local, so **you must run opencode from inside the repo**.

## Prerequisites

See **[PREREQUISITES.md](PREREQUISITES.md)** — opencode, the `chrome-devtools` MCP, and the `jev` tool for triage.

## The honesty guarantee

- `profile.md` is the single source of truth; every experience bullet has a stable `evidence_id`.
- A tailored CV may only **select / reorder / reword** — never invent. Every bullet keeps its `<!-- e001 -->` trace.
- `scripts/selfcheck_cv.py` fails if a CV references an unknown evidence id **or** claims a skill not backed by `profile.md`.
- No auto-apply. Ever.

## License

MIT.
