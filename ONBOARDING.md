# Onboarding — first run

Get from `git clone` to your first tailored CV in ~15 minutes.

## 1. Prereqs

Install and verify the tools in [PREREQUISITES.md](PREREQUISITES.md): opencode, the `chrome-devtools` MCP, and `jev`. Run the jev smoke test once.

## 2. Run opencode from inside the repo

The skills are project-local, so this matters:

```bash
cd job-copilot
opencode
```

## 3. Build your profile

```bash
cp profile.example.md profile.md
```

Pick one path and tell the agent:

- **You have a CV PDF:** "Set up profile.md from /path/to/cv.pdf"
  The agent extracts text (via `uv`/`pypdf`), drafts the profile, and asks you to confirm skill levels, salary range, must-have/nice-to-have.
- **Blank start:** "Help me fill profile.md — interview me."
- **You'll do it yourself:** edit `profile.md`, replacing every `[...]`, and give each experience bullet an `e0xx` id.

**Do not skip:** Targeted weights, must-have list, and salary floor. Scoring and rejecting depend on them.

## 4. Smoke test the pipeline

The cheapest source is a pasted JD (no login, no scraper):

> "Here's a JD, score it against my profile and save it."
> [paste a job description]

You should get a `jobs/…md` file with a `match_score` and a `score_rationale`.

## 5. First scan from a board

Log into the board in the MCP-controlled Chrome window, then:

> "Scan ITViec for <role> in <city>, 2 pages."

Verify the watch-outs in `.opencode/skills/job-hunt/references/itviec.md` still hold (sites change).

## 6. First tailored CV

> "Tailor a CV for <job id>."

Then run the two scripts yourself to be sure:

```bash
python3 .opencode/skills/vn-it-cv/scripts/selfcheck_cv.py cv/<file>.md
python3 .opencode/skills/vn-it-cv/scripts/render_cv.py cv/<file>.md
```

Open the `.html`, print to PDF (A4). Review it. Submit it yourself.

## 7. Keep it running

After each application: "I applied to <job> — log it." Follow the funnel in [WORKFLOW.md](WORKFLOW.md) Phase 6.

## Troubleshooting

- **Skills not found** → you're not running opencode from inside the repo.
- **`selfcheck_cv.py` fails** → a CV references an unknown `e0xx` or claims a skill absent from `profile.md`. Fix the CV, not the check.
- **Scraper returns nothing** → the site's DOM changed; update the matching `references/<source>.md`.
