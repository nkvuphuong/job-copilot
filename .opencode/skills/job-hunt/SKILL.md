---
name: job-hunt
description: Quét JD từ job board (ITViec/LinkedIn/TopCV/VietnamWorks), import JD dán/file, hoặc referral; triage bằng Jev, chấm điểm theo profile.md, lưu + theo dõi trạng thái ứng tuyển, và tailor CV trung thực theo từng JD (gọi skill vn-it-cv). Trigger: "quét JD", "tìm việc", "scan ITViec/LinkedIn", "import JD", "tailor CV theo JD", "theo dõi apply", "so sánh offer", "job hunt".
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
4. **Dedupe trước khi ghi**: `rg --no-ignore -l '<url>' jobs/`.
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

- **Source**: ITViec (verified) · LinkedIn/TopCV/VietnamWorks (skeleton) · **import** (dán JD/đưa file) · **referral** (nội bộ).
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

**C. Job board** (ITViec verified; LinkedIn/TopCV/VietnamWorks là skeleton — verify trước khi tin):
> ITViec: 20 card/trang, phân trang `?page=N` (KHÔNG virtualized). Extract compact, Jev lọc trước khi mở.

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
3. Board fetch hàng loạt không cần mở tab: từ 1 tab cùng origin, `fetch(url,{credentials:'include'})` + `DOMParser`.

## Phase 4 — Score vs profile

Score neo vào **Targeting** trong `profile.md` (trọng số + must-have + nice-to-have). Bắt buộc ghi lý do để audit.

1. **Gate must-have trước:** vi phạm (fresher-level / onsite Hà Nội / yêu cầu JP-KR-CN) → `status: rejected`, `match_score: 0`, ghi lý do; hỏi user có lưu để tham khảo không.
2. **match_score** = trung bình có trọng số 5 tiêu chí Targeting (skill/stack, seniority, location, salary, domain), mỗi tiêu chí 0–100. Nice-to-have cộng tối đa +5 (không vượt 100).
3. **`score_rationale`**: 1 dòng, dạng `skill 90 · sen 100 · loc 90 · sal 80 · dom 60 → 88`, kèm gap chính. Đây là thứ để audit con số, không chỉ `notes`.
4. `gap_skills[]` = skill JD yêu cầu mà profile không có evidence.
5. Chỉ giữ vào `jobs/` nếu qua gate; dưới ngưỡng (mặc định < 60) thì báo + hỏi có lưu không.

## Phase 5 — Lưu `jobs/*.md`

- Dedupe: `rg --no-ignore -l '<url>' jobs/` — có rồi thì bỏ qua.
- Tên file: `jobs/YYYY-MM-<source>-<company-slug>-<role-slug>.md`.
- Frontmatter (schema dưới) + body = raw JD.

```yaml
---
id: 2026-10-itviec-acme-be
title: Backend Engineer
company: Acme
source: itviec
url: https://...
location: Ho Chi Minh
remote: hybrid
seniority: mid
salary_min: 0
salary_max: 0
currency: VND
skills_required: [Java, Spring]
skills_nice: [Kafka]
lang_req: [en]
posted_date: 2026-10-01
match_score: 82
score_rationale: "skill 90 · sen 100 · loc 85 · sal 70 · dom 60 → 83"  # audit con số
gap_skills: [Kafka]
status: saved        # saved|applied|screen|tech|onsite|offer|rejected|ghosted|closed
referral: false
referral_contact: ""  # tên/kênh người giới thiệu (khi referral: true)
next_action: ""
next_action_date: ""
applied_at: ""       # ISO date khi nộp; rỗng = chưa nộp
apply_method: ""     # portal|email|linkedin|referral
followup_at: ""      # ngày nên theo dõi lại
cv_version: ""
notes: ""
---
```

## Phase 6 — Tailor CV (gọi `vn-it-cv`)

