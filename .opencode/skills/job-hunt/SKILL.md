---
name: job-hunt
description: Quét JD từ job board (ITViec/LinkedIn/TopCV/VietnamWorks), import JD dán/file, hoặc referral; triage bằng Jev, chấm điểm theo profile.md, lưu + theo dõi trạng thái ứng tuyển, tailor CV trung thực theo từng JD (gọi skill vn-it-cv), và chuẩn bị phỏng vấn (JD digest + company brief + technical/non-technical prep + mock interview). Trigger: "quét JD", "tìm việc", "scan ITViec/LinkedIn", "import JD", "tailor CV theo JD", "theo dõi apply", "chuẩn bị phỏng vấn", "prep cho job X", "mock interview", "phỏng vấn thử", "quiz me", "so sánh offer", "job hunt".
license: MIT
compatibility: opencode
metadata:
  audience: personal
  repo: job-copilot
  mcp: [chrome-devtools]
  tool: jev
  depends_on: vn-it-cv
---

# Job Hunt

Biến việc tìm việc thành pipeline có kiểm soát: **quét JD → triage → score → lưu → tailor CV → nộp → track → (offer) compare**.

## Nguyên tắc (bắt buộc)

1. **Trung thực tuyệt đối:** CV tailor chỉ được SELECT / REORDER / REWORD từ `profile.md`. **Cấm INVENT.** Mọi bullet truy về `evidence_id`. Không có evidence → không xuất hiện.
2. **Không auto-apply.** Con người duyệt cuối + bấm nộp.
3. **Hỏi scope trước khi quét** (source, keyword, level, location, remote, số lượng).
4. **Dedupe trước khi ghi**: `python3 tools/jobcopilot/cli.py dedupe-check '<url>'`.
5. **Không đổi ngày tháng/title** khi tailor; de-emphasize là lựa chọn có ý thức (ghi lại).
6. Chạy skill này khi **cwd nằm trong repo** `job-copilot` (để `vn-it-cv` cũng load).

## Phase 0 — Prereq check (tránh lỗi đầu session)

```
[ ] chrome-devtools MCP attach được (list_pages KHÔNG lỗi "browser is already running")
[ ] Đã login ITViec/LinkedIn trong Chrome do MCP launch (không hiện form login)
[ ] Tool jev OK — smoke: node ~/.config/opencode/skills/jev-triage/scripts/smoke.mjs → SMOKE OK
[ ] profile.md đã điền (ít nhất meta + skills + 1 experience)
```
Stale Chrome profile: `pkill -f "user-data-dir=$HOME/.cache/chrome-devtools-mcp/chrome-profile"; sleep 2` rồi `list_pages` lại.

## Phase 1 — Hỏi scope (dùng `question` tool)

- **Source**: ITViec (verified) · TopCV (verified) · LinkedIn/VietnamWorks (skeleton) · **import** (dán JD/đưa file) · **referral** (nội bộ).
- **Keyword / role** (vd "backend java", "golang").
- **Level / location / remote** (mặc định lấy từ `profile.md` mục Targeting).
- **Số lượng / số trang** cần quét.

## Phase 2 — Scan list + Jev preview-screen

Chọn cách theo source (Phase 1). **Nguồn hạng nhất là `import`** — không cần board/login.

**A. Import / paste / file** (rẻ nhất, chạy được ngay):
- User dán JD text hoặc trỏ file → **bỏ qua scan**, sang thẳng Phase 3.
- Vẫn tạo `jobs/*.md` với `source: import`, `url: local://<ghi chú>`.

**B. Referral / nội bộ:**
- Không có scraper. User mô tả cơ hội → tạo `jobs/*.md` với `source: referral`, `referral: true`, `referral_contact: <tên/kênh>`.

**C. Job board** (ITViec + TopCV verified; LinkedIn/VietnamWorks là skeleton — verify trước khi tin):
> ITViec: 20 card/trang, phân trang `?page=N` (KHÔNG virtualized). TopCV: ~52 card/trang, `?page=N`, JSON-LD `JobPosting` ở detail. Extract compact, Jev lọc trước khi mở.

1. Navigate tới trang search với filter (keyword/location) — selectors/URL theo `references/<source>.md`.
2. **Collect-while-scroll** trên list kết quả, dedupe theo link JD, extract compact mỗi item:
   `{ title, company, location, salary, level, posted, url, snippet }` (cap text ~200–300 ký tự).
