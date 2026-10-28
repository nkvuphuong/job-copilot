# Roadmap

Trạng thái: **v1 + B5.1 (prep) + B7 (export/backup) + B9 (profile sync) đã xong**.
Còn lại: B5.2 (offers), B6 (onboard/archive), B8 (market → GAP → roadmap).
Spec: [`docs/spec-db-ui.md`](docs/spec-db-ui.md).

Mục đích file này: giữ các bước **cố tình hoãn** với đủ ngữ cảnh để nhặt lên làm
tiếp mà không phải nhớ. Mỗi mục có acceptance criteria riêng.

## Đã xong — v1

- [x] `tools/jobcopilot/db.py` + `identity.py` + schema
- [x] `migrate.py`: import `jobs/*.md` frontmatter → DB, strip frontmatter
- [x] `cli.py`: `init` / `import` / `dedupe-check` / `add` / `run` / `status` / `report`
- [x] `server.py` + `ui/index.html`: dashboard + list/filter + đổi state + confirm duplicate
- [x] Rewire `job-hunt/SKILL.md` (Phase 2,3,5,6) + `WORKFLOW.md` (Phase 2,3,5,6 + Non-goals) sang DB
- [x] Cập nhật `AGENTS.md`, `README.md`, `.gitignore` (+`jobcopilot.db`)

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

### B9. Đồng bộ profile lên nền tảng / mạng xã hội việc làm ✅ xong (2026-10-28)

**Mục tiêu:** `profile.md` = SoT → sinh **"profile pack"** tuỳ biến theo từng nền tảng
(tối ưu keyword/headline để **headhunter** tìm thấy) → giảm thao tác thủ công + thông tin luôn đồng bộ.

**Skill mới:** `.opencode/skills/profile-sync/`.

**B9.1 — Pack generator ✅ xong:**
- MVP **4 nền tảng**: LinkedIn, ITviec, **TopCV** (thêm theo yêu cầu user), GitHub.
- Format **theo field** (`## Field  <!-- limit: N -->` + fenced block) — paste thẳng từng ô.
- Ngôn ngữ: **EN toàn bộ** (kể cả ITviec/TopCV — chốt của user).
- `references/platforms.md` (limit + trạng thái verify), `references/writing-style.md` (style từng nền tảng).
- Gate: `scripts/pack_check.py` — vượt limit ký tự hoặc evidence id không tồn tại → exit 1. E2E P5e phủ.
- Output: `sync/<platform>.md` (gitignored).

**B9.4 — Prefill bằng chrome-devtools MCP ✅ xong (làm trước B9.2):**
- `references/prefill.md`: `navigate_page` → `take_snapshot` → `fill_form`/`fill` → `take_screenshot` → **dừng**.
- **Guardrail tuyệt đối: agent KHÔNG bao giờ bấm Save/Lưu/Cập nhật/Publish/Submit** — user tự bấm.
- Không lưu selector trong repo (dùng a11y ref của `take_snapshot`) → nền tảng đổi UI không vỡ.
- Thứ tự: ITviec → TopCV → GitHub → LinkedIn (LinkedIn chống automation mạnh nhất, modal từng field).
- Upload **CV master** (không phải CV tailor) qua `upload_file`, không bấm nút xác nhận.

**B9.2 — Sync state + drift ✅ xong:**
- Bảng `profile_sync` (platform PK, path, profile_hash, last_synced_at, status, notes) — `SCHEMA_VERSION=3`.
- `jc sync status` · `jc sync mark <platform>` · `jc sync drift`; tái dùng `db.profile_ver()` của `cv_versions`.

**B9.3 — UI ✅ xong:** panel **Profile sync** trên dashboard (platform · lần sync cuối · cờ drift ·
"Mở pack" · "Đã sync"); `GET /api/sync`, `GET /api/sync/<platform>[?format=html]`, `POST /api/sync/<platform>`.

**Còn lại (chưa làm):**
- `sync/github.md` — pinned repos cần user chọn (5 slot đang `[cần xác nhận]`).
- LinkedIn prefill: chưa chạy lượt nào (giới hạn đã verify từ tài liệu, chưa verify trên form thật).

**Bài học từ lượt prefill đầu (2026-10-28)** — chi tiết + luật ở
`.opencode/skills/profile-sync/references/prefill.md` mục "Sai sót đã mắc":
1. Pack ITviec/TopCV viết từ giả định → sai hình dạng (ITviec = CV builder + About Me 2500 ký tự;
   TopCV không có profile text). **Snapshot trước, viết pack sau.**
2. `Close`/`×` trên ITviec **huỷ** thay đổi, không phải lưu → mất 2 lượt điền (About Me; Title + link).
3. `ArrowDown`+`Enter` trên combobox chọn nhầm option (`Vice President / Director`) → luôn
   `fill` đúng nhãn rồi `Enter` + đọc lại value.
4. ~~Native `<select>` không điền được~~ **SAI, đã sửa**: `<select>` bị **Tom Select** bọc (1×1px,
   `tabindex=-1`). `click`/`fill`/`press_key` đều fail, nhưng điền được bằng
   `el.tomselect.open()` → `refreshOptions(false)` → click `.option[data-value="9"]` → verify `el.value`.
   → đừng kết luận "không điền được" trước khi thử đường của widget.
5. Điều hướng nhiều lần trên TopCV → Cloudflare chặn phiên. **Một nền tảng một lượt, không retry.**
6. `new_page`/`close_page` khi còn form chưa Save → **mất form** (id tab đổi sau `new_page`). Phải
   `list_pages` + so URL/title trước khi đóng; tab đang có form = chỉ snapshot/screenshot.
7. Chép bullet Work Experience vào Highlight Project (trùng ~90%). Project = bối cảnh/quy mô/kiến trúc/
   vai trò/team; số liệu **kết quả** để Experience kể.
8. Đọc counter `1441/500` thành 5000 → Cover Letter bị chặn. Lấy đúng cặp `x/y` từ DOM trước khi viết.

**Non-goal:** không auto-publish. **Phụ thuộc:** `profile.md` + `vn-it-cv`.

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
