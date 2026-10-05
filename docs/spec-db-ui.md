# Spec: DB + UI quản lý state job-hunt (v1)

Status: draft → chờ duyệt
Owner: phuongnguyenkieuvu
Scope: v1 = bước 1–4 (DB + CLI + migrate + UI state). Bước 5–6 để trong `ROADMAP.md`.

## Objective

Hiện state sống trong frontmatter `jobs/*.md`; báo cáo bằng `rg`; agent mỗi lần chạy
phải full-scan folder, và các lần re-run chồng job/CV nhiều version. Mục tiêu:

- **DB SQLite** là nguồn sự thật cho **lifecycle + identity/dedupe + run**.
- **File** vẫn giữ phần **nội dung** (raw JD, CV body, prep, offer) — agent sở hữu.
- **UI local** cho người dùng quản lý state (status, apply, follow-up) thay vì chat.
- Scan lại **loại trừ job đã có bằng query DB**, không quét folder.

Người dùng: một người, chạy local, dự án cá nhân. Không auth, không multi-user.

Success: re-run idempotent; state transition làm trên UI; mỗi run truy vết được
"mang về gì / trùng gì"; mỗi field state chỉ có **một** nguồn (DB).

## Tech Stack

- Python 3.13 **stdlib thuần**, 0 dependency mới: `sqlite3`, `argparse`, `http.server`, `json`, `hashlib`, `re`, `unicodedata`.
- SQLite một file: `jobcopilot.db` (gitignored, sinh ra bởi `init`).
- UI: 1 file HTML tĩnh + JS thuần, `fetch` JSON endpoint. Không Jinja2, không framework, không ORM.
- Seam để đổi sau: `db.py` thuần (không HTTP). Nếu UI phình → chỉ thay `server.py`, không đụng data layer.

## Commands

```bash
# CLI (agent + người dùng cùng gọi)
python3 tools/jobcopilot/cli.py init                      # tạo DB + schema nếu chưa có (idempotent)
python3 tools/jobcopilot/cli.py import                    # migrate jobs/*.md frontmatter -> DB, strip frontmatter
python3 tools/jobcopilot/cli.py dedupe-check <url> [--source S --external-id E --company C --title T --location L]
python3 tools/jobcopilot/cli.py add --json '<job json>'   # đăng ký 1 job mới (agent dùng sau khi extract)
python3 tools/jobcopilot/cli.py run start --source itviec --params '<json>'
python3 tools/jobcopilot/cli.py run finish <run_id> --counts '<json>'
python3 tools/jobcopilot/cli.py status <job_id> --to applied [--at 2026-10-05 --method portal] [--note ...]
python3 tools/jobcopilot/cli.py report                    # in funnel/backlog/follow-up (đọc DB)
python3 tools/jobcopilot/cli.py selfcheck                 # assert-based check cho identity/dedupe

# UI (localhost)
python3 tools/jobcopilot/server.py                        # tự init nếu DB thiếu; mặc định http://127.0.0.1:8765
```

Không có bước build/lint riêng (stdlib). Kiểm thử: `python3 tools/jobcopilot/cli.py selfcheck`.

## Project Structure

```
tools/jobcopilot/
  db.py          # schema, connection, CRUD thuần (nguồn ghi state duy nhất)
  identity.py    # url_canonical, dedupe_key, normalize title/company, tier-2 fuzzy
  migrate.py     # đọc frontmatter jobs/*.md -> DB; strip frontmatter (giữ raw JD)
  cli.py         # argparse; import/init/add/dedupe-check/run/status/report/serve/selfcheck
  server.py      # http.server: phục vụ ui/ + JSON API -> gọi db.py
  ui/index.html  # dashboard + list/filter + form đổi state (JS thuần)
docs/
  spec-db-ui.md  # file này
ROADMAP.md       # backlog bước 5–6 + ghi chú Docker nếu hosted
jobcopilot.db    # gitignored
```

Content files giữ nguyên: `jobs/<id>.md` (sau migrate: vài dòng header hiển thị
`title` / `company` / `url`, rồi tới raw JD — không còn frontmatter lifecycle),
`cv/*.md`, `prep/*.md`, `offers/*.md`, `profile.md`.

## Data Model (SQLite)

