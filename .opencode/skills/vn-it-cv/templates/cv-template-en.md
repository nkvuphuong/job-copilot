<!-- CV Template — International (EN)

Hướng dẫn điền:
- Thay [...] bằng nội dung thật; KHÔNG bịa số liệu — chỗ nào chưa có số, ghi [cần xác nhận: ...]
- 1 trang nếu <3 năm kinh nghiệm; tối đa 2 trang.
- Bullet experience theo công thức: Action verb + việc làm (tech) + kết quả đo được.
- Xóa toàn bộ comment HTML này trước khi xuất PDF.
- Dòng đầu tiên bắt buộc là `# [FULL NAME]` (render_cv.py lấy dòng `# ` ĐẦU TIÊN làm tên). -->

# [FULL NAME]
[Target title — khớp JD, VD: Senior Backend Engineer (Java/Go)]

[City, Vietnam] · [email chuyên nghiệp] · [SĐT]
[github.com/username] · [linkedin.com/in/username]
<!-- KHÔNG mặc định thêm dòng Languages/Work-auth. Quy ước:
     - Không ghi CEFR tự đánh giá (A2–B1…) và không ghi work-authorization/sponsorship lên CV.
     - Năng lực tiếng Anh thể hiện qua kinh nghiệm thật (khách/dự án quốc tế) trong Summary/Experience.
     - Chỉ khi JD là REMOTE cho công ty NGOÀI VN: thêm 1 dòng `Time zone: GMT+7` (overlap giờ làm việc). -->

## Summary
[2–3 dòng, tailor theo JD: số năm kinh nghiệm + domain + stack chính + 1 thành tích nổi bật. Không dùng câu sáo rỗng.
 Lấy từ profile.md §1b Positioning: chọn 1 headline + 2–3 hero metric — KHÔNG tự nghĩ số mới.]

## Selected Achievements
<!-- Tùy chọn, dùng khi có ≥3 thành tích định lượng mạnh. 3–5 bullet, mỗi bullet 1 `<!-- e0xx -->`.
     Đây là phần thắng trong 6–10s scan đầu tiên. Bỏ nếu experience đã tự nổi bật. -->
- [Thành tích định lượng mạnh nhất] <!-- e0xx -->
- [...]

## Skills
- **Core:** [3–6 skill khớp JD nhất, có bằng chứng]
- **[Nhóm]:** [...]
<!-- Chỉ để tech thật sự dùng được trong công việc; xếp theo mức liên quan JD.
     Core = những gì JD cần nhất, lên đầu để lọt scan. CHỈ list skill `confirmed: true` trong profile.md §3.
     Skill `confirmed: false` (list-only/exploring) → KHÔNG list; selfcheck_cv.py sẽ chặn. -->

## Experience

### [Company] — [Title] · [Start – End]
[1 dòng context: sản phẩm/domain, team size, scope nếu hữu ích]
- [Action verb] + [việc làm + tech] + [kết quả có số] <!-- e0xx -->
- [...]
- [...]
**Tech:** [các tech THẬT SỰ dùng ở role này — mỗi cái phải có trong bullet trên hoặc `confirmed: true`]

### [Company] — [Title] · [Start – End]
- [...]
**Tech:** [...]

## Projects
<!-- Fresher/junior: đưa section này LÊN TRƯỚC Experience. Senior: có thể bỏ nếu experience đã đủ mạnh. -->
### [Project name] — [link]
[1 dòng mục tiêu project] · Stack: [...]
- [Đóng góp cá nhân + kết quả] <!-- e1xx -->

## Education
**[Bachelor of Science in Information Technology]** — [University] · [Start – End]
[GPA nếu ≥ 7.5/10 hoặc ≥ 3.0/4.0; bỏ nếu thấp hơn]

## Certifications
- [Chứng chỉ + điểm + năm — chỉ cái liên quan JD]
