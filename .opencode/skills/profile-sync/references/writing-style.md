# Writing style — theo từng nền tảng

Cùng một `profile.md`, bốn cách đọc khác nhau. Sai style là mất tín hiệu dù nội dung đúng.

## Nguyên tắc chung (mọi nền tảng)

- **Metric trước, tính từ sau.** "−95% data errors" đọc mạnh hơn "cải thiện đáng kể độ chính xác dữ liệu".
- **Không sáo rỗng:** passionate, hard-working, team player, detail-oriented, "chăm chỉ, chịu khó" → xoá.
- **Không liệt kê khái niệm ai cũng biết** (OOP, MVC, SOLID) — đọc là junior/padding.
- **Động từ chủ động ở đầu bullet** (Built, Led, Cut, Migrated, Rebuilt), thì quá khứ.
- **Một bullet = một kết quả.** Không nhồi 3 việc vào một câu.
- **Không lặp lại quy mô công ty trong mọi bullet** — nói 1 lần ở phần mô tả, sau đó chỉ nói kết quả.

## LinkedIn

Người đọc: recruiter lướt 3 giây, rồi headhunter search bằng keyword.

- **Headline**: 60 ký tự đầu phải đứng một mình được — `Senior Backend Engineer · 13+ years`. Sau đó
  mới là stack + một tín hiệu quy mô. Không nhồi 10 công nghệ; 4–6 là đủ.
- **About**:
  1. Câu 1 (trong ~300 ký tự đầu) = hook có số liệu, không phải "I am a passionate developer".
  2. 3–5 bullet "what I am hired to do", mỗi bullet một loại việc (hiệu năng / migration / dữ liệu / delivery).
  3. 1 đoạn ngắn về công việc gần nhất.
  4. Stack + địa điểm/timezone + CTA liên hệ.
  - Xuống dòng bằng dòng trống (LinkedIn giữ line break). Ký tự bullet `•` an toàn.
- **Experience description**: 4–6 bullet, kèm 1 dòng context (domain + stack) ở đầu. Không copy nguyên
  About vào đây.
- **Skills**: 20–35 skill, xếp theo mức ưu tiên của `profile.md` §2 Targeting (thứ tự hiển thị = thứ tự bạn chọn).

## ITviec

Người đọc: recruiter IT Việt Nam + **AI MatchScore** của ITviec.

- Tên công nghệ **chuẩn hoá** theo bảng trong `platforms.md` — đây là yếu tố ảnh hưởng match score.
- **Career objective**: mở bằng con số quy mô, rồi bullet kết quả, cuối là stack + địa điểm + notice.
  Không quá 1 trang màn hình.
- **Work experience**: mỗi công ty 3–6 bullet, bullet dài vừa (1–2 dòng), số liệu đứng cạnh động từ.
- **Skills**: nhóm theo backend / database / devops / data, viết dạng danh sách phẳng để filter khớp.
- Bỏ hẳn ngoại ngữ (CEFR), work authorization, lương.

## TopCV

Người đọc: recruiter đa ngành (không chỉ IT) — cần dễ đọc hơn, ít thuật ngữ hơn.

- **Mục tiêu nghề nghiệp** là field quan trọng nhất: số năm + domain + giá trị mang lại + mong muốn
  vị trí + ngắn hạn/dài hạn. Không viết "mong muốn làm việc trong môi trường năng động, chuyên nghiệp".
- **Skills**: ghi nhóm + công nghệ, vì TopCV ít filter theo từng skill tag hơn ITviec.
- **Kinh nghiệm**: bullet ngắn hơn ITviec, giữ số liệu nhưng bỏ chi tiết kỹ thuật quá sâu.
- Nếu nền tảng cho upload CV: **upload CV master**, không upload bản tailor cho 1 JD.

## GitHub

Người đọc: engineer, mở repo để xem code viết thế nào.

- **Bio (160)**: công thức `role · years · stack · một tín hiệu quy mô`. Không link (không bấm được).
- **README**: đọc như landing page, không phải CV.
  - Mở bằng 2–3 dòng về loại hệ thống mình làm, có quy mô.
  - "Things I've actually shipped" — 3–5 bullet có số.
  - Stack 1 dòng.
  - "Currently building" — repo đang làm, kèm 1 câu mô tả.
  - Liên hệ.
  - Không badge trang trí, không GitHub stats card nếu nội dung đã đủ.
- **Pinned**: chỉ repo bạn dám để người khác đọc code. Ưu tiên backend / hệ thống / có README + test.

## Chuyển ngữ

Pack là EN nhưng SoT `profile.md` có phần viết VN (§1b headline, bullet mixing VN/EN). Khi dịch:
**dịch nghĩa, giữ nguyên số liệu, ngày, tên công ty, tên công nghệ**; không "làm đẹp" con số, không
đổi đơn vị, không gộp hai bullet thành một câu mạnh hơn thực tế.