3. **Jev preview-screen** (1 request, đánh số section) — quyết định item nào đáng mở:
   - `sN_relevant` (noul): "JD này khớp target role/skills trong profile?" 
   - `sN_seniority` (choice): dưới mức / đúng mức / trên mức (theo `profile.md`).
   - Structural signal thắng Jev: badge "New"/"Hot", bằng đúng keyword → keep không cần hỏi.
   - Luật: `noul ≥ 0.8` → mở; `0.5–0.8` → mở (thà thừa hơn sót); `< 0.5` và không structural → skip + log.
4. Chỉ mở JD của item `keep`.

> Selectors từng source: xem `references/<source>.md`. ITViec đã verify; các board khác là skeleton — verify rồi cập nhật file trước khi dùng.

## Phase 3 — Mở JD + extract + parse

1. Lấy nội dung JD (fetch board theo `references/<source>.md`; hoặc JD user dán/import). **Parse bằng snippet thống nhất** (JSON-LD path 1 → fallback DOM path 2) trong `references/itviec.md` mục 3 khi là ITViec. Không bỏ JD chỉ vì thiếu JSON-LD.
2. Parse thành field cấu trúc (model chính, không dùng Jev):
   `{ title, company, seniority, location, remote, salary_min/max, currency, skills_required[], skills_nice[], lang_req, years_exp }`.
3. Board fetch hàng loạt không cần mở tab: từ 1 tab cùng origin, `fetch(url,{credentials:'include'})` + `DOMParser`. **Throttle 1.5s/batch ≤8 + phát hiện Cloudflare challenge (429/403)** — xem `references/fetch-policy.md`; list dùng `navigate_page` + DOM.

## Phase 4 — Score vs profile

Score neo vào **Targeting** trong `profile.md` (trọng số + must-have + nice-to-have). Bắt buộc ghi lý do để audit.

1. **Gate must-have trước:** vi phạm (fresher-level / onsite Hà Nội / yêu cầu JP-KR-CN) → `status: rejected`, `match_score: 0`, ghi lý do; hỏi user có lưu để tham khảo không.
2. **match_score** = trung bình có trọng số 5 tiêu chí Targeting (skill/stack, seniority, location, salary, domain), mỗi tiêu chí 0–100. Nice-to-have cộng tối đa +5 (không vượt 100).
3. **`score_rationale`**: 1 dòng, dạng `skill 90 · sen 100 · loc 90 · sal 80 · dom 60 → 88`, kèm gap chính. Đây là thứ để audit con số, không chỉ `notes`.
4. `gap_skills[]` = skill JD yêu cầu mà profile không có evidence.
5. Chỉ lưu nếu qua gate; dưới ngưỡng (mặc định < 60) thì báo + hỏi có lưu không.

## Phase 5 — Lưu: raw JD ra file + state vào DB

**DB là nguồn state** (`jobcopilot.db`, xem `docs/spec-db-ui.md`). File chỉ chứa nội dung.

1. **Dedupe trước khi ghi** (thay cho `rg`):
   ```bash
   python3 tools/jobcopilot/cli.py dedupe-check '<url>' --source <src> \
     --company '<c>' --title '<t>' --location '<l>'
   ```
   - `exact` khác null → đã có, **bỏ qua**.
   - `fuzzy` khác rỗng → vẫn thêm, nhưng `add` sẽ set `duplicate_of`; **người xác nhận trên UI** (không auto-skip).
2. **Ghi raw JD** vào `jobs/<id>.md` với header hiển thị, rồi tới JD nguyên văn:
   ```
   # <title> — <company>

   Company: <company> · Source: <source>
   URL: <url>

   <raw JD>
   ```
3. **Đăng ký structured row** (score/skills/gaps) + gắn run:
   ```bash
   python3 tools/jobcopilot/cli.py add --json '{
     "id":"<id>","title":"…","company":"…","source":"…","url":"…",
     "location":"…","remote":"hybrid","seniority":"mid",
     "salary_min":0,"salary_max":0,"currency":"VND",
     "skills_required":["Java","Spring"],"skills_nice":["Kafka"],"lang_req":["en"],
     "match_score":82,"score_rationale":"skill 90 · sen 100 · loc 85 · sal 70 · dom 60 → 83",
     "gap_skills":["Kafka"],"verdict":"keep","run_id":<run-id>}'
   ```
   `id = YYYY-MM-<source>-<company-slug>-<role-slug>`; tên file = `id`. Lifecycle
   (`status/applied_at/…`) **không** nằm trong file — đổi qua UI hoặc `jc status`.

