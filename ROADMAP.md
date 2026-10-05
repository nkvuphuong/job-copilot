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

Mục tiêu: đưa các bảng đã khai báo sẵn (`cv_versions`, `prep`, `prep_rounds`,
`offers`) vào dùng thật, thay vì chỉ ghi file như v1.

- **Schema cần thêm:** `prep` (job_id, path, prep_status), `prep_rounds` (prep_id,
  round_type, at, notes), `offers` (job_id, base, bonus, equity, benefits_json,
  level, deadline, score_json, status, path).
- **CLI cần thêm:** `cv-version add/list`, `prep open|status`, `prep round-log`,
  `offer add|score`.
- **UI cần thêm:** tab Prep (cue card link + prep_status + mock log), tab Offers
  (scorecard + deadline + decision), CV version list theo job.
- **Acceptance:** tạo prep cho 1 job → `prep_status` đổi được trên UI; log 1 mock
  round → lưu `prep_rounds`; tạo offer → scorecard tính theo trọng số Targeting
  trong `profile.md`.
- **Phụ thuộc:** v1 xong (DB + UI chạy).

### B6. Onboard checklist + archive + Loop

- **UI:** checklist onboarding (giấy tờ, thiết bị, mục tiêu 30/60/90 ngày);
  archive job `closed`.
- **Acceptance:** đánh dấu accepted offer → sinh checklist; archive không xoá
  dữ liệu, chỉ đổi `status: closed`.

### B7. Export / backup DB

- Lệnh `cli.py export` (JSON/markdown) và `cli.py backup`.
- Acceptance: export ra JSON round-trip được (import lại không mất state).

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
