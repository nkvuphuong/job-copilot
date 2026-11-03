# Headline research — đo trước khi viết

> Dùng khi user nói "headline của tôi có ổn không", "sao không ai tìm thấy tôi", "LinkedIn có đề xuất
> tôi cho người khác không", hoặc trước khi viết `Headline` trong pack lần đầu.
> Nguyên tắc: **đo trên tài khoản thật rồi mới viết**, không suy ra từ "best practice" trên blog.
> Mọi con số dưới đây là **placeholder** — số thật của user nằm trong `sync/<platform>.md` (gitignored).

## 0. Câu hỏi cần trả lời trước khi sửa chữ

Headline tác động lên hai thứ **khác nhau**:

| Surface | Headline có vai trò gì | Sửa headline có tác dụng? |
|---|---|---|
| Search (recruiter / people) | Là 1 field được index → khớp keyword | **Có** — đây là lý do duy nhất để tối ưu |
| Card trong kết quả search | Hiện nguyên văn, tạo quyết định bấm | **Có** (CTR) |
| "People also viewed", PYMK, gợi ý kết nối | Chọn ứng viên bằng graph + hành vi | **Không** — đổi chữ vô ích |
| Job suggestion, feed | Dựa vào skills + job preferences | **Không** (dùng pinned skills, không dùng headline) |

→ Nếu phần lớn lượt xuất hiện của user đến từ **network recommendations**, headline **không phải**
nút thắt. Phải nói thẳng điều đó trước khi tối ưu 2.3% còn lại.

## 1. Đo: profile được nhìn thấy từ đâu (bắt buộc, làm trước)

`analytics/search-appearances` và `analytics/profile-views` (cần đăng nhập):

- Tổng số lần xuất hiện, và **tỉ lệ search vs network recommendations**.
- Số profile views / 90 ngày + có bao nhiêu viewer đến từ `Search`.
- Số connections.

Ghi lại kèm ngày. Nếu search < ~10% tổng → nói rõ với user: đòn thật là connections/activity,
headline chỉ tinh chỉnh phần nhỏ. Đừng hứa hẹn bằng headline.

## 2. Corpus phía cầu — từ vựng thị trường của user

- Lấy **JD thật** user đang apply (`jobs/`), đếm token trong **title**: `Engineer` vs `Developer`,
  `Backend` vs `Full-Stack`, `Senior` vs `Principal`, và tên stack có nằm ngay trong title không.
- Đếm nhu cầu trên job board (cùng location + cùng seniority filter, dùng exact phrase):
  `"<title A>"` vs `"<title B>"` vs `A OR B`.
- **Nếu `A + B ≈ A OR B`** → hai pool gần như rời nhau → chọn title nào là **bỏ gần hết** pool còn
  lại → cân nhắc nhét title thứ hai vào ngoặc thay vì chọn một.
- Cảnh báo: corpus JD đã lọc theo tiêu chí của user thì bị **bias**. Đừng dùng nó để kết luận thị
  trường; dùng job board cho con số nhu cầu.

## 3. Corpus phía cung — người đang thắng query

People search 3–5 query (title mục tiêu, title + stack), đọc 10–20 card đầu:

- Card #1 thường là headline **trùng khít chuỗi query** (không thêm chữ). Đây là đòn mạnh nhất đo được.
- Pattern phổ biến: `Title · stack`, `Title | stack | domain | N+ yrs`, `Title @ Company`.
- Đếm xem có bao nhiêu người dùng **ngôi thứ nhất** hoặc câu mô tả ở đầu headline.
- Đọc thêm pool "title thứ hai" (nếu user định thêm) để xem stack của pool đó có phải stack của user
  không. Nếu pool đó toàn công nghệ user không mạnh → **không đứng đầu bằng title đó**.
- Spelling: platform thường normalize biến thể (`Fullstack` / `Full Stack` / `Full-Stack`); kiểm bằng
  cách search biến thể này xem có trả về dạng kia không. Đừng đoán.

## 4. Đo hiển thị thật (đừng tin "60 ký tự")

Đo bằng DOM trên card thật (desktop + mobile):

```js
// với mỗi card: đếm ký tự có rect nằm trong khung của element headline
const rg = document.createRange(); rg.setStart(node, i); rg.setEnd(node, i + 1);
rg.getBoundingClientRect().right <= box.right;   // còn nhìn thấy
```

Kết quả thường gặp: **card search desktop hiện đủ headline** (kể cả >100 ký tự, xuống 2–3 dòng);
cắt thật xảy ra ở surface hẹp (sidebar, invite, comment, mobile). Vì vậy giữ khuyến nghị "keyword
trong ~60 ký tự đầu" — nhưng vì đó là **vùng an toàn cho surface hẹp**, không phải vì search cắt.

## 5. Viết

- **Title của user (chuỗi người ta gõ) đứng đầu**, verbatim, không thêm chữ trước nó.
- `Engineer` vs `Developer`: chọn theo cái thị trường/user gõ nhiều hơn, không theo sở thích.
- **Vùng 60 ký tự đầu = 100% keyword.** Ngôi thứ nhất / động từ dẫn dắt chỉ được nằm **sau** title.
- Stack ngay sau title, ngăn bằng `·` hoặc `,`, 3–5 token (xem `writing-style.md`).
- Không số liệu (trừ khi con số *chính là* định vị — xem `writing-style.md`).
- Title thứ hai (nếu cần bắt pool thứ hai): đặt **trong ngoặc ngay sau title chính** để cụm title
  chính vẫn liền mạch. Dạng `A / B` phá cụm `A` → mất thứ hạng exact-phrase.
- Giới hạn ký tự: `platforms.md`, không lấy từ trí nhớ.

## 6. Đóng vòng — không có bước này thì mọi thứ trên là niềm tin

- Ghi lại **số đo trước** (mục 1) vào `sync/<platform>.md` kèm ngày, cùng headline mới.
- Hẹn đo lại **2–4 tuần**: `search appearances` + tỉ lệ search/network.
- Không nhích → kết luận là **headline không phải nút thắt**, chuyển sang connections/activity/
  pinned skills. Đừng sửa headline lần hai mà không có dữ liệu mới.
