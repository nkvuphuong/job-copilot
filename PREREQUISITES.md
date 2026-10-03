# Prerequisites

`job-copilot` relies on a few tools. Some live in this repo (shipped); others are
personal/global and you must set them up once.

## Shipped in the repo (nothing to install)

| Component | Location |
|---|---|
| Skill `job-hunt` | `.opencode/skills/job-hunt/` |
| Skill `vn-it-cv` | `.opencode/skills/vn-it-cv/` |
| Scripts | `.opencode/skills/vn-it-cv/scripts/render_cv.py`, `selfcheck_cv.py` |

## Global — set up once

| Component | Where | Notes |
|---|---|---|
| [opencode](https://opencode.ai) | your machine | Run it from inside the repo. |
| MCP `chrome-devtools` | `~/.config/opencode/opencode.json` | Drives a logged-in Chrome to scan boards. |
| Tool `jev` + auth | `~/.config/opencode/tools/jev.ts` | Triage model. Needs `OPENCODE_API_KEY` or `opencode auth login` (OpenCode Zen). |
| Skill `jev-triage` | `~/.config/opencode/skills/jev-triage/` | Primer for `jev`; kept global on purpose. |
| `uv` (optional) | https://docs.astral.sh/uv/ | Only to extract text from a CV PDF without installing anything. |

### Smoke test jev

```bash
node ~/.config/opencode/skills/jev-triage/scripts/smoke.mjs   # expect: SMOKE OK
```

### MCP chrome-devtools

Add it to `~/.config/opencode/opencode.json` and log into the job boards inside the Chrome window it controls. Scanning reuses that session's cookies.

## How to run

`job-hunt` and `vn-it-cv` are **project-local** — opencode only finds them when the
working directory is inside the repo:

```bash
cd ~/path/to/job-copilot
opencode
```

That's it. See [ONBOARDING.md](ONBOARDING.md) for the first-run walkthrough.
