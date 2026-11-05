# Cover letter — khung trả lời recruiter (ITviec/TopCV/email)

Dùng khi: JD hoặc recruiter yêu cầu; HOẶC CV có **gap cứng** cần nói trước khi recruiter tự phát hiện
(thiếu 1 tech bắt buộc, lệch domain, lệch level). Không có gap và JD không đòi → **không gửi**
(một thư chung chung làm loãng hồ sơ mạnh).

Ngôn ngữ: theo JD. Độ dài: **≤ 1 trang, 300–400 từ** (đếm cả header). Không lặp lại nguyên CV.

## 1. Khung 4 đoạn

| Đoạn | Nội dung | Độ dài |
|---|---|---|
| 1. Mở | Vị trí + 2 hook khớp JD nhất, mỗi hook 1 câu có số/quy mô thật | 2–3 câu |
| 2. Bằng chứng | Backend/domain mạnh nhất — 1 đoạn liền, không bullet; số thật từ `profile.md` §1b/§4 | 4–6 câu |
| 3. Gap | Nói thẳng cái còn thiếu + bằng chứng gần nhất + mức bù thực tế + "measure me on it" | 3–4 câu |
| 4. Screen + đóng | Bộ 3 câu ở §2, rồi 1 câu đề nghị trao đổi | 4 dòng |

Đoạn 3 là lý do tồn tại của thư. Viết "I have not shipped X in production" — không viết
"familiar with X", không hứa "expert in one week". Nêu khoảng thời gian + tiêu chí để họ đo.

## 2. Bộ 3 câu screen mà ITviec gần như luôn hỏi

Gửi kèm sau khi ứng tuyển: *expected nett salary · current nett salary and position · earliest
date of commencement*. Trả lời **đủ cả 3, đúng thứ tự, in đậm nhãn** để recruiter copy thẳng vào form.
Thiếu 1 mục = bị coi là né tránh và thường bị loại trước khi đọc CV.

```
- **Expected nett salary:** NN–NN million VND per month, net (negotiable depending on scope and package).
- **Current position and nett salary:** <Title> at <Company> (<domain>), <còn làm / contract ended DD Month YYYY>.
  My current net salary is <khoảng NN triệu / "in the range I would rather confirm in a short call than state as a single figure">.
- **Earliest commencement date:** immediate — within N week(s) of an agreement.
```

Luật cho từng mục:
- **Expected:** luôn là **khoảng hẹp** (cách nhau ≤ 5 triệu) + chữ *negotiable*. Đơn vị VND/tháng, ghi rõ *net*.
  Không đưa 1 số cứng (bị khoá trần), không đưa khoảng quá rộng (bị đọc là chưa biết mình muốn gì).
- **Current:** bắt buộc có **cả vị trí và số**. Không muốn nêu số chính xác → vẫn phải nêu vị trí,
  rồi "prefer to confirm in a call" + nêu kỳ vọng ở mục trên. Im lặng bỏ mục là lỗi nặng nhất.
- **Commencement:** ngày cụ thể hoặc `immediate — within N week(s)`. Đừng ghi mâu thuẫn với notice period
  trong `profile.md` §1 — nếu đã hết hợp đồng thì sửa notice period trước khi gửi.

## 3. Luật trung thực

- Mọi số, tech, quy mô lấy từ `profile.md` — y như CV. Không có evidence → không viết.
- Không claim tech chỉ có trong "list kỹ năng". Gap thì mô tả đúng mức: *chưa ship production*, không *chưa từng nghe*.
- Không hứa timeline tuyệt đối cho việc học tech mới; nêu khoảng + tiêu chí đo.
- Kinh nghiệm làm việc tiếng Anh: chỉ nêu việc **đã làm thật** (khách/dự án nước ngoài, spec, PR) —
  không ghi CEFR, không ghi "fluent".

## 4. Nơi lưu

`cv/cover/cover-<company-slug>-<role-slug>-<lang>.md` — sub-folder riêng, local, gitignored (được phép có
tên công ty thật). Tách khỏi `cv/*.md` để `selfcheck_cv.py` / `ats_check.py` / batch export không coi
cover letter là CV.
Xuất PDF riêng (batch `cv/*.md` không quét sub-folder):
`python3 .opencode/skills/vn-it-cv/scripts/export_cv.py cv/cover/cover-<...>.md`

## 5. Template

```
# <Full name>
<City> · <email> · <phone>
<linkedin> · <github>

<Company> — <Team/Department>
Re: <Job title as posted> — <Location>

Dear Hiring Team,

I am applying for the <job title> role <một mệnh đề mục tiêu của sản phẩm/team>.
Two things in the job description match what I have spent most of my career on: <hook 1 — stack/domain
chính, có quy mô>; and <hook 2 — thứ hiếm trong JD mà mình có thật>.

For the backend, <bằng chứng mạnh nhất: sản phẩm + quy mô + quyết định kỹ thuật + kết quả đo được>.
<1–2 câu phụ nếu JD nhấn tiếp một mảng khác — caching, auth, integration, data sync>.

For <mảng còn lại của JD>, <dự án gần nhất cùng hình dạng bài toán — domain hoặc loại hệ thống>.

One thing I want to be direct about rather than have you find later: <gap>. <Bằng chứng gần nhất>.
I would expect <khoảng thời gian> to be fully productive in <công nghệ>, and I am comfortable being
measured on that. <1 câu về cách làm việc với team nước ngoài, nếu JD có>.

Answering your three questions:

- **Expected nett salary:** ...
- **Current position and nett salary:** ...
- **Earliest commencement date:** ...

<1 câu đề nghị trao đổi cụ thể (kiến trúc, 90 ngày đầu)>. Thank you for your time.

Best regards,
<Full name>
```

## 6. Sau khi gửi

Ghi vào DB, đừng để trong đầu:
`python3 tools/jobcopilot/cli.py status <job_id> --to applied --method portal --followup-at <applied+7d>`
