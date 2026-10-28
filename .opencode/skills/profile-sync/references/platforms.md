# Platforms — field & giới hạn ký tự

> Nguồn giới hạn ghi kèm ngày verify. Nền tảng đổi UI/limit không báo trước → mục nào `chưa verify`
> thì **kiểm tra trên trang thật trước khi khẳng định** với user; mục đã verify vẫn nên so lại nếu
> quá 6 tháng.

## LinkedIn

Verify 2026-10-28 (LinkedIn Help + nhiều nguồn đo editor độc lập, số liệu khớp nhau).

| Field | Giới hạn | Hiển thị trước khi cắt |
|---|---|---|
| Headline | 220 | ~60–70 trong search, comment, invite |
| About | 2600 | ~300 trên profile |
| Experience title | 100 | — |
| Experience description | 2000 / role | — |
| Skill (mỗi skill) | 80 | — |
| Số skill tối đa | 50 | — |

Ghi chú:
- Headline chỉ ~60–70 ký tự hiện trong search → **keyword chính phải nằm trong 60 ký tự đầu**.
- About: ~300 ký tự đầu là "hook"; phần sau chỉ hiện khi bấm "see more".
- LinkedIn **không** cho link bấm được trong About/bio → email ghi dạng text.
- **Không có undo / version history:** ghi đè About là mất bản cũ → backup ra
  `sync/linkedin.before.md` trước khi mở modal.
- **Không có preview:** Save là live ngay, không xem trước được.
- **Counter từng field khác nhau** (verify 2026-10-28): **About: không có counter** → gõ quá 2.600 không
  biết, phải tự đếm. **Highlights/description của role: CÓ counter** (`0/2,000` ngay dưới ô).
- **About vs Highlights**: hai field khác trục — About = *capability*, Highlights = *event + cơ chế*.
  Không bỏ trống field nào, không copy câu. Luật: `writing-style.md` §"About vs Highlights".
  Sau mỗi Save phải đọc lại DOM.
- **Không dùng API trực tiếp (Voyager):** cần `JSESSIONID` + `csrf-token`, request shape khác traffic SPA,
  rate limit theo account, có thể trả `200` mà không lưu. Rủi ro **cao hơn** lái browser.
- **Phân tầng:** *tầng 1* Headline / About / Location / Contact → agent điền được; *tầng 2* Skills /
  Education → người dùng; *tầng 3* Experience (typeahead + date picker + checkbox "currently") →
  người dùng copy từ pack. Chi tiết + pre-flight: `prefill.md` §"LinkedIn — ưu tiên an toàn tài khoản".
- **Ngân sách:** **≤2 section / phiên**, **1 field mỗi lần Save**, **không 2 phiên trong cùng 1 giờ**,
  ≤4 `navigate_page`. Trước phiên đầu: người dùng tắt *"Share profile updates with your network"*
  (mỗi Save bắn notification cho network). Dấu hiệu phải dừng: checkpoint ("verify it's you"), captcha,
  hoặc yêu cầu đăng nhập lại giữa phiên — đây là chặn **tài khoản**, nặng hơn block IP; dừng ngay.

## GitHub

Verify 2026-10-28 (GitHub Docs: "The bio field is limited to 160 characters").

| Field | Giới hạn |
|---|---|
| Bio (plain text, không markdown, không link) | 160 |
| Website (URL) | 255 |
| Profile README (`<user>/<user>/README.md`) | không giới hạn |
| Pinned repos | 6 |

Ghi chú: bio không hỗ trợ link → đặt link ở field Website.
- **Ngân sách:** **0 điều hướng** — bio/README/pinned làm bằng `git commit` + API, không lái browser.
  Chỉ dùng browser khi bắt buộc (pinned repo là thao tác UI).

## ITviec

**Verify 2026-10-28** (đăng nhập thật, đọc DOM + counter trên form).

ITviec **không phải** profile form ngắn — nó là **CV builder** đầy đủ mục
(About Me · Education · Work Experience · Skills · Languages · Projects · Certificates · Awards),
cộng một lớp **CV upload** riêng. Hai thứ này tồn tại song song.

