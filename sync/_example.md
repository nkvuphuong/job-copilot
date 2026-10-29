# <Platform> — profile pack (example)

> Copy of the real shape. The agent writes one of these per platform to
> `sync/<platform>.md`, which is **gitignored** — packs hold your real profile
> text. Only this example is committed.
> Gate before finishing: `python3 .opencode/skills/profile-sync/scripts/pack_check.py`

## Headline  <!-- limit: 130 -->
```text
I build <thing> · <stack> · <what you are hired for>
```

Evidence: e001, e004

## About  <!-- limit: 2600 -->
```text
<Problem you solve. What you own. Where you have done it.
No company names here — that is the Experience section's job.>
```

Evidence: e002, e009

## Highlights — Acme Corp · Senior Engineer (MM/YYYY – MM/YYYY)  <!-- limit: 2000 -->
```text
<One line of context: industry · stack>

• <Event + mechanism + result — the numbers live here, not in Headline/About.>
• <Second event.>
```

Evidence: e007, e011

## Notes

- The fenced block is the **verbatim paste** — never put `[eNNN]` markers inside it.
  The `Evidence:` line below each block is for traceability and is not pasted.
- `<!-- limit: N -->` only when the platform limit is known; omit it otherwise
  (the block is then not length-checked).
- `<platform>.before.md` = snapshot of the live profile taken before editing, so
  it can be restored. It is skipped by `pack_check`.
