# Rubric chấm điểm CV IT (thang 100)

## Cách chấm
- Mỗi tiêu chí 0–10 điểm → nhân trọng số → cộng lại, làm tròn. **Tổng /100**.
- Chấm độc lập với việc viết lại: điểm là điểm, góp ý là góp ý.
- Không có JD: chấm tiêu chí 1 ở mức "khớp vai trò chung suy ra từ CV" và ghi rõ là ước lượng.

| # | Tiêu chí | Trọng số | 9–10 | 5–6 | 0–2 |
|---|---|---|---|---|---|
| 1 | **Khớp JD** (tech, keyword, level) | 20% | Trùng khớp rõ ràng cả stack chính lẫn level, có bằng chứng | Khớp một phần, thiếu 1–2 tech chính | Sai stack/sai level |
| 2 | **Impact & thành tích** (metric, ownership) | 20% | Hầu hết bullet có kết quả đo được + ownership rõ | Có hành động nhưng ít kết quả/số liệu | Thuần nhiệm vụ, không kết quả |
| 3 | **Cấu trúc & quét 10 giây** (1–2 trang) | 15% | Thông tin khớp JD nằm nửa trên trang 1, phân mục rõ | Đọc được nhưng phải tìm, hơi rối | Wall of text, quá dài, khó quét |
| 4 | **Độ tin cậy kỹ thuật** (stack rõ, link project) | 15% | Stack + level chính xác, có GitHub/portfolio/demo liên quan | Có stack nhưng chung chung, thiếu link | Liệt kê tràn lan, không có bằng chứng |
| 5 | **Progression & ổn định** | 10% | Thấy rõ tăng trách nhiệm/promotion/scope | Có tiến bộ nhưng mờ nhạt | Journeyman, nhảy việc liên tục không giải thích |
| 6 | **Phù hợp thị trường VN** (chuẩn theo loại công ty) | 10% | Đúng chuẩn target (ngôn ngữ, ảnh/DOB, format — xem vn-market.md) | Gần đúng, lệch 1 chi tiết | Lệch hẳn (VD: ảnh+DOB cho công ty quốc tế) |
| 7 | **Trình bày & lỗi** (chính tả, nhất quán) | 10% | Không lỗi, format nhất quán, tên file chuyên nghiệp | Vài lỗi nhỏ | Lỗi chính tả/format nghiêm trọng |

**Bands:** ≥80 Mạnh — "Yes pile" · 65–79 Tốt, sửa vài chỗ · 50–64 Trung bình, sửa nhiều · <50 Viết lại.

## Mô phỏng quét 6–10 giây
Người chấm đóng vai recruiter, chỉ đọc như đang lướt, trả lời:
1. Trong 6–10 giây có thấy được **level + stack + kinh nghiệm liên quan** không?
2. Có thấy **dấu hiệu progression** hoặc thành tích nổi bật không?
3. Có **lỗi chặn đọc** không (wall of text, lỗi chính tả, format lạ)?
→ Kết luận: **Yes / Maybe / No** + 1 câu lý do.

## Anti-patterns (gặp là trừ điểm, nêu rõ trong nhận xét)
- Objective chung chung ("Tìm kiếm cơ hội phát triển bản thân...").
- Bullet mô tả nhiệm vụ, không có kết quả; hoặc mọi bullet đều "Tham gia...".
- Kỹ năng dạng thanh % hoặc sao (5/5 Python) — vô nghĩa với người đọc.
- Liệt kê mọi công nghệ từng chạm, không phân biệt chính/phụ.
- Journeyman: nhiều năm không thấy tăng trách nhiệm.
- Dài 3+ trang khi <5 năm kinh nghiệm; CV fresher 2 trang.
- Ảnh selfie / ảnh đời thường; với công ty quốc tế: có ảnh + DOB + giới tính + tình trạng hôn nhân.
- Lộ thông tin thừa: CCCD, địa chỉ nhà chi tiết, số tài khoản.
- Email/nick không chuyên (vd: `boy9x_pro@...`); tên file `CV.pdf` thay vì `NguyenVanA-Backend-2026.pdf`.
- Lỗi nhất quán: Reactjs/ReactJS/React.js, NodeJS/Node.js, viết hoa lung tung; lẫn EN/VN nửa nọ nửa kia.
- Nhồi keyword không có bằng chứng; hoặc nộp Word dễ vỡ format (khuyến nghị PDF).
- Với local corporate VN: thiếu ảnh/DOB/chứng chỉ theo thông lệ; với công ty quốc tế: thừa các mục đó.

## Ví dụ bullet trước/sau (mẫu format, không phải số liệu thật)
- **Before:** "Tham gia phát triển website bán hàng bằng PHP, hỗ trợ fix bug."
- **After:** "Phát triển module thanh toán (Laravel, MySQL) xử lý ~[số thật] đơn/ngày; giảm [metric thật] bằng cách [cách làm]."
- **Before:** "Làm việc nhóm, sử dụng Docker, Git, Redis, Kafka, AWS, React, Vue..."
- **After:** "Thiết kế pipeline xử lý sự kiện bằng Kafka + Redis cho hệ thống [tên], đạt [độ trễ/thông lượng thật]."
> Luôn hỏi user số liệu thật trước khi viết vào CV — không tự điền.

## Checklist VN theo loại công ty (chạy cuối mỗi lần review)
- [ ] Ngôn ngữ CV khớp JD (EN cho international; VN nếu JD/local corporate yêu cầu).
- [ ] Ảnh/DOB/giới tính đúng chuẩn theo loại công ty (xem `vn-market.md` mục 1).
- [ ] Chứng chỉ ngoại ngữ (TOEIC/IELTS/JLPT/TOPIK) ghi kèm điểm + ngày nếu có liên quan.
- [ ] Link GitHub/LinkedIn hoạt động, không private.
- [ ] Fresher: GPA chỉ đưa khi ở mức tốt; project/đồ án có link.
- [ ] Tên file chuyên nghiệp + định dạng PDF khi nộp.