## Phase 6 — Tailor CV (gọi `vn-it-cv`)

1. Load skill `vn-it-cv` → chạy workflow GENERATE với input = `profile.md` + JD.
2. **Ràng buộc:** chỉ chọn bullet có trong `profile.md`; mỗi bullet giữ `<!-- evidence_id -->`.
3. **Self-check (bắt buộc):** `python3 .opencode/skills/vn-it-cv/scripts/selfcheck_cv.py cv/<file>.md` — fail (evidence_id lạ / skill `confirmed: false` bị list / skill claim vượt `profile.md` / `**Tech:**` thiếu bằng chứng / header lộ placeholder) → sửa, không tự bịa. Số liệu Summary chỉ được **warn** (không fail) trừ khi chạy `--strict-summary`.
4. **Mô phỏng ATS (bắt buộc):** `python3 .opencode/skills/vn-it-cv/scripts/ats_check.py cv/<file>.md` — fail (thiếu email/phone/URL, sai thứ tự section, role thiếu ngày, header placeholder). Advisory: `python3 .opencode/skills/vn-it-cv/scripts/jd_coverage.py cv/<file>.md jobs/<job>.md` (ADD/CONTEXT/GAP — chỉ thêm khi có bằng chứng).
5. Output: `cv/<company>-<role>-<lang>.md` → `python3 .opencode/skills/vn-it-cv/scripts/export_cv.py cv/<file>.md` → `cv/<file>.pdf` (text-based, Chrome headless).
6. Cập nhật `cv_versions` (hash) trong DB; `status` đổi qua UI/`jc status` — **KHÔNG** ghi lifecycle vào `jobs/*.md`.

## Phase 6.5 — Interview Prep (sau khi nộp / khi có lịch)

Sau khi `status: applied` (hoặc muộn hơn khi có lịch phỏng vấn), tạo `prep/<job-id>.md` (schema `prep/_example.md`, hướng dẫn `references/interview-prep.md`). Mục tiêu: **cue card** để ứng viên không bỏ sót gì khi vào vòng — không phải script học thuộc.

**4 khối:**
1. **JD digest** — must-have vs nice-to-have; stack JD nhấn (lặp nhiều = họ quan tâm); signal seniority (own/lead/design/mentor); 2–3 responsibility chính `[jd]`.
2. **Company brief** — chỉ từ JD + trang chính thức **nếu đã fetch**; product/mô hình, quy mô/domain, stack lộ ra, văn hóa, tin gần đây (kèm ngày). Thiếu nguồn → `[confirm: ...]`, **không bịa**.
3. **Technical prep** — map JD → evidence `profile.md` (strong/ok/weak) → gap plan `[gap: ôn X]`; câu hỏi khả năng cao theo stack (cue, không viết sẵn đáp án); **STAR story bank** lấy từ 3–5 bullet có sẵn trong profile, kèm `evidence_id`. Cấm bịa story/skill mới.
4. **Non-technical prep** — quy trình làm việc (Agile/review/CI-CD/on-call), problem-solving, giao tiếp/trình bày, teamwork; **3–5 câu hỏi ngược lại cho nhà tuyển dụng**; logistics (hình thức/thời lượng/người PV).

**Nhãn nguồn bắt buộc:** `[jd]` · `[web: <url>]` · `[profile: e0xx]` · `[guess]` · `[confirm: ...]`. Không nêu fact công ty chưa đọc.

- Web fetch chỉ khi user cho phép (dùng `webfetch` hoặc MCP browser). Offline → điền từ JD, phần còn lại `[confirm: ...]`.
- Cập nhật `prep_status` (`draft→ready→done`) + ghi log từng vòng vào mục "Mock round log".
- Đặt cue card tại `prep/<job-id>.md`. `prep_status` sẽ chuyển vào DB ở bước B5 (`ROADMAP.md`); v1 chưa có bảng prep.

> Khi user nói "prep cho job X", "chuẩn bị phỏng vấn <công ty>" → chạy phase này.

