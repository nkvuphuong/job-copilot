---
name: vn-it-cv
description: Generate, tailor, review, and score IT CVs/resumes for the Vietnamese job market. Use when user asks to "viết CV", "tạo CV", "update CV", "viết lại CV", "tailor CV theo JD", "review CV", "góp ý CV", "chấm điểm CV", "đánh giá CV", "CV xin việc IT", "resume feedback". Chỉ dùng cho CV/resume — KHÔNG dùng cho cover letter, luyện phỏng vấn, hay tối ưu LinkedIn.
license: MIT
compatibility: opencode
metadata:
  audience: vietnamese-it-jobseekers
  market: vietnam
---

# VN IT CV — Generate / Review / Score

Viết, sửa, review và chấm điểm CV cho thị trường IT Việt Nam.

**Base dir:** thư mục chứa skill này (`.opencode/skills/vn-it-cv/` trong repo `job-copilot`) — đường dẫn dưới đây tính từ đây.

**Files:**
- `references/best-practices.md` — nguyên tắc CV cốt lõi (generate + review)
- `references/vn-market.md` — chuẩn CV theo loại công ty, platform, fresher, lương tham chiếu (nguồn + ngày)
- `references/rubric.md` — rubric 100 điểm, anti-patterns, mô phỏng scan
- `references/review-sources.md` — nguồn review bên ngoài (r/EngineeringResumes, ByteByteGo, ATS guides) + tool upload (Resumly…) + cách đối chiếu
- `templates/cv-template-en.md` / `templates/cv-template-vn.md` — skeleton khi generate
- `templates/cv-print.html` — bản A4 in PDF bằng trình duyệt
- `scripts/render_cv.py` — render `cv/*.md` → HTML in PDF (strip mọi comment HTML kể cả nhiều dòng; contact nhiều dòng render riêng hàng; `break-inside` chống cắt entry)
- `scripts/export_cv.py` — `cv/*.md` → PDF text-based (Chrome headless); `--docx` xuất thêm DOCX (pandoc)
- `scripts/selfcheck_cv.py` — kiểm trung thực: evidence_id (#1) + skill claim map về bullet/`confirmed: true` (#2); Summary warn (#3); thứ tự kinh nghiệm (#4); `**Tech:**` mỗi role phải có bằng chứng (#5); header không lộ placeholder/comment (#6)
- `scripts/ats_check.py` — mô phỏng ATS (stdlib): email/phone/URL, thứ tự section, ngày mỗi role, header sạch; cảnh báo PDF cũ/rasterized

## Bước 0 — Routing

| User nói | Workflow |
|---|---|
| "viết CV", "tạo CV", "update CV", "viết lại", "tailor theo JD" | **GENERATE** |
| "review CV", "góp ý", "CV ổn chưa", đưa CV + hỏi chung | **REVIEW** |
| "chấm điểm", "cho điểm", "đánh giá nhanh" | **SCORE** |
| "đối chiếu tool review", "upload lên ATS checker", "lấy nhận xét tự động" | **REVIEW-AUTO** |
| Chỉ đưa CV, không nói rõ | Hỏi muốn REVIEW đầy đủ hay SCORE nhanh (mặc định REVIEW) |

## Guardrails (bắt buộc, mọi workflow)

1. **KHÔNG bịa**: không tự thêm kinh nghiệm, số liệu, chức danh, thời gian, công nghệ user chưa dùng. Thiếu thông tin → hỏi, hoặc đánh dấu `[cần xác nhận: ...]` trong output.
2. **Skill chỉ đưa vào CV khi có bằng chứng hoặc user xác nhận.** Phân biệt 2 mức:
   - **Có evidence** (map được bullet trong profile.md) → để trong mục Skills bình thường.
   - **Chỉ "có trong list kỹ năng"** (`confirmed: false`) → **KHÔNG** list trong CV. Muốn dùng thì user phải xác nhận dùng thật → thêm bullet bằng chứng vào `profile.md` §4/§5 và bật `confirmed: true` TRƯỚC. `selfcheck_cv.py` chặn skill `confirmed: false`.
   - Cấm suy diễn "chắc cũng dùng" từ việc có tech liên quan.
   - Dòng `**Tech:**` cuối mỗi vị trí theo cùng luật: chỉ tech thật dùng ở role đó (có trong bullet của role hoặc `confirmed: true`); `selfcheck_cv.py` #5 chặn.
3. **Summary lấy từ §1b Positioning**: mọi con số/headline trong Summary phải khớp `profile.md` §1b + Meta. Không tự nghĩ số/định vị mới. `selfcheck_cv.py` cảnh báo (warn) metric không truy về được.
3b. **Ngôn ngữ & quyền làm việc trên CV**: KHÔNG đưa CEFR tự đánh giá (A2–B1…) hay work-authorization/sponsorship lên CV — đó là chuyện trao đổi sau, không "lật bài ngửa". Năng lực tiếng Anh thể hiện qua kinh nghiệm thật (khách/dự án quốc tế) trong Summary/Experience. Ngoại lệ duy nhất: JD là remote cho công ty **ngoài VN** → thêm 1 dòng `Time zone: GMT+7`.
4. Số liệu thị trường/lương chỉ lấy từ `references/vn-market.md`, kèm nguồn + ngày; không tự sinh số mới.
5. Xác định **loại công ty đích** (ma trận trong `vn-market.md` mục 1) trước khi chọn chuẩn CV — không mặc định một chuẩn. Không rõ → hỏi user.
6. Trao đổi với user bằng tiếng Việt; ngôn ngữ CV theo JD (mặc định EN cho IT).
7. Không ghi lương vào CV; không thêm mục thừa (sở thích, người tham chiếu) khi không được yêu cầu.

## Workflow GENERATE

1. **Thu thập** (hỏi theo cụm, không hỏi từng câu một):
   - Kinh nghiệm thô: công ty, chức danh, thời gian, việc làm, tech, kết quả/số liệu.
   - Học vấn, chứng chỉ, link GitHub/LinkedIn, CV cũ (nếu có).
   - JD + loại công ty đích + level; ngôn ngữ CV (mặc định EN).
2. Đọc `references/best-practices.md` + phần liên quan của `references/vn-market.md`.
3. **Gap analysis** JD ↔ kinh nghiệm: giữ gì, cắt gì, nhấn gì; chỉ ra chỗ thiếu bằng chứng.
4. **Draft** theo `templates/cv-template-en.md` hoặc `cv-template-vn.md` (theo target).
   - Bullet = Action + tech + kết quả; chỗ thiếu số để `[cần xác nhận: ...]`, không tự điền.
5. **Self-score** bằng `references/rubric.md` → báo điểm + danh sách chỗ cần user xác nhận.
   - **Self-check trung thực:** `python3 .opencode/skills/vn-it-cv/scripts/selfcheck_cv.py cv/<file>.md` — fail = có evidence_id lạ, skill claim vượt bullet/`confirmed: true`, `**Tech:**` thiếu bằng chứng, hoặc header lộ placeholder → sửa trước khi báo user. Summary metric là warn-only (thêm `--strict-summary` để fail).
   - **Mô phỏng ATS:** `python3 .opencode/skills/vn-it-cv/scripts/ats_check.py cv/<file>.md` — fail = thiếu email/phone/URL, sai thứ tự section, role thiếu ngày, hoặc header còn placeholder.
6. **Output**: hỏi đường dẫn, mặc định `./cv/<Ten>-<Role>-2026.md`. Render HTML/PDF:
   `python3 .opencode/skills/vn-it-cv/scripts/export_cv.py cv/<file>.md` (batch: `cv/*.md`) → `cv/<file>.pdf` text-based (Chrome headless). Thêm `--docx` nếu JD yêu cầu Word. (Chỉ cần `render_cv.py` khi muốn xem HTML trong trình duyệt.)
7. Nhắc: nộp bản PDF; xin referral **trước khi** apply nếu chưa nộp.

## Workflow REVIEW

1. Đọc CV (file/text) + JD nếu có. Đọc `references/rubric.md`, `best-practices.md`, mục 1 + checklist `vn-market.md`.
2. Mô phỏng quét **6–10 giây** → Yes/Maybe/No + lý do 1 câu.
3. Chấm rubric → bảng điểm từng tiêu chí + tổng /100 + verdict band.
4. Top 3–5 vấn đề ưu tiên (severity cao → thấp), mỗi vấn đề kèm cách sửa cụ thể.
5. 2–3 ví dụ before/after dùng bullet thật của user (thiếu số → placeholder, không bịa).
6. Checklist VN theo loại công ty đích (cuối `rubric.md`).
7. Kết bằng 2–3 quick wins làm ngay.

## Workflow SCORE (nhanh)

Chỉ chạy: mô phỏng scan (6–10s) + bảng điểm rubric + verdict + 3 lỗi nặng nhất. Không viết lại, không checklist dài.

## Workflow REVIEW-AUTO (upload & đối chiếu)

Dùng khi user muốn "đối chiếu với tool review bên ngoài" / "lấy nhận xét tự động". Đọc `references/review-sources.md`.

1. **Xuất PDF** text-based: `python3 .opencode/skills/vn-it-cv/scripts/export_cv.py cv/<file>.md` → `cv/<file>.pdf`.
2. **Xin phép user** trước khi upload — CV có info cá nhân (email/SĐT) ra site bên thứ 3. Nếu user muốn riêng tư: bỏ/anonymize dòng contact trong 1 bản copy tạm trước khi upload.
3. **Upload qua chrome-devtools MCP** lên 1 tool free trong `review-sources.md` (mặc định **Resumly**, không cần login):
   - Điền file vào `input[type=file]` (dùng `upload_file`), submit, chờ report.
   - Chỉ dùng tool **free + không cần login** trừ khi user đồng ý ngược lại.
4. **Đối chiếu** theo `review-sources.md` mục 3: map dimension tool → tiêu chí rubric; keyword gaps phải qua **luật trung thực** (guardrail 2) — không nhồi.
5. **Output**: điểm rubric /100 (chốt) + bảng đối chiếu điểm tool ↔ rubric + việc sửa theo severity. Nêu rõ điểm tool chỉ là tín hiệu bổ sung, không thay rubric.

## Format output REVIEW

```markdown
### 🔍 Mô phỏng quét 6–10 giây
[Verdict Yes/Maybe/No — lý do 1 câu]

### 📊 Điểm: [xx]/100
| # | Tiêu chí | Điểm | Nhận xét |
|---|---|---|---|

### 🎯 Vấn đề ưu tiên
1. [severity] ... → cách sửa

### ✍️ Viết lại mẫu
Before: ...
After: ...

### ✅ Checklist
- [ ] ...
```

## Khi dữ liệu thị trường cần cập nhật

Kiểm tra mục **8. Nguồn & hạn verify** trong `vn-market.md`. Nếu đã quá hạn: fetch lại nguồn (ITviec report, TopDev market reports) trước khi trích số mới; cập nhật ngày truy cập.
