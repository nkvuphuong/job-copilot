# CV Format ATS — luật trình bày cho ngành CNTT

> Đúc kết từ các nguồn uy tín (xem `review-sources.md`): r/EngineeringResumes wiki, ByteByteGo/Gergely Orosz,
> và nhóm ATS guides 2026. Dùng khi render (`render_cv.py`/`export_cv.py`) và khi review layout (`rubric.md` #3, #7).
> Truy cập 2026-10-05.

## 1. Bố cục (bắt buộc)
- **Single-column**, đọc top→bottom. Two-column/sidebar → parser trộn dòng (Greenhouse liệt kê là nguyên nhân parse lỗi). → CV generator phải luôn 1 cột.
- **Heading chuẩn:** Summary, Skills, Experience, Education, Certifications, Projects. Không đặt tên sáng tạo ("My Journey").
- **Contact trong body**, KHÔNG header/footer HTML (nhiều ATS bỏ qua header/footer).
- **Contact 2 dòng** cố định: dòng 1 địa điểm · email · phone; dòng 2 github · linkedin → URL không bị wrap/cắt. `render_cv.py` render mỗi dòng contact thành 1 hàng riêng.
- Thứ tự senior: Header → Summary → (Selected Achievements?) → Skills → Experience → Education.
- Thứ tự fresher: Education → Projects → Skills → Experience → Certifications.

## 2. Cấm/tránh (parse-safety)
- Không tables, text-boxes, ảnh, icon, logo, chart, thanh % / sao kỹ năng.
- Không chữ ẩn/trắng để nhồi keyword.
- Không ảnh selfie/đời thường; công ty quốc tế: KHÔNG ảnh + DOB + giới tính + hôn nhân (xem `vn-market.md` §1).
- Không lộ thông tin thừa: CCCD, địa chỉ nhà chi tiết, số tài khoản.

## 3. Typography & xuất file
- **Font system ATS-safe:** Arial, Helvetica 10–12pt body; heading 14–16pt. (CV generator dùng `Arial,Helvetica,sans-serif` — bỏ Georgia/serif để font stack nhất quán.)
- **Ngày:** một format duy nhất mọi chỗ (mm/yyyy). Format lẫn lộn → trừ điểm timeline.
- **File:** text-based PDF (chọn/copy được chữ) hoặc DOCX khi Workday/Taleo yêu cầu. KHÔNG ảnh-only/scanned.
- **Độ dài:** 1 trang khi <10 năm; ≤2 trang cho senior/13+ năm. `ats_check.py` cảnh báo nếu >2 trang hoặc trang 2 lèo tèo.
- **Tên file chuyên nghiệp:** `NguyenVanA-Backend-2026.pdf`, không `CV.pdf`, không `cv-final-final.pdf`.
- **Bullet:** ≤2 dòng (r/ER cho ≤2–3); solid circle/square; không bullet lồng.
- **Keyword trong ngữ cảnh:** mỗi vị trí kết bằng `**Tech:** [...]` (tech thật dùng ở role đó) — keyword trong Experience được ATS/recruiter đánh giá cao hơn chỉ nằm ở Skills. Mỗi tech phải có trong bullet của role hoặc `confirmed: true` (selfcheck check #5).
- **Skills phân tầng:** dòng `**Core:**` đầu tiên (3–6 skill khớp JD nhất), rồi mới tới các nhóm Backend/Frontend/Databases/Cloud.
- **Ngắt trang:** CSS `h3 { break-after: avoid }` + `.meta { break-after: avoid }` + `li { break-inside: avoid }` — không để entry bị cắt đôi hoặc dính chữ khi sang trang.

## 4. Bullet content (impact)
- Công thức **XYZ** (r/EngineeringResumes + Google): *Accomplished X as measured by Y by doing Z*.
- Bắt đầu bằng **strong past-tense action verb** (Led/Owned/Built/Reduced), không "Tham gia/Hỗ trợ/Responsible for".
- Action + công nghệ + kết quả đo được. Số chỉ ghi **số thật** (không bịa).
- Bold chỉ dùng cho tên skill nếu nó vốn được viết đặc biệt; tránh bold rải rác.

## 5. Đối chiếu CV generator hiện tại
| Luật | `render_cv.py` hiện tại | Đạt? |
|---|---|---|
| Single-column | render 1 cột | ✅ |
| Heading chuẩn | Summary/Skills/Experience/Education | ✅ |
| Contact trong body div | ✅ | ✅ |
| Contact 2 dòng (URL không wrap) | ✅ | ✅ (sửa 2026-10-06) |
| Không table/icon/skill-bar | không có | ✅ |
| Font system | `Arial,Helvetica,sans-serif` | ✅ (sửa 2026-10-06) |
| Keyword trong ngữ cảnh (Tech line) | `**Tech:**` mỗi role | ✅ (selfcheck #5, 2026-10-06) |
| PDF text-based | `export_cv.py` (Chrome headless), `/Font` | ✅ |
| DOCX fallback | `export_cv.py --docx` (pandoc) | ✅ |
| Mô phỏng ATS | `ats_check.py` (email/phone/URL, thứ tự section, ngày, header) | ✅ (mới 2026-10-06) |
| Phủ keyword JD | `jd_coverage.py` (ADD/CONTEXT/UNCONF/GAP) | ✅ (mới 2026-10-06) |
| Độ dài | phụ thuộc nội dung; senior có thể tới 2 trang | ⚠️ xem HM (canh 1–2 trang) |
| Bullet ≤2 dòng | có bullet dài | ⚠️ rút khi draft |

## 6. Nguồn & hạn verify
Chi tiết URL + ngày truy cập ở `review-sources.md`. Kiểm tra lại khi ATS vendor đổi hành vi parse (~6 tháng) hoặc r/EngineeringResumes wiki đổi cấu trúc.