| Field | Nơi sửa | Giới hạn / ghi chú |
|---|---|---|
| Title (headline) | `/profiles/<id>/edit?section_type=contact_info` | đã điền 60 ký tự, không bị cắt; chưa xác định max cứng |
| About Me | `/profiles/<id>/summaries/edit` | **2500 ký tự**, rich text (bold/italic/underline/bullet), counter hiện ngay dưới ô |
| Full name / Phone | Personal details | required |
| Preferred work location | Basic information | **max 3** địa điểm (hiện 1/3) |
| Job expertise | Basic information | required, **multi-select**; option chuẩn: `Backend Developer`, `Fullstack Developer`… |
| Foreign language | Basic information | required (checkbox "No foreign languages" nếu bỏ trống) |
| Total years / Current level / Working model / Industry / Salary | General Information modal | tất cả required; **Industry max 5** |
| CV file | `/profile-cv/manage-cv` | PDF/DOC/DOCX, **≤3MB**, upload **thay thế** CV cũ, tự submit, status `Approved` |
| Cover Letter | `/profile-cv/manage-cv` (inline textarea) | **500 ký tự** (`#user_cover_letter`); không có modal. URL `/cover_letter/edit` **redirect** về `/profile-cv` — đừng mở trực tiếp |
| Skills | modal `Core Skills` | **max 20 / group**; vượt trần → ô `Search skills` **bị disable** |
| Highlight Project | modal `Highlight Project` | Description **2500**; Month/Year là Tom Select |

**Cách điền an toàn (đã thử):**
- Text thuần (title, About) → `fill` trực tiếp vào textbox. OK.
- **`<select>` bị Tom Select bọc** (years / level / industry / currency / Month-Year) → **ĐIỀN ĐƯỢC**,
  xem `prefill.md` §"Date picker của ITviec". `fill`/`click` a11y uid vẫn fail — đừng dùng.
- Job expertise là input search được: `click` → `fill` đúng tên option → `Enter`. **Không** bấm
  ArrowDown+Enter (sẽ nhảy sang option khác — đã mắc lỗi chọn "Vice President / Director").
- ITviec tự upload khi chọn file: không có bước submit riêng.
- **Company trong Work Experience là employer autocomplete:** gõ tên thương mại có thể không ra entry
  chuẩn. Không ra thì gõ **tên pháp lý tiếng Việt** (vd `CÔNG TY CỔ PHẦN GIẢI PHÁP ACME` cho "Acme") —
  ITviec lưu theo tên pháp lý. Gợi ý hiện dưới dạng **button**, click được.
  Tên pháp lý thật luôn lấy từ `profile.md` §4 (dòng `company:`), không đoán.
- **Month/Year của From/To (Experience + Project)** → Tom Select, điền được bằng
  `el.tomselect.open()` → `refreshOptions(false)` → click `.option[data-value="9"]` → verify `el.value`.
- **Ngày có sẵn trên hồ sơ KHÔNG đáng tin:** toàn bộ Project từng hiện `01/2020 – 03/2026` (giá trị mặc
  định do form điền). Luôn đối chiếu từng entry với `profile.md` §4 trước khi kết luận "đã đúng".
- **Nút "Quick update" / "Fill profile from CV"** (ITviec tự trích CV) đã đổ skill rác (`Ajax`, `CSS`,
  `HTML`, `JQuery`, `Angular 4`, `Linux`) và đẩy group lên **21/20**. Không bấm; dùng danh sách skill tự
  soạn từ `profile.md` §3. Nếu đã lỡ: xoá chip qua `.core-skill-remove` (xem `prefill.md` §ngoại lệ),
  kiểm tra **trùng lặp** (đã gặp `ETL` 2 lần) rồi mới thêm skill còn thiếu.
- **Skill group đầy = ô search bị disable**, không phải lỗi tool. Đọc counter `(x/20)` trước khi thử điền.
- **Ngân sách:** ≤ 6 điều hướng / phiên (đã chạy ~10 lượt/phiên chưa bị chặn). Không dò URL trang
  con — lấy link từ snapshot `/profile-cv`.

### Project ≠ Work Experience

