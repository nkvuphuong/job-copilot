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
- `templates/cv-template-en.md` / `templates/cv-template-vn.md` — skeleton khi generate
- `templates/cv-print.html` — bản A4 in PDF bằng trình duyệt
- `scripts/render_cv.py` — render `cv/*.md` → HTML in PDF (tự strip `<!-- evidence_id -->`)
- `scripts/selfcheck_cv.py` — kiểm trung thực: evidence_id + skill claim phải map về `profile.md`

## Bước 0 — Routing

| User nói | Workflow |
|---|---|
| "viết CV", "tạo CV", "update CV", "viết lại", "tailor theo JD" | **GENERATE** |
| "review CV", "góp ý", "CV ổn chưa", đưa CV + hỏi chung | **REVIEW** |
| "chấm điểm", "cho điểm", "đánh giá nhanh" | **SCORE** |
| Chỉ đưa CV, không nói rõ | Hỏi muốn REVIEW đầy đủ hay SCORE nhanh (mặc định REVIEW) |

## Guardrails (bắt buộc, mọi workflow)

1. **KHÔNG bịa**: không tự thêm kinh nghiệm, số liệu, chức danh, thời gian, công nghệ user chưa dùng. Thiếu thông tin → hỏi, hoặc đánh dấu `[cần xác nhận: ...]` trong output.
2. **Skill chỉ đưa vào CV khi có bằng chứng hoặc user xác nhận.** Phân biệt 2 mức:
   - **Có evidence** (map được bullet trong profile.md) → để trong mục Skills bình thường.
   - **Chỉ "có trong list kỹ năng"** (profile đánh dấu, không có bullet chứng minh) → CHỈ đưa nếu JD yêu cầu và user xác nhận đã dùng thật; khi đó ghi trong CV không kèm ngữ cảnh/số liệu giả. Còn lại: bỏ.
   - Cấm suy diễn "chắc cũng dùng" từ việc có tech liên quan.
3. **Summary cũng phải truy về evidence**: mọi con số/"12+ years"/domain trong Summary phải khớp `profile.md` Meta + ít nhất 1 `evidence_id`. Không nêu thành tích không có bullet.
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
   - **Self-check trung thực:** `python3 .opencode/skills/vn-it-cv/scripts/selfcheck_cv.py cv/<file>.md` — fail = có evidence_id lạ hoặc skill claim vượt `profile.md` → sửa trước khi báo user.
6. **Output**: hỏi đường dẫn, mặc định `./cv/<Ten>-<Role>-2026.md`. Render HTML in PDF:
   `python3 .opencode/skills/vn-it-cv/scripts/render_cv.py cv/<file>.md` (batch: `cv/*.md`), rồi `Cmd+P` → Save as PDF (A4).
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