1. Load skill `vn-it-cv` → chạy workflow GENERATE với input = `profile.md` + JD.
2. **Ràng buộc:** chỉ chọn bullet có trong `profile.md`; mỗi bullet giữ `<!-- evidence_id -->`.
3. **Self-check (bắt buộc):** `python3 .opencode/skills/vn-it-cv/scripts/selfcheck_cv.py cv/<file>.md` — fail (evidence_id lạ / skill claim vượt `profile.md` / số liệu Summary không có nguồn) → sửa, không tự bịa.
4. Output: `cv/<company>-<role>-<lang>.md`; render HTML bằng `python3 .opencode/skills/vn-it-cv/scripts/render_cv.py cv/<file>.md` → in PDF từ trình duyệt.
5. Cập nhật `cv_version` + `status` trong `jobs/*.md`.

## Phase 7 — Track & report

**Sự kiện ứng tuyển log vào frontmatter** (không cần file event riêng). Khi user báo tiến triển:

| Sự kiện | Ghi |
|---|---|
| Đã nộp đơn | `status: applied`, `applied_at: <ngày>`, `apply_method: portal\|email\|linkedin\|referral`, `followup_at: <applied_at + 7 ngày>` |
| Phản hồi/screen | `status: screen`, cập nhật `next_action` + `next_action_date` |
| PV tech/onsite | `status: tech` / `onsite`, `next_action` = chuẩn bị gì |
| Bị từ chối/ghosted | `status: rejected` / `ghosted`, `next_action: ""` |

Báo cáo bằng `rg` (không cần script):

```bash
rg --no-ignore --no-filename -o '^status: \w+' jobs/ | sort | uniq -c              # funnel
rg --no-ignore -l '^status: applied' jobs/ | wc -l                                # đã nộp
rg --no-ignore -l '^applied_at: ""' jobs/ | wc -l                                 # chưa nộp (backlog)
rg --no-ignore -l '^followup_at: 2026-10' jobs/                                   # cần follow-up tháng 10
rg --no-ignore -l '^referral: true' jobs/                                         # đơn có referral
```

> Nhắc chủ động: khi mở session, nếu có `followup_at` ≤ hôm nay và status chưa đổi → báo user.

## Phase 8 — Offer → Onboard → Loop

**Offer:** khi có offer, tạo `offers/<id>.md` (schema `offers/_example.md`: base/bonus/equity/benefits/level/growth/risk/deadline) + scorecard theo trọng số Targeting; set job `status: offer`.

**Onboard:** khi chốt offer → `offers/<id>.md` `status: accepted` + checklist onboarding (giấy tờ, thiết bị, mục tiêu 30/60/90 ngày). Việc thủ công, skill chỉ nhắc.

**Loop:** đóng các đơn cũ (`status: closed`); giữ `profile.md` làm nền cho lần hunt sau — profile chỉ tốt lên.

## Error handling

| Lỗi | Xử lý |
|---|---|
| `list_pages` chỉ `about:blank` / `browser already running` | Kill chrome-profile (Phase 0) → retry; login lại trong MCP window |
| Hết login | Detect form login → báo user login trong MCP window |
| List thiếu item | ITViec: phân trang `?page=N` (KHÔNG virtualized) → loop page; LinkedIn: offset `start` (xem `references/linkedin.md`) |
| `jev 401/5xx/timeout` | Log `jev-error` → fallback: mở theo keyword structural, không chặn scan |
| Trùng JD | `rg --no-ignore -l '<url>' jobs/` trước khi ghi |
| DOM đổi | Ưu tiên parse `body.innerText` thay vì selector cứng |
| Board chưa verify | `references/<source>.md` còn nhãn SKELETON → verify + cập nhật file trước khi tin kết quả |

## Non-goals (YAGNI)

Không auto-apply · không DB/UI (dùng Markdown + `rg`) · không crawler riêng (dùng MCP session) · không grounding script (dùng ràng buộc cấu trúc + self-check) — thêm khi có ca hallucination lọt.
