# CV Format ATS — luật trình bày cho ngành CNTT

> Đúc kết từ các nguồn uy tín (xem `review-sources.md`): r/EngineeringResumes wiki, ByteByteGo/Gergely Orosz,
> và nhóm ATS guides 2026. Dùng khi render (`render_cv.py`/`export_cv.py`) và khi review layout (`rubric.md` #3, #7).
> Truy cập 2026-10-05.

## 1. Bố cục (bắt buộc)
- **Single-column**, đọc top→bottom. Two-column/sidebar → parser trộn dòng (Greenhouse liệt kê là nguyên nhân parse lỗi). → CV generator phải luôn 1 cột.
- **Heading chuẩn:** Summary, Skills, Experience, Education, Certifications, Projects. Không đặt tên sáng tạo ("My Journey").
- **Contact trong body**, KHÔNG header/footer HTML (nhiều ATS bỏ qua header/footer).
- Thứ tự senior: Header → Summary → (Selected Achievements?) → Skills → Experience → Education.
- Thứ tự fresher: Education → Projects → Skills → Experience → Certifications.

## 2. Cấm/tránh (parse-safety)
- Không tables, text-boxes, ảnh, icon, logo, chart, thanh % / sao kỹ năng.
- Không chữ ẩn/trắng để nhồi keyword.
- Không ảnh selfie/đời thường; công ty quốc tế: KHÔNG ảnh + DOB + giới tính + hôn nhân (xem `vn-market.md` §1).
- Không lộ thông tin thừa: CCCD, địa chỉ nhà chi tiết, số tài khoản.

## 3. Typography & xuất file
- **Font system ATS-safe:** Arial, Calibri, Helvetica, Georgia 10–12pt body; heading 14–16pt. (CV generator dùng `Arial,Calibri,Helvetica,Georgia,sans-serif`.)
- **Ngày:** một format duy nhất mọi chỗ (mm/yyyy). Format lẫn lộn → trừ điểm timeline.
- **File:** text-based PDF (chọn/copy được chữ) hoặc DOCX khi Workday/Taleo yêu cầu. KHÔNG ảnh-only/scanned.
- **Độ dài:** 1 trang khi <10 năm; ≤2 trang cho senior/13+ năm.
- **Tên file chuyên nghiệp:** `NguyenVanA-Backend-2026.pdf`, không `CV.pdf`, không `cv-final-final.pdf`.
- **Bullet:** ≤2 dòng (r/ER cho ≤2–3); solid circle/square; không bullet lồng.

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
| Không table/icon/skill-bar | không có | ✅ |
| Font system | `Arial,Calibri,Helvetica,Georgia` | ✅ (đã sửa 2026-10-05) |
| PDF text-based | `export_cv.py` (Chrome headless), `/ToUnicode` | ✅ |
| DOCX fallback | `export_cv.py --docx` (pandoc) | ✅ |
| Độ dài | phụ thuộc nội dung; senior có thể tới 2 trang | ⚠️ xem HM (canh 1–2 trang) |
| Bullet ≤2 dòng | có bullet dài | ⚠️ rút khi draft |

## 6. Nguồn & hạn verify
Chi tiết URL + ngày truy cập ở `review-sources.md`. Kiểm tra lại khi ATS vendor đổi hành vi parse (~6 tháng) hoặc r/EngineeringResumes wiki đổi cấu trúc.
