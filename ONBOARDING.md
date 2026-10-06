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

Then run the checks yourself to be sure:

```bash
python3 .opencode/skills/vn-it-cv/scripts/selfcheck_cv.py cv/<file>.md   # honesty gate
python3 .opencode/skills/vn-it-cv/scripts/ats_check.py cv/<file>.md      # ATS fields/structure
python3 .opencode/skills/vn-it-cv/scripts/export_cv.py cv/<file>.md      # -> cv/<file>.pdf
```

Review the PDF. Submit it yourself.

## 7. Prepare for the interview

Once you've applied (or a round is booked):

> "Prep me for the <job> interview."

The agent builds `prep/<job-id>.md` — a cue card with a JD digest, a company brief, technical gaps + likely questions, and non-technical questions to expect. Company facts are source-tagged (`[jd]` / `[web]` / `[confirm]`); nothing is invented. Review it, add your own notes, then practise:

> "Mock interview me for the <job> — tech round, 30 min."

The agent asks one question at a time, stays in role, and gives feedback at the end.

## 8. Keep it running

After each application: "I applied to <job> — log it." Follow the funnel in [WORKFLOW.md](WORKFLOW.md) Phase 6.

## Troubleshooting

- **Skills not found** → you're not running opencode from inside the repo.
- **`selfcheck_cv.py` fails** → a CV references an unknown `e0xx`, claims a skill not backed by an evidence bullet / `confirmed: true` skill in `profile.md`, puts an unbacked tech in a `**Tech:**` line, or leaks a placeholder into the header. Fix the CV, not the check (or add real evidence to `profile.md` first).
- **`ats_check.py` fails** → missing email/phone/profile URL, sections out of order, a role heading without an `MM/YYYY` date, or a header placeholder. Fix the CV.
- **Scraper returns nothing** → the site's DOM changed; update the matching `references/<source>.md`.
