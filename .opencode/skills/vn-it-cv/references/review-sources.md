# Nguồn Review Resume — tham khảo & đối chiếu

> Cách dùng: dùng các nguồn này để **đối chiếu** với rubric 100 điểm (`rubric.md`) và checklist format
> (`cv-format-ats.md`). Điểm của tool tự động **không thay thế** rubric — chỉ là tín hiệu bổ sung.
> Mọi dữ liệu đều ghi URL + ngày truy cập; kiểm tra mục **4. Nguồn & hạn verify** trước khi trích lại.

## 1. Nguồn QUY TẮC (đọc, không upload) — neo chuẩn

| Nguồn | Loại | Giá trị cốt lõi | URL |
|---|---|---|---|
| **r/EngineeringResumes wiki** | Dev-focused, cộng đồng review thật | Single-column ≤3 dòng/skill; bullet bắt đầu bằng strong past-tense action verb; công thức **XYZ** ("Accomplished X as measured by Y by doing Z"); 1 trang mặc định; template LaTeX/Google Docs | https://old.reddit.com/r/EngineeringResumes/wiki/index |
| **ByteByteGo / Gergely Orosz** *How to Write a Good Resume* | Senior eng / hiring manager | Yes/Maybe/No model, ~7s scan, tailor theo JD, impact bullets, career progression, tránh journeyman; PDF khi nộp | https://blog.bytebytego.com (part free: Intro, Part 1, Ch.1–2) |
| **ATS guides 2026** (ATSAlign, NeuraCV, ResumeAdapter, atsperfect…) | Tổng hợp quy tắc parse-safe | Đồng thuận gần tuyệt đối: single-column · standard headings · không tables/text-boxes/icons/photos/skill-bars · contact trong **body** (không header/footer) · font system Arial/Calibri/Helvetica/Georgia 10–12pt · mm/yyyy nhất quán · text-based PDF hoặc DOCX · quantify achievements | https://www.atsalign.com/blog/ats-resume-format · https://neuracv.com/resources/blog/ats-resume-format-2026 |

### 1b. Điểm đồng thuận (dùng làm checklist nhanh)
Toàn bộ nguồn trên thống nhất:
- **Bố cục:** 1 cột, đọc top→bottom; two-column/sidebar làm parser trộn dòng → loại.
- **Heading chuẩn:** Summary, Experience, Education, Skills, Certifications — không đặt tên sáng tạo.
- **Contact ở body**, không header/footer (nhiều ATS bỏ qua header/footer).
- **Không** ảnh, icon, thanh % kỹ năng, logo, chart.
- **Ngày** mm/yyyy nhất quán mọi chỗ.
- **Bullet** action verb + công nghệ + kết quả đo được; ≤2 dòng (r/ER khuyên ≤2–3).
- **Độ dài:** 1 trang khi <10 năm; ≤2 trang cho senior.
- **File:** text-based PDF (chọn được chữ); DOCX khi Workday/Taleo ask; không ảnh-only/scanned.

## 2. Tool UPLOAD tự động — lấy điểm ATS nhanh

| Tool | Free | Upload | Login | Ghi chú |
|---|---|---|---|---|
| **Resumly** `resumly.ai/ats-resume-checker` | ✅ free, no account | PDF/DOCX | Không cần cho scan | 6 chiều: parsing, sections, quantified, writing, dates, readability. **Ưu tiên #1** |
| **ResumeFast** `resumefast.io/ats-checker` | ✅ free unlimited | PDF/DOCX | Không cần cho scan cơ bản | Có keyword matcher + bullet grader + readability |
| **ResumeX** `ats.resumex.dev` | ✅ free | **PDF-only** | Không cần | Đơn giản: section parsing, impact metrics, action verbs |
| **ATSFreeCV** `atsfreecv.com` | Scan free, report đầy đủ ~$1–2 | PDF/DOCX | Không cần cho score | Score /100 + keyword match |
| **atsresumeschecker.com** | Free 16-check, rewrite trả phí | PDF/DOCX/DOC/RTF/ODT/TXT | Không cần | 16 checks |
| Jobscan | ❌ $49.95/mo | PDF/DOCX | Có | Chuẩn công nghiệp nhưng paywall |
| Resume Worded | ❌ $49/mo | PDF/DOCX | Có | Paywall |
| Kickresume | ❌ $29/mo | PDF/DOCX | Có | Paywall |

### 2b. KHÔNG dùng được để upload CV cá nhân
- **ITviec `MatchScore`** — là tool cho **nhà tuyển dụng** đo độ khớp CV↔JD, không phải ứng viên.
- **TopCV "quality assessment"** — chỉ chấm CV tạo **trong hệ thống TopCV**, không nhận PDF upload ngoài.
- **TopDev** — có "Create CV" nhưng không có upload-ngoài để lấy report.

## 3. Cách đối chiếu kết quả tool ↔ rubric vn-it-cv
Điểm tool ≠ điểm rubric. Khi có report:
1. Map từng dimension của tool về tiêu chí rubric: parsing/format → rubric #3, #7; quantified → #2; keywords → #1; dates → #5.
2. **Keyword gaps** của tool phải đối chiếu với **luật trung thực** (SKILL.md guardrail 2): thiếu keyword thì chỉ thêm được nếu có evidence trong `profile.md`; nếu không → ghi nhận là gap thật, **không nhồi**.
3. Chênh lệch lớn giữa điểm tool và điểm rubric → nêu rõ nguyên nhân (tool không biết level/domain; rubric biết JD + evidence).
4. Kết luận bằng điểm rubric /100 + danh sách việc sửa theo severity.

## 4. Nguồn & hạn verify
| Dữ liệu | Nguồn | Truy cập | Verify lại khi |
|---|---|---|---|
| Quy tắc format dev | r/EngineeringResumes wiki | 2026-10-05 | Wiki đổi cấu trúc / Reddit migration |
| Nguyên tắc CV senior | ByteByteGo (Gergely Orosz) | 2026-10-05 | Bản sách mới |
| Quy tắc ATS parse-safe | Nhóm ATS guides 2026 | 2026-10-05 | ATS vendor đổi hành vi parse (review ~6 tháng) |
| Danh sách tool upload + free tier | Trang chủ từng tool | 2026-10-05 | Tool đổi pricing/login-gate (kiểm tra trước mỗi đợt upload) |
