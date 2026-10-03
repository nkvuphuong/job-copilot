# Profile — Source of Truth (TEMPLATE)

> **Rule of gold:** everything in a tailored CV MUST trace back to an entry in this file.
> No `evidence_id` → it must not appear in a CV. Never invent, never overstate.
> Update this file FIRST, then regenerate CVs.
>
> **How to get here:**
> - **From an existing CV (PDF):** extract text, then fill this file. See `ONBOARDING.md`.
> - **By hand:** replace every `[...]` below.
> - **Agent-assisted:** ask the agent to interview you cluster by cluster (experience, skill levels, targeting).
>
> Rename this file to `profile.md` (it is gitignored, stays private).

---

## 1. Meta

- **Name:** [Full name]
- **Title:** [Primary title, e.g. Full-Stack Developer]
- **Contact:** [phone] · [email] · [city] · [linkedin.com/in/...]
- **GitHub:** [https://github.com/username or leave blank]
- **Experience:** [N+ years]
- **Languages:** [e.g. Vietnamese (native), English (professional)]
- **Work authorization:** [e.g. citizen / needs sponsorship for remote abroad]
- **Target roles:** [e.g. Senior/Lead Full-stack (backend-heavy), Backend Engineer]

## 2. Targeting — matching criteria for the scanner

> Suggest based on your profile; tune freely. The scanner scores JDs against this table.

| Criterion | Weight | Notes |
|---|---|---|
| Skill/stack match | high | [e.g. PHP/Laravel, Python, MySQL, Redis, AWS; learning Golang/Kafka] |
| Seniority | high | [e.g. Senior / Lead (N+ years)] |
| Location / remote | medium | [e.g. HCM; hybrid/remote OK; remote abroad optional] |
| Salary | medium | [e.g. Senior ≥ $X gross · Lead ≥ $Y gross] |
| Company type / domain | low | [e.g. prefer product/SaaS/fintech over outsourcing] |

**Must-have** (violation → reject, no scoring needed):
- [e.g. not a fresher-level role (Senior/Lead minimum)]
- [e.g. no on-site in another city]
- [e.g. no Japanese/Korean/Chinese language requirement]

**Nice-to-have** (bonus points, not a filter): [e.g. hybrid/remote · product company · international remote]

## 3. Skills

> Leave `level`/`years` for yourself to confirm (never invent). `evidence` points to a bullet in Experience.
> Skills marked "list only" have no proving bullet — the CV rule only lets them in with your explicit confirmation.

| id | skill | group | level | years | evidence |
|---|---|---|---|---|---|
| s1 | [e.g. PHP / Laravel] | backend |  |  | e001, e002 |
| s2 | [e.g. Python] | backend |  |  | e003 |
| s3 | [e.g. MySQL] | database |  |  | _list only — confirm a project_ |

## 4. Experiences

> One block per company. Bullets get a stable `**[e0xx]**` id. Numbers must be real.

### [Company] — [Title] ([start] → [end])
_[one-line context: product/domain, team size, market]_

**[Title] · [start]–[end]**
- **[e001]** [Action verb + what you did + tech + measurable result].
- **[e002]** [...]
- **Stack:** [tech used across this company]

### [Company 2] — [Title] ([start] → [end])
_[context]_
- **[e003]** [...]
- **Stack:** [...]

## 5. Projects

_(Projects already attached to Experience bullets; split out here when you want to spotlight one for a specific JD. Use `e1xx` ids.)_

## 6. Education / Certifications

- **[University]** — [Major], [years] · [degree(s)]

---

## `evidence_id` conventions

- `e0xx` for experiences, `e1xx` for projects (never reuse or renumber).
- In a tailored CV, each bullet keeps a comment `<!-- e001 -->` next to it for tracing.
- De-emphasize (drop / shorten) is a valid choice; **never change dates or titles**.
- A skill with no proving bullet (marked "list only") → weigh carefully when tailoring, never add context you can't back.