Modal Highlight Project tips nói rõ: *project details, your role, technologies, team size* — tức **khung
dự án**, không phải danh sách achievement. Achievement đã có ở Work Experience; chép lại là lỗi đã mắc
(5 bullet Experience → 5 bullet Project, trùng ~90%, NTD đọc 2 lần cùng một thứ).

Chia vai:

| | Work Experience | Highlight Project |
|---|---|---|
| Nội dung | achievement, metric, vai trò theo thời gian | bối cảnh dự án, quy mô, kiến trúc, integrations |
| Metric | nhiều, mỗi bullet 1 metric | **số liệu quy mô** (N orders/year, ~X GB, N sites) **được dùng** — chúng định nghĩa dự án. **Số liệu kết quả** (%, $, thời gian tiết kiệm) để Experience kể |
| Từ vựng | đa dạng theo bullet | **không** dùng lại câu/động từ của bullet Experience |

Template (đã dùng thật, ví dụ đã generic hoá):

```
<1 dòng: dự án là gì, cho ai>
Role: <vai trò trong dự án - sở hữu phần nào, đến đâu (backend/frontend/production rollout)>
Project details:
- <N> production systems: <liệt kê module, không kèm số liệu>
- Architecture: <service + frontend + data + hạ tầng>
- Integration surface: <hệ thống ngoài đã nối>
- Features delivered: <danh sách tính năng, không kèm số liệu>
Technologies: <...>            # dùng chữ "Technologies", không dùng "Stack" (Stack để cho Experience)
```

Thiếu dữ kiện (số trạm, team size, số user) → **hỏi người dùng**, không bịa; tips có nhắc team size nên
điền khi có số thật.

## TopCV

**Verify 2026-10-28.**

TopCV **không có profile text** (không có About Me / headline công khai để paste). Toàn bộ nằm ở
`/quan-ly-cv` với hai khu:

1. **CV đã tạo trên TopCV** — CV builder WYSIWYG (mục: thông tin, mục tiêu nghề nghiệp, kinh nghiệm,
   kỹ năng, học vấn…). Sửa = thao tác trong builder, không phải paste block.
2. **CV đã tải lên TopCV** — upload file qua `/upload-cv`:
   chọn file bằng input `file_upload_cv` → **bấm nút `Tải CV lên`** (submit tường minh, khác ITviec).

Ngoài ra panel phải có toggle **"Đang tắt tìm việc"** — trạng thái người dùng tự bật, agent không đụng.

**Hệ quả cho pack:** `sync/topcv.md` chỉ dùng để (a) upload CV master, (b) copy nội dung từng mục
nếu người dùng muốn dựng CV builder. Không có form để prefill.

**Ngân sách: 1–2 điều hướng / phiên.** Không dò URL, không nhảy trang, không retry sau block.

**⚠️ Rủi ro đã gặp 2026-10-28:** sau ~6 lần điều hướng liên tiếp bằng agent, TopCV trả
`Sorry, you have been blocked` (Cloudflare) — chặn cả phiên đã đăng nhập. Vì vậy với TopCV:
**một lượt duy nhất** (mở `/upload-cv` → chọn file → người dùng bấm `Tải CV lên`), không điều hướng
qua lại nhiều trang, không retry khi bị chặn (retry làm chặn lâu hơn). ITviec chưa gặp hiện tượng này.

## Bảng tên công nghệ chuẩn (dùng chung mọi pack)

Để search và AI matching của nền tảng không trượt. Lấy đúng biến thể đã có trong `profile.md` §3:

`PHP` · `Laravel` · `Slim` · `Golang (Go)` · `Python` · `Node.js` · `Java` · `Spring Boot` ·
`TypeScript` · `JavaScript` · `React` · `Angular` · `MySQL` · `PostgreSQL` · `Redis` · `MongoDB` ·
`ClickHouse` · `Elasticsearch` · `RabbitMQ` · `Kubernetes` · `Docker` · `AWS` · `AWS SQS` ·
`AWS Lambda` · `AWS RDS` · `Cloudflare` · `N8N` · `Metabase` · `Grafana` · `Prometheus` ·
`RESTful API` · `WebSocket` · `ETL/ELT` · `CI/CD`

Không tự thêm biến thể (`Postgres`, `K8s` khi đã viết `Kubernetes`, `Node` khi đã viết `Node.js`).
