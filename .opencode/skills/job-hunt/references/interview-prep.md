# Interview Prep — reference (how to build `prep/<job-id>.md`)

Interview Prep turns a JD + a bit of company research into a **cue card** the candidate
reviews before each round. It is **not** a script to memorise and **not** an answer key —
it is a structured reminder so nothing important is forgotten in the room.

Output: `prep/<job-id>.md` (schema: `prep/_example.md`). One file per job.

## The honesty rule (non-negotiable)

Every line in the prep file carries a source tag:

| Tag | Meaning |
|---|---|
| `[jd]` | stated in the job description |
| `[web: <url>]` | read from that URL (fetched during prep) |
| `[profile: e0xx]` | backed by your evidence in `profile.md` |
| `[guess]` | an inference — must be verified before you rely on it |
| `[confirm: ...]` | needs the candidate's input |

**Never state a company fact you did not read.** If the company website is not fetched,
the brief says `[confirm: check acme.com/about]`, not an invented "fast-growing startup".
This mirrors the CV rule: the same anti-hallucination discipline, applied to prep.

## Building it — 4 blocks

### 1. JD digest
- Separate **must-have** from **nice-to-have** (the gate that scoring already used).
- List **stack emphasis**: a technology the JD repeats or names first is what they care about.
- Note **seniority signals**: words like "own", "lead", "design", "mentor" tell you the level of autonomy expected.
- Pull 2–3 core responsibilities verbatim `[jd]`.

### 2. Company brief
- Source = JD + official site / LinkedIn page, **only if fetched** (`webfetch` / the MCP browser).
- Cover: product & business model, size/domain/market, tech stack surfaced, values, recent news/reviews (with date).
- End with **open questions** — gaps you could not verify `[confirm: ...]`. Those gaps become questions to ask the interviewer.

### 3. Technical prep
- **Gap plan:** map each JD requirement → `profile.md` evidence → strong/ok/weak. Weak ones get a `[gap: study X]` checkbox.
- **Likely questions by stack:** for each emphasised stack item, one line "why they'll ask" + a cue + which project to cite. Cue = reminder, **not** a written answer.
- **STAR story bank:** pick 3–5 existing profile bullets and lay them out as Situation/Task/Action/Result + `evidence_id`. Never invent a story. This is the *only* place prep reuses CV-style evidence tracing.

### 4. Non-technical prep
- Working process (Agile/Scrum, code review, CI/CD, on-call) — their stated process `[jd]` vs your experience `[profile: e0xx]`.
- Problem-solving approach, communication/presenting, teamwork/feedback — each as a one-line cue.
- **Your questions for them** (3–5): team shape, on-call, tech debt, growth path, what success looks like in 6 months.
- Logistics: format, duration, interviewers, what to bring / whether there's a live-coding or take-home.

## Rules of use

1. **Cue card, not teleprompter.** Do not write full answers; write reminders. Reading a script in an interview is worse than a short honest gap.
2. **No new claims.** Technical prep never adds a skill that isn't in `profile.md` — same guardrail as the CV.
3. **Update per round.** After each round, log it in the "Mock round log" and refine. `prep_status`: `draft` → `ready` → `done`.
4. **Offline-safe.** Without web access, fill the company brief from the JD alone and mark the rest `[confirm: ...]`. Never fill the gap with a guess.
5. **Agent may quiz you.** If asked, the agent can run a mock round (below) using only the questions in the file and the `profile.md` story bank — but it must not invent facts about the company either.

## Mock interview (optional sub-step)

When the candidate says "mock interview", "phỏng vấn thử", "quiz me", or "đóng vai interviewer" for job X:

**Setup.** Read `prep/<job-id>.md`. Confirm the round type (screen / tech / manager) and length. Default: tech, 30–45 min.

**Rules the agent MUST follow:**
1. **One question at a time.** Ask, then stop and wait for the candidate's answer. Never dump a list.
2. **Only sources allowed:** questions in the prep file (section 3 "Likely questions" + section 4) and the `profile.md` story bank. **Do not invent company facts** or stack the JD didn't mention.
3. **No answers given during the round.** If asked for the answer mid-round, defer: "I'll give feedback at the end."
4. **Be a realistic, polite interviewer** — not a host. Follow up once on a weak answer, then move on.
5. **Stay in role** until the candidate says "stop" / "end mock".

**Round shape (default tech):**
- Warm-up (1–2 min): intro / "tell me about yourself" (from prep §3 story bank).
- Technical (bulk): 4–6 questions from prep §3, progressing easy → hard, each tied to a JD skill.
- Behavioral (2–3): STAR prompts from prep §3 (ownership, conflict, failure, mentoring).
- Candidate questions (2–3 min): "what would you like to ask us?" — evaluate the prep §4 list.
- Close.

**Feedback (after the candidate says stop/end).** Give, per answer: what was strong, what was vague, and **one concrete fix** (which story to use, which gap to study). Then:
- Update the `prep/<job-id>.md` "Mock round log" table (date, round, what went well, what to fix).
- If a gap surfaced, add it to the §3 gap plan as `[gap: ...]`.
- Do **not** rewrite the candidate's answers into a script — the point is practice, not memorising.

**Anti-patterns for the mock:** asking 10 questions at once · revealing the answer mid-round · inventing a "the interviewer will definitely ask about X" claim · grading the candidate's skill level (you are not the employer).

## Anti-patterns (prep overall)

- ❌ A "company brief" full of plausible-but-unverified claims.
- ❌ Writing complete STAR answers to memorise.
- ❌ Listing skills in technical prep that aren't in `profile.md`.
- ❌ Skipping the "my questions for them" block — asking good questions is part of the interview.
