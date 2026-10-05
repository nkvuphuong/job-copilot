# Roadmap

Trạng thái: **v1 (bước 1–4) đang triển khai** — DB SQLite + CLI + migrate + UI state.
Spec: [`docs/spec-db-ui.md`](docs/spec-db-ui.md).

Mục đích file này: giữ các bước **cố tình hoãn** với đủ ngữ cảnh để nhặt lên làm
tiếp mà không phải nhớ. Mỗi mục có acceptance criteria riêng.

## Đang làm — v1

- [ ] `tools/jobcopilot/db.py` + `identity.py` + schema (5 bảng)
- [ ] `migrate.py`: import `jobs/*.md` frontmatter → DB, strip frontmatter
- [ ] `cli.py`: `init` / `import` / `dedupe-check` / `add` / `run` / `status` / `report`
- [ ] `server.py` + `ui/index.html`: dashboard + list/filter + đổi state + confirm duplicate
- [ ] Rewire `job-hunt/SKILL.md` (Phase 2,3,5,6) + `WORKFLOW.md` (Phase 2,3,5,6 + Non-goals) sang DB
- [ ] Cập nhật `AGENTS.md`, `README.md`, `.gitignore` (+`jobcopilot.db`)

## Backlog (bước 5–6) — chưa làm

### B5. cv_versions / prep / offers vào DB + UI

**B5.1 — prep ✅ xong** (spec: `docs/spec-db-ui.md` mục "Phase B5.1"):
bảng `prep` + `prep_rounds`, CLI `prep open|status|round-add|show|list`,
UI drawer khối Interview Prep (đổi `prep_status`, log round, xem cue card),
API `GET /api/prep/<job_id>` + `POST /api/jobs/<id>/prep|prep-round`. E2E phủ.
`stage` derive thêm mốc `prep`.

**UI v1.2 — Việt hoá + render HTML ✅ xong:**
UI nhãn tiếng Việt; file nội dung (.md) hiển thị qua HTML render on-the-fly
(`tools/jobcopilot/render.py`, endpoint `?format=html` cho CV/prep/JD) mở ở tab
mới — `.md` vẫn phục vụ agent (mặc định). Chip giai đoạn dịch nhãn (giữ giá trị gốc).

**B5.2 — offers (chưa làm):**

- **Schema cần thêm:** `offers` (job_id, base, bonus, equity, benefits_json,
  level, deadline, score_json, status, path).
- **CLI cần thêm:** `offer add|score`.
- **UI cần thêm:** tab Offers (scorecard + deadline + decision).
- **Acceptance:** tạo offer → scorecard tính theo trọng số Targeting trong `profile.md`.
- **Phụ thuộc:** B5.1 xong.

### B6. Onboard checklist + archive + Loop

- **UI:** checklist onboarding (giấy tờ, thiết bị, mục tiêu 30/60/90 ngày);
  archive job `closed`.
- **Acceptance:** đánh dấu accepted offer → sinh checklist; archive không xoá
  dữ liệu, chỉ đổi `status: closed`.

### B7. Export / backup DB ✅ xong

- `cli.py export --format json|csv|md [--out]`: json round-trip được;
  csv = 1 `.zip` mỗi bảng 1 file (`_meta.json` kèm counts); md = funnel + bảng job.
- `cli.py restore --in <json> [--into <db>]` — `INSERT OR REPLACE` theo thứ tự FK,
  chỉ ghi DB, không đụng `jobs/*.md`. Acceptance đạt: restore → report + row count
  mọi bảng khớp.
- `cli.py backup [--out]` — `sqlite3.backup()` online (an toàn khi DB đang mở).
- E2E P5b phủ. `SCHEMA_VERSION` trong `db.py`.

## Ghi chú kiến trúc — Docker / chia sẻ repo

- **v1: KHÔNG Docker.** Tool phải chạy cùng máy với opencode agent (đọc/ghi file
  repo) và phụ thuộc `chrome-devtools` MCP + `jev` trên host; SQLite mở đồng thời
  từ host và container = lock/path hazard. Python stdlib 0-dep → setup đã là
  `git clone` + `python3`, Docker không cắt được friction nào thật.
- **Nguyên tắc dữ liệu (áp dụng cả khi có Docker):** code/templates/docs mới được
  đóng gói; `profile.md`, `jobs/*`, `cv/*`, `prep/*`, `offers/*`, `jobcopilot.db`
  là dữ liệu cá nhân — gitignored, sinh lại bằng `init` + `import`, **không bao
  giờ bake vào image/repo**.
- **Khi nào mới cân nhắc Docker:** nếu cần **hosted / multi-user** (deploy UI lên
  server). Lúc đó container hóa `server.py` + DB, data mount volume; tách khỏi
  đường chạy local của agent.
