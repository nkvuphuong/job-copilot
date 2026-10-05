# Tasks: DB + UI v1

Spec: `docs/spec-db-ui.md` · Plan: `tasks/plan.md`

## T1: Schema + identity (nền tảng) ✅
**Files:** `tools/jobcopilot/db.py`, `tools/jobcopilot/identity.py`, `tools/jobcopilot/cli.py` (selfcheck)
- [x] `db.py`: `connect()`, `init_schema()`, 5 bảng + index (gồm UNIQUE `cv_versions(job_id,path)`).
- [x] `identity.py`: `url_canonical`, `title_norm`, `company_slug`, `dedupe_key`, `extract_external_id`, `find_duplicates` (tier1 exact + tier2 fuzzy).
- [x] selfcheck trong `cli.py`.

**Verify:** `init` + `selfcheck` → `SELFCHECK OK`. ✅

## T2: Migrate từ markdown ✅
**Files:** `tools/jobcopilot/migrate.py`
- [x] Parse frontmatter → row `jobs`; backup → `jobs/.backup/`; strip → header title/company/url + raw JD.
- [x] Link `cv_versions` từ `cv_version` + dò file `cv/<...>`.
- [x] Idempotent (đã sửa bug nhân đôi `cv_versions`).

**Verify:** 13 jobs, 13 cv_versions, chạy 2 lần không đổi, raw JD còn nguyên. ✅

## CP-A — Checkpoint ✅
- [x] `init` + `import` ×2 ổn, selfcheck pass, không mất raw JD.

## T3: CLI (đường agent) ✅
**Files:** `tools/jobcopilot/cli.py`
- [x] `init` · `import` · `dedupe-check` · `add --json` · `run start|finish` · `status` · `report` · `selfcheck`.
- [x] `status` ghi `job_events` + update `jobs.status,updated_at`.
- [x] `report`: funnel, backlog (`applied_at IS NULL`), follow-up due ≤ today.

**Verify:** exact/fuzzy dedupe đúng, `add` gắn `duplicate_of`, status sinh event, report đúng. ✅

## T4: UI (đường người dùng) ✅
**Files:** `tools/jobcopilot/server.py`, `tools/jobcopilot/ui/index.html`
- [x] server tự `init` nếu DB thiếu; port 8765 (`--port`), JSON API gọi `db.py`; connection per-request (thread-safe).
- [x] UI: dashboard (funnel + follow-up due), filter (status/source/seniority), đổi status, clear `duplicate_of`.

**Verify:** smoke trên bản copy DB: report/jobs/filter/post status/dup/404 OK; DB thật không đổi. ✅

## CP-B — Checkpoint ✅
- [x] dedupe đúng; status → `job_events`; UI smoke pass.

## T5: Rewire skill + workflow ✅
**Files:** `.opencode/skills/job-hunt/SKILL.md`, `WORKFLOW.md`
- [x] Phase 2/3/5/6: dedupe/state/track → `cli.py` (DB); bỏ `rg` frontmatter.
- [x] Non-goals: bỏ "no DB/UI", trỏ `ROADMAP.md`; prep_ref chú thích hoãn sang B5.

**Verify:** không còn `rg --no-ignore` cho state; chỉ còn `frontmatter` ở chú thích "no frontmatter". ✅

## T6: Docs + gitignore ✅
**Files:** `AGENTS.md`, `README.md`, `.gitignore`, `ROADMAP.md`
- [x] `.gitignore` += `jobcopilot.db`, `jobs/.backup/`.
- [x] `README.md` quickstart + bảng path + privacy.
- [x] `AGENTS.md` thêm mục "State store".

**Verify:** `git check-ignore jobcopilot.db jobs/.backup/x.md` → in đường dẫn. ✅

## CP-C — Done
- [x] Success Criteria trong `docs/spec-db-ui.md` đạt (xem `code-review-and-quality`).
- [ ] Chạy `code-review-and-quality` trước khi báo hoàn thành. ← đang chạy