**Mock interview (sub-step, khi user yêu cầu):** "mock interview", "phỏng vấn thử", "quiz me", "đóng vai interviewer".
- Đọc `prep/<job-id>.md`; xác nhận loại vòng (screen/tech/manager) + thời lượng (mặc định tech 30–45').
- **Hỏi từng câu một**, chờ trả lời rồi mới qua câu kế. Chỉ dùng câu hỏi trong prep file + STAR story bank `profile.md`; **không bịa** fact công ty/stack ngoài JD.
- Giữ vai interviewer, không đưa đáp án giữa vòng; feedback sau khi user nói "stop/end".
- Feedback: mỗi câu → điểm mạnh, chỗ mơ hồ, **1 cách sửa cụ thể**; ghi vào "Mock round log" + bổ sung gap plan nếu lộ lỗ hổng. Không viết lại đáp án thành script.
- Chi tiết + anti-patterns: `references/interview-prep.md` mục "Mock interview".

## Phase 7 — Track & report

**Sự kiện log vào DB + `job_events`** (không sửa file). Khi user báo tiến triển, ghi qua CLI/UI:

| Sự kiện | Ghi |
|---|---|
| Đã nộp đơn | `jc status <id> --to applied --at <ngày> --method portal\|email\|linkedin\|referral --followup-at <applied+7d>` |
| Phản hồi/screen | `jc status <id> --to screen --next-action … --next-action-date …` |
| PV tech/onsite | `jc status <id> --to tech` / `--to onsite`; tạo/cập nhật `prep/<job-id>.md` |
| Bị từ chối/ghosted | `jc status <id> --to rejected` / `--to ghosted` |

Báo cáo từ DB — **không quét folder**:

```bash
python3 tools/jobcopilot/cli.py report     # funnel + backlog (chưa nộp) + followup_due
python3 tools/jobcopilot/server.py         # UI: http://127.0.0.1:8765
```

> Nhắc chủ động: khi mở session, chạy `cli.py report`; nếu `followup_due` khác rỗng → báo user.

## Phase 8 — Offer → Onboard → Loop

**Offer:** khi có offer, tạo `offers/<id>.md` (schema `offers/_example.md`: base/bonus/equity/benefits/level/growth/risk/deadline) + scorecard theo trọng số Targeting; đổi state bằng `jc status <id> --to offer` (hoặc UI).

**Onboard:** khi chốt offer → `offers/<id>.md` `status: accepted` + checklist onboarding (giấy tờ, thiết bị, mục tiêu 30/60/90 ngày). Việc thủ công, skill chỉ nhắc.

**Loop:** đóng các đơn cũ (`status: closed`); giữ `profile.md` làm nền cho lần hunt sau — profile chỉ tốt lên.

## Error handling

| Lỗi | Xử lý |
|---|---|
| `list_pages` chỉ `about:blank` / `browser already running` | Kill chrome-profile (Phase 0) → retry; login lại trong MCP window |
| Hết login | Detect form login → báo user login trong MCP window |
| List thiếu item | ITViec: phân trang `?page=N` (KHÔNG virtualized) → loop page; LinkedIn: offset `start` (xem `references/linkedin.md`) |
| `jev 401/5xx/timeout` | Log `jev-error` → fallback: mở theo keyword structural, không chặn scan |
| Trùng JD | `cli.py dedupe-check '<url>'` trước khi ghi (exact auto-block; fuzzy → người confirm) |
| `fetch` 429 / `cf-mitigated: challenge` (ITViec) | Cloudflare challenge do burst — **throttle 1.5s**, batch ≤8, retry sau 5–10s; vẫn chặn → `navigate_page` + DOM. Xem `references/fetch-policy.md`. |
| `fetch` list 403 (TopCV) | List **bắt buộc** `navigate_page` + đọc DOM; chỉ detail mới `fetch`. Xem `references/fetch-policy.md`. |
| Nhập sai / cần xoá 1 job (reset) | `python3 tools/jobcopilot/cli.py rm <job_id> [--files]` — xoá row + children (`job_events`/`cv_versions`/`prep`…); `--files` xoá luôn `jobs/<id>.md` + `prep/<id>.md`. Không có trong file content khác. |
| Cần reset shortlist (đổi mục tiêu) | archive = loop `cli.py status <id> --to closed` (giữ history); xoá hẳn = `cli.py rm <id> --files` |
| DOM đổi | Ưu tiên parse `body.innerText` thay vì selector cứng |
| Board chưa verify | `references/<source>.md` còn nhãn SKELETON → verify + cập nhật file trước khi tin kết quả |

## Non-goals (YAGNI)

Không auto-apply · DB/UI đang triển khai từng phần (state/dedupe/run trong SQLite — `docs/spec-db-ui.md`, `ROADMAP.md`; file vẫn giữ nội dung) · không crawler riêng (dùng MCP session) · không grounding script (dùng ràng buộc cấu trúc + self-check) — thêm khi có ca hallucination lọt.
