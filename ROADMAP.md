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

## Backlog (bước 5–8) — chưa làm

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

### B8. Market research → GAP → learning roadmap

**Mục tiêu:** khảo sát thị trường theo **tiêu chí người dùng định nghĩa** → so/đối chiếu với
`profile.md` → xác định **GAP** kỹ năng & kiến thức → đề xuất **lộ trình phát triển**. Ưu tiên
roadmap **có sẵn trên roadmap.sh**; nếu không có → dùng tính năng **"Learn with AI" của roadmap.sh**
hoặc **lộ trình nội bộ tự thiết kế**.

**Skill mới:** `.opencode/skills/market-research/` (tách khỏi `job-hunt`).

**B8.1 — Tổng hợp + snapshot (chưa làm):**
- **Schema:** `market_snapshots` (id, created_at, criteria_json, counts_json,
  top_skills_json, salary_json, run_ids_json).
- **CLI:** `jc market scan --criteria '<json>'` (aggregate từ `jobs` đã scan, hoặc chạy scan N JD),
  `jc market report [--snapshot <id>]`.
- **Acceptance:** 1 tiêu chí → snapshot có top-skill (required/nice, %), salary band, seniority & remote ratio.

**B8.2 — GAP vs profile (chưa làm):**
- **CLI:** `jc gap [--snapshot <id>] [--target <role>]` — diff skill demanded vs `profile.md` §3
  (`confirmed:false` / `exploring` / thiếu hẳn) + level gap.
- **Acceptance:** liệt kê đúng skill thiếu; mỗi gap gắn % xuất hiện trên thị trường.

**B8.3 — Lộ trình (chưa làm):**
- Map gap → roadmap.sh: fetch **read-only** `github.com/kamranahmedse/developer-roadmap`
  (**link + tóm tắt tự viết**, KHÔNG copy nguyên — license CC BY-NC-SA). Fallback: "Learn with AI"
  của roadmap.sh, hoặc lộ trình nội bộ.
- **Nội dung:** `roadmaps/<slug>.md` (stage → resource → mini-project → success-check) + nguồn + ngày.
- **Acceptance:** mỗi gap có ≥1 lộ trình + lý do; ghi rõ nguồn (roadmap.sh có sẵn vs tự thiết kế).

**B8.4 — UI (chưa làm):** tab **Market** (bar top-skills, salary band, bảng GAP, link roadmap).

- **Phụ thuộc:** scan + bảng `jobs` (đã có).
- **Non-goal:** không auto-apply; không copy nguyên văn nội dung roadmap.sh.

### B9. Đồng bộ profile lên nền tảng / mạng xã hội việc làm

**Mục tiêu:** `profile.md` = SoT → sinh **"profile pack"** tuỳ biến theo từng nền tảng
(tối ưu keyword/headline để **headhunter** tìm thấy) → giảm thao tác thủ công + thông tin luôn đồng bộ.

**Skill mới:** `.opencode/skills/profile-sync/`.

**B9.1 — Pack generator (chưa làm):**
- **Nội dung:** `sync/<platform>.md` — block copy-paste sẵn + giới hạn ký tự + checklist.
  Nền tảng MVP: **LinkedIn, ITViec, GitHub** (TopCV/VietnamWorks/personal site sau).
- **Tuỳ biến:** LinkedIn (headline ≤220 ký tự, About, top skills theo market); ITViec (style VN theo
  `vn-market.md`); GitHub (bio, README, pinned repos).
- **Acceptance:** 1 profile → ≥3 pack; nội dung lấy từ `profile.md`, không bịa.

**B9.2 — Sync state + drift (chưa làm):**
- **Schema:** `profile_sync` (platform, path, profile_hash, last_synced_at, status, notes).
- **CLI:** `jc sync status` · `jc sync mark <platform> [--at]` · `jc sync drift`
  (hash `profile.md` vs lần sync → cờ "cần re-sync").
- **Acceptance:** đổi `profile.md` sau sync → `jc sync drift` báo đúng nền tảng cần cập nhật.

**B9.3 — UI (chưa làm):** panel **Profile sync** (platform, lần sync cuối, cờ drift, "view pack").

- **Automation:** MVP = **sinh pack + người paste** (khớp triết lý no-auto-apply; tránh ToS/captcha).
  **Optional (sau):** browser **prefill** qua `chrome-devtools` MCP — điền form, người bấm Save.
- **Non-goal:** auto-publish.
- **Phụ thuộc:** `profile.md` + `vn-it-cv` (đã có). **Drift detection đọc nền tảng (browser):** hoãn.

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
