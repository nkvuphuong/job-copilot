# Agent Skills — job-copilot

This repo is a job-hunt pipeline, not an application codebase. Its own skills
(`job-hunt`, `vn-it-cv`) live in `.opencode/skills/` and are the primary
routing targets. General software-development skills are installed globally in
`~/.config/opencode/skills/`.

If a task matches a skill, invoke it with the `skill` tool before acting.

## Intent → Skill

Job-search (prefer the project-local skills):

- Profile setup / update → `job-hunt` (+ `vn-it-cv` for CV work)
- Scan / triage / score jobs → `job-hunt`
- Tailor / review / score a CV → `vn-it-cv`
- Interview prep / mock → `job-hunt`
- Track applications / compare offers → `job-hunt`

## State store (do not re-invent)

Job lifecycle, identity/dedupe and scan runs live in `jobcopilot.db` (SQLite),
not in Markdown frontmatter. The CLI/UI is the single write path:

- `python3 tools/jobcopilot/cli.py dedupe-check|add|status|report` — agent + human
- `python3 tools/jobcopilot/server.py` — local UI at `http://127.0.0.1:8765`

Content (raw JD, CV, prep, offer, `profile.md`) stays in files; the agent owns it,
the DB owns state. Never edit `jobcopilot.db` by hand and never store lifecycle in
`jobs/*.md`. Spec: `docs/spec-db-ui.md`; deferred work: `ROADMAP.md`.

Repo code, scripts & docs (only when editing this repo itself):

- Bug / failure in scripts → `debugging-and-error-recovery`
- Review / refactor Python or skill files → `code-review-and-quality`, `code-simplification`
- New tooling → `planning-and-task-breakdown`, `test-driven-development`
- Docs / ADRs → `documentation-and-adrs`

## Boundaries

- Job-search requests are content work: do NOT impose software lifecycle gates
  (spec, TDD, CI) on them.
- Dev skills apply only to changes in this repo's own code, scripts and docs.
- `profile.md` is the single source of truth; never invent experience. Tailored
  CVs keep their `<!-- eNNN -->` evidence trace; run
  `vn-it-cv/scripts/selfcheck_cv.py` + `vn-it-cv/scripts/ats_check.py` before finishing.
