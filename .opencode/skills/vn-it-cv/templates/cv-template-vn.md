<!-- CV Template — VN corporate style

Hướng dẫn điền:
- Dùng template này khi target: local corporate / SME / bank / telco / nhà nước (xem vn-market.md mục 1).
- Thay [...] bằng nội dung thật; KHÔNG bịa số liệu — chỗ chưa có ghi [cần xác nhận: ...]
- Ảnh thẻ 3×4 (nền sáng, chuyên nghiệp) chèn ở góc phải phần thông tin cá nhân — không selfie.
- Xóa comment HTML trước khi xuất PDF.
- Dòng đầu tiên bắt buộc là `# [HỌ VÀ TÊN]` (render_cv.py lấy dòng `# ` ĐẦU TIÊN làm tên). -->

# [HỌ VÀ TÊN]
[Vị trí ứng tuyển — khớp JD]

## Thông tin cá nhân
- Ngày sinh: [dd/mm/yyyy] · Giới tính: [Nam/Nữ]
- Điện thoại: [...] · Email: [email chuyên nghiệp]
- Địa chỉ: [Quận/Huyện, Tỉnh/Thành phố — không cần số nhà] · Quê quán: [nếu JD/thông lệ yêu cầu]
- GitHub: [...] · LinkedIn: [...]
- Ngoại ngữ: [Tiếng Anh] <!-- KHÔNG ghi level CEFR tự đánh giá; KHÔNG ghi dòng "Quyền làm việc" -->
- [Ảnh thẻ 3×4]

## Mục tiêu nghề nghiệp
[2–3 dòng, gắn với vị trí: số năm kinh nghiệm + stack chính + giá trị mang lại. Tránh câu sáo rỗng.
 Lấy từ profile.md §1b Positioning — không tự nghĩ số mới.]

## Thành tích nổi bật
<!-- Tùy chọn: 3–5 thành tích định lượng mạnh, mỗi bullet 1 `<!-- e0xx -->`. Bỏ nếu kinh nghiệm đã đủ nổi bật. -->
- [Thành tích định lượng] <!-- e0xx -->

## Kỹ năng
- **Core:** [3–6 skill khớp JD nhất, có bằng chứng]
- **[Nhóm]:** [...]
<!-- Core = những gì JD cần nhất, lên đầu để lọt scan. CHỈ list skill `confirmed: true` trong profile.md §3.
     Skill `confirmed: false` (list-only/exploring) → KHÔNG list; selfcheck_cv.py sẽ chặn. -->


## Kinh nghiệm làm việc

### [Công ty] — [Chức danh] · [Bắt đầu – Kết thúc]
[1 dòng bối cảnh: sản phẩm/domain, quy mô team]
- [Động từ hành động] + [việc làm + công nghệ] + [kết quả đo được] <!-- e0xx -->
- [...]
**Tech:** [các tech THẬT SỰ dùng ở role này — mỗi cái phải có trong bullet trên hoặc `confirmed: true`]

### [Công ty] — [Chức danh] · [Bắt đầu – Kết thúc]
- [...]
**Tech:** [...]

## Dự án
<!-- Fresher: đưa lên trước Kinh nghiệm làm việc -->
### [Tên dự án] — [link nếu có]
[1 dòng mục tiêu] · Công nghệ: [...]
- [Đóng góp cá nhân + kết quả] <!-- e1xx -->

## Học vấn
**[Cử nhân Công nghệ Thông tin]** — [Trường] · [Bắt đầu – Kết thúc]
[GPA nếu ≥ 7.5/10 hoặc ≥ 3.0/4.0; bỏ nếu thấp hơn]

## Chứng chỉ
- [Ngoại ngữ: TOEIC/IELTS/JLPT/TOPIK + điểm + năm]
- [Chuyên môn: AWS/Google/Azure... nếu liên quan JD]