| Bảng | Vai trò | Cột chính |
|---|---|---|
| `runs` | 1 scan session | `id` PK, `started_at`, `source`, `params_json`, `status`(running/done/error), `counts_json` |
| `jobs` | job + lifecycle hiện tại | `id` PK, `source`, `external_id`, `url`, `url_canonical`, `company`, `company_slug`, `title`, `title_norm`, `location`, `remote`, `seniority`, `salary_min`, `salary_max`, `currency`, `skills_required_json`, `skills_nice_json`, `lang_req_json`, `posted_date`, `match_score`, `score_rationale`, `gap_skills_json`, `verdict`(keep/skip/gate-rejected), `verdict_reason`, `duplicate_of`, `status`, `applied_at`, `apply_method`, `followup_at`, `next_action`, `next_action_date`, `referral`, `referral_contact`, `first_run_id`, `notes`, `created_at`, `updated_at` |
| `job_events` | lịch sử transition | `id` PK, `job_id` FK, `at`, `type`, `from_status`, `to_status`, `note` |
| `run_items` | job nào do run nào mang về | `run_id` FK, `job_id` FK, `disposition`(new/dup/skipped/error) |
| `cv_versions` | versioning CV (để sẵn cho bước 5) | `id` PK, `job_id` FK, `lang`, `path`, `created_at`, `hash`, `is_current` |

`status` vocab: `saved|applied|screen|tech|onsite|offer|rejected|ghosted|closed`.
`jobs.status` = trạng thái hiện tại; lịch sử nằm ở `job_events`.

### Identity / Dedupe

- Tier 1 (auto-block): `dedupe_key = source||':'||external_id`, fallback `url_canonical` (bỏ query/utm/fragment).
- Tier 2 (KHÔNG auto-skip): khớp `company_slug + title_norm + location` → set `duplicate_of`, UI cho người xác nhận.
- Lý do tier 2 không tự chặn: re-post có thể đổi lương/level → là cơ hội mới.

## Code Style

```python
# db.py — thuần, không import HTTP
def connect(path: str = "jobcopilot.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def set_status(conn, job_id: str, to: str, *, at: str, note: str = "") -> None:
    row = conn.execute("SELECT status FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if row is None:
        raise KeyError(job_id)
    conn.execute("UPDATE jobs SET status = ?, updated_at = ? WHERE id = ?", (to, at, job_id))
    conn.execute(
        "INSERT INTO job_events (job_id, at, type, from_status, to_status, note) VALUES (?,?,?,?,?,?)",
        (job_id, at, "status", row["status"], to, note),
    )
```

Quy ước: snake_case; type hint ở chữ ký public; không comment thừa; SQL thẳng,
không ORM; mọi thao tác ghi state đi qua `db.py` (CLI và server đều gọi cùng hàm).

## Testing Strategy

- Không framework test. Một `selfcheck` assert-based trong `cli.py` (hoặc `test_identity.py`) phủ `identity.py`: chuẩn hoá URL (bỏ utm/query), `title_norm`, và `dedupe_key` (source+external_id thắng url).
- Check thủ công bắt buộc sau migrate: `migrate` chạy 2 lần → số row không đổi.
- UI smoke: mở `server.py`, list + filter + đổi status + confirm duplicate.

## Boundaries

- **Always:** đi qua `db.py` khi ghi state; migrate idempotent; giữ `vn-it-cv` + `render_cv.py` + `selfcheck_cv.py` nguyên vẹn; chạy `selfcheck` sau khi sửa `identity.py`.
- **Ask first:** đổi schema (thêm/xoá bảng/cột); đổi vocab `status`; thêm dependency; xoá/rewrite `jobs/*.md` ngoài phạm vi strip frontmatter.
- **Never:** bake DB/personal data vào git; viết CV body vào DB; auto-apply; xoá file content của người dùng; auto-skip ở tier-2.

## Success Criteria

1. `cli.py init` tạo `jobcopilot.db` với 5 bảng; chạy lại không lỗi.
2. `cli.py import` nạp đủ 13 `jobs/*.md` + liên kết `cv_versions` cho 16 CV đang có; chạy 2 lần số row không đổi; `jobs/*.md` sau đó còn header hiển thị (title/company/url) + raw JD (không frontmatter lifecycle).
3. `dedupe-check <url đã có>` trả về job cũ; re-post lệch URL (tier 2) → gắn `duplicate_of`, không chặn.
4. `status` transition ghi được `job_events` (có from/to) và cập nhật `jobs.status`.
5. UI: dashboard hiển thị funnel + due follow-up; list lọc được theo status/source/seniority/run; đổi status + confirm duplicate hoạt động; không cần quét folder.
6. `report` (đọc DB) cho ra số liệu khớp với UI.

## Decisions (đã chốt)

1. Port UI mặc định: `8765` (đổi qua `--port`).
2. `jobs/<id>.md` sau migrate: thêm vài dòng header hiển thị `title` / `company` / `url`, rồi raw JD.
3. 13 job migrate: `first_run_id = NULL` (không có run gốc).

## Open Questions

Không còn.
```
