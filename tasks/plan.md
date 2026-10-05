# Implementation Plan: DB + UI quản lý state (v1)

Spec: [`../docs/spec-db-ui.md`](../docs/spec-db-ui.md). Tasks: [`todo.md`](todo.md).

## Overview

Thêm DB SQLite + CLI + UI local làm nguồn sự thật cho lifecycle/identity/run,
giữ file làm nơi chứa nội dung. v1 = bước 1–4. Bước 5–6 ở `ROADMAP.md`.

## Architecture Decisions

- **Python stdlib thuần** (sqlite3/argparse/http.server), 0 dep. Seam: `db.py` thuần → đổi `server.py` sang framework sau nếu cần.
- **Một cửa ghi state:** CLI và server đều gọi `db.py`; không dual-write.
- **Dedupe 2 tầng:** exact (source+external_id / url_canonical) auto-block; fuzzy gom `duplicate_of`, người xác nhận.
- **Migrate idempotent**, strip frontmatter, để lại header hiển thị title/company/url.
- **No Docker v1**; không bao giờ bake DB/data vào repo.

## Task List (chi tiết ở `todo.md`)

### Phase 1: Foundation
- [ ] T1: `db.py` schema + CRUD + `identity.py` + selfcheck
- [ ] T2: `migrate.py` import jobs + cv_versions, strip frontmatter

### Checkpoint A (sau T1–T2)
- [ ] `init` tạo DB, import chạy 2 lần số row không đổi, selfcheck pass

### Phase 2: Agent path
- [ ] T3: `cli.py` (init/import/dedupe-check/add/run/status/report/selfcheck)

### Phase 3: Human path
- [ ] T4: `server.py` + `ui/index.html` (dashboard, list/filter, đổi status, confirm duplicate)

### Checkpoint B (sau T3–T4)
- [ ] dedupe-check chặn đúng; status ghi `job_events`; UI smoke pass

### Phase 4: Wire + docs
- [ ] T5: Rewire `job-hunt/SKILL.md` + `WORKFLOW.md` sang DB
- [ ] T6: `AGENTS.md`, `README.md`, `.gitignore`, `ROADMAP.md` cập nhật

### Checkpoint C — Done
- [ ] Toàn bộ Success Criteria trong spec đạt

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Strip frontmatter làm mất dữ liệu job | High | T2 backup `jobs/*.md` → `jobs/.backup/` trước khi ghi; verify row count trước khi strip |
| `import` chạy 2 lần nhân đôi | Med | upsert theo `id` (PK) + `INSERT OR REPLACE`; test idempotency |
| Dedupe fuzzy bắt nhầm | Med | không auto-skip tier-2, chỉ set `duplicate_of` |
| SQLite mở đồng thời | Low | 1 tiến trình local; `PRAGMA foreign_keys=ON` |

## Open Questions

Không còn (port 8765, header title/company/url, first_run_id NULL đã chốt).
