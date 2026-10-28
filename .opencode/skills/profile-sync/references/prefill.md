# Prefill — điền form bằng chrome-devtools MCP

Agent **điền**, người dùng **bấm Save**. Đây là ranh giới không thương lượng.

## Vì sao không viết script selector

`take_snapshot` trả a11y tree kèm `ref` được tính lại mỗi lần chạy, và `fill_form` nhận chính các
ref đó. Nghĩa là **không có selector nào phải lưu trong repo** → nền tảng đổi UI thì không có gì vỡ.
Đừng "tối ưu" bằng `evaluate_script` + CSS selector hardcode.

## ⚠️ Sai sót đã mắc — không lặp lại

Đúc kết từ lượt prefill ITviec/TopCV 2026-10-28. Mỗi dòng là một lỗi **thật đã xảy ra**, không phải
giả định.

| # | Lỗi đã mắc | Hậu quả thật | Luật để không lặp lại |
|---|---|---|---|
| 1 | Thiết kế pack từ search + tài liệu công khai, đánh dấu ITviec/TopCV "chưa verify" rồi vẫn viết pack như thể là form profile | Pack ITviec/TopCV sai hình dạng (giả định có "career objective"; thực tế ITviec = CV builder + About Me 2500 ký tự; TopCV **không có** profile text) | **Snapshot trang thật TRƯỚC khi viết pack.** Không có snapshot = không có field list, chỉ được ghi `chưa verify` và **không** sinh nội dung theo giả định |
| 2 | Điền xong bấm `Close`/`×` để "quay lại sau" | Mất toàn bộ nội dung đã điền — **hai lần** (About Me, rồi Title + LinkedIn) | **Close/Cancel/× = huỷ, không phải lưu.** Điền → screenshot → **để nguyên modal** và bàn giao. Không bao giờ đóng rồi định quay lại |
| 3 | Dùng `ArrowDown` + `Enter` trên combobox để chọn option | Chọn nhầm `Vice President / Director` thay vì `Backend Developer` — dữ liệu sai trên hồ sơ thật | Không dùng phím mũi tên để đoán. Xem kỹ thuật đúng ở mục "Combobox search" bên dưới |
| 3b | Dùng `fill` để đổ chữ vào combobox search | `fill` **không kích hoạt filter** → danh sách vẫn đầy đủ, `Enter` chọn option đầu tiên theo nhóm (`C-level (CTO, CIO, CISO, CDO)`) — sai, phải sửa lại lần 2 | Gõ **từng ký tự** bằng `press_key`: field hiện đúng chuỗi query và list lọc còn 1 option → `Enter` → đọc lại value |
| 4 | Cố `click`/`fill` vào `<select>` bị Tom Select bọc (years / level / industry / currency) | ~6 lần fail liên tiếp; kết luận sai là "không điền được" và ghi vào skill | KHÔNG dùng `click`/`fill`/`press_key` trên loại select này. Dùng công thức `tomselect.open()` → `refreshOptions` → click `.option[data-value]` (§Date picker) |
| 5 | Điều hướng qua lại nhiều trang TopCV trong thời gian ngắn | Cloudflare chặn cả phiên đã đăng nhập (`Sorry, you have been blocked`) | **Mỗi nền tảng một lượt duy nhất**, không nhảy trang qua lại. Bị chặn → dừng hẳn, không retry (retry làm chặn lâu hơn) |
| 6 | Viết "I am currently at <công ty gần nhất>" trong khi `profile.md` đã ghi `end` date trong quá khứ | Hồ sơ nói sai thời điểm hiện tại, NTD đọc thành đang đi làm nơi khác | Trước khi dùng thì hiện tại, **đọc `end` date trong `profile.md` §4**. Hết hạn → "Most recently at …" |
| 7 | Điều hướng trực tiếp tới URL của modal (`/summaries/edit`) | Không mở modal, chỉ render lại trang | Modal chỉ mở bằng **click icon bút chì** trong section, không phải bằng URL |
| 8 | Giả định upload file cần thêm bước submit | ITviec **tự submit** khi chọn file; TopCV thì cần bấm `Tải CV lên` | Sau `upload_file`, **đọc lại trạng thái** (tên file, "last uploaded", status) rồi mới kết luận |
| 9 | Không phân biệt "đã chọn file" và "đã upload" | Dễ báo xong khi file mới chỉ nằm trong input | Kiểm bằng DOM: `input[type=file].files` = đã chọn; danh sách CV của trang = đã upload |
| 10 | **Navigate sang trang khác khi modal còn mở chưa Save** | Mất sạch form vừa điền (phải làm lại từ đầu) | Có modal đang mở = **khoá mọi navigation** trên tab đó. Chỉ được `take_snapshot` + `screenshot`, rồi bàn giao. Điều hướng = đóng = huỷ |
| 11 | Gõ tên thương mại vào field employer autocomplete | Gợi ý lộn xộn, tưởng nền tảng không có công ty | Chọn từ danh sách gợi ý, thử **tên pháp lý tiếng Việt**; xem mục "Field dạng autocomplete" |
| 12 | Thử 4 kỹ thuật liên tiếp trên cùng `<select>` Month/Year rồi kết luận "không điền được" | Mất ~6 tool call, giá trị đổi được = 0, **và ghi sai vào skill** — hai lượt sau vẫn tưởng phải chọn tay | Sau **2 kỹ thuật** thất bại → xem bảng "Field chưa từng điền được" **và** mục Date picker. Nếu widget là Tom Select → dùng công thức ngay, không mò |
| 13 | `new_page` 2 lần rồi `close_page` theo id cũ | **Đóng nhầm tab hồ sơ đang mở modal chưa Save** → mất nguyên form (ngày OMS 09/2020–06/2023) | Trước `close_page`: `list_pages` + so **URL + title** của đúng id. Khi còn form chưa Save: **không mở tab mới, không đóng tab** — chỉ snapshot/screenshot |
| 14 | Tin rằng entry đã có sẵn trên hồ sơ là đúng (ngày, skill) | 5 Project cùng hiện `… – 03/2026`, `01/2020`; skill có `ETL` trùng 2 lần, group 21/20 | Sau khi người dùng Save: **đọc lại DOM** và đối chiếu từng field với `profile.md` §3/§4 (ngày, chức danh, trùng lặp) trước khi báo xong |

## Quy trình chuẩn (áp dụng sau các lỗi trên)

```text
BƯỚC 0  Đọc pack sync/<platform>.md + references/platforms.md (đã verify chưa?)
BƯỚC 1  snapshot trang thật → đối chiếu field với pack; lệch thì SỬA PACK trước, không tự sáng tác
BƯỚC 2  Điền TỪNG field: click → fill → đọc lại value (verify) 
BƯỚC 3  take_screenshot
BƯỚC 4  DỪNG. Nói rõ: "bấm Save giúp tôi" + còn field nào phải làm tay
BƯỚC 5  Người dùng xác nhận đã Save → cli.py sync mark <platform>
```

Một modal một lượt. Nếu còn 2 modal (ví dụ Title và About Me), làm **tuần tự**: điền → người dùng Save
→ mới mở modal tiếp theo. Không gộp.

## Guardrail cứng

| Không được | Vì sao |
|---|---|
| Click Save / Lưu / Cập nhật / Update / Publish / Submit / Đăng / Tải CV lên | Người dùng giữ quyền quyết định cuối; đây là tài khoản thật của họ |
| Đóng modal (Close/×/Cancel) sau khi đã điền | Huỷ sạch nội dung — đã mất 2 lần |
| `evaluate_script` để set value / submit form / dispatch event giả | Vượt validation của nền tảng = dữ liệu bẩn; đây cũng là ranh giới "làm như người dùng" |
| Điền field không có trong `sync/<platform>.md` | Pack là nguồn duy nhất đã duyệt |
| Điền mật khẩu, OTP, thông tin thanh toán | Ngoài phạm vi, rủi ro |
| Vượt captcha / 2FA / Cloudflare / cảnh báo bảo mật | Dừng và báo người dùng; retry làm tình trạng xấu hơn |
| Mở nhiều nền tảng song song, hoặc nhảy trang nhiều lần trên cùng nền tảng | Tăng rủi ro anti-automation; TopCV đã chặn thật |

Gặp bất kỳ màn hình lạ, modal xác nhận, hay cảnh báo: **dừng, screenshot, hỏi người dùng**.

## Chống block — luật chung mọi nền tảng

Block là **hỏng cả phiên**, không phải lỗi lẻ để sửa. TopCV đã chặn thật (2026-10-28). Áp dụng cho mọi
nền tảng, kể cả nền tảng chưa từng chặn.

### Trước khi mở browser

1. **Lập tuyến trước.** Viết ra danh sách trang sẽ mở và field sẽ điền. Tuyến cần >2 trang trong khi
   việc chỉ có 1 hành động → **giao người dùng làm**.
2. **Việc ≤3 thao tác thì người dùng làm ngay từ đầu** (chọn file, bấm 1 nút, đổi 1 toggle).
   Automation ở đây lỗ: giá trị ~0, rủi ro thật.
3. **Ưu tiên API / file thay browser** khi nền tảng có: GitHub README = `git commit`, không phải UI.

### Trong phiên

4. **Snapshot một lần, đọc nhiều lần.** Không `navigate` lại chỉ để xem lại dữ liệu — mine từ snapshot
   đã có. Mỗi lần navigate là một request thật.
5. **Cấm dò URL.** Lấy link thật từ **một** snapshot menu/nav. Không đoán path kiểu
   `/ho-so-ca-nhan`, `/tao-cv` — mỗi 404 vẫn là một request và làm tăng điểm nghi.
6. **Một nền tảng một phiên.** Không mở song song, không nhảy qua lại giữa 2 nền tảng trong một lượt.
7. **Ngân sách điều hướng / phiên** (chỉ tính `navigate_page`, không tính snapshot):

   | Nền tảng | Ngân sách | Cơ sở |
   |---|---|---|
   | TopCV | **1–2** | bị Cloudflare chặn sau ~6 lượt liên tiếp |
   | ITviec | ≤ 6 | ~10 lượt/phiên chưa bị gì |
   | LinkedIn | **≤2 section / phiên**, 1 field / lần Save, ≤4 navigate | checkpoint LinkedIn = chặn **tài khoản**, nặng hơn block IP. Chi tiết: §"LinkedIn — ưu tiên an toàn tài khoản" |
   | GitHub | **0** | dùng `git` / API, không lái browser |

   Vượt ngân sách → dừng, báo người dùng, phần còn lại để họ làm.

### Dấu hiệu dừng ngay (không cần thử thêm)

- HTTP **403 / 429**
- Chữ **"Sorry, you have been blocked"** hoặc trang Cloudflare/WAF
- Redirect sang `/cdn-cgi/…`, `?__cf_chl…`
- Captcha, checkpoint, "verify it's you", 2FA bất thường
- Trang trắng / layout lạ ở nền tảng vừa thao tác bình thường

Gặp **một** trong các dấu hiệu trên → **kết thúc phiên**: screenshot, báo người dùng, **không thử field
khác**, **không retry**.

### Sau khi bị block

8. **Không tự probe lại.** Không mở lại domain để "kiểm tra hết chưa" — chính request đó kéo dài block.
9. Người dùng xác nhận "đã vào được" thì mới tiếp.
10. Recovery đưa cho người dùng (agent không tự làm): chờ 15–30 phút → xoá cookie domain (mất đăng nhập)
    → đổi IP (4G/Wi-Fi khác) → support nền tảng. **Không** VPN rồi login lại ngay.

## LinkedIn — ưu tiên an toàn tài khoản

LinkedIn là nền tảng **duy nhất** trong 4 nền tảng chặn ở tầng **tài khoản** (checkpoint "verify it's you"
→ buộc upload giấy tờ). Đang trong mùa tìm việc thì mất account vài ngày thiệt hại hơn nhiều so với
"đỡ phải copy-paste 10 phút". Vì vậy: **thà để người dùng làm tay** còn hơn lái browser cho đẹp.

### Rủi ro đến từ đâu (3 nguồn, chỉ 1 liên quan tới công cụ)

| Nguồn | Nội dung | Mức |
|---|---|---|
| **Fingerprint kỹ thuật** | headless? `navigator.webdriver`? TLS/JA3? cookie? — browser thật đang đăng nhập thì **sạch** (`webdriver=false`, UA thật, plugin thật) | Thấp |
| **Hành vi** ← *nguồn chính* | 0 mouse move / 0 scroll, text xuất hiện tức thì, click chính xác tâm element, mở 7 modal liên tiếp, timeline đều tăm tắp, thiếu request phụ của SPA | **Cao** |
| **Chính sách + enforcement** | ToS cấm automated access; họ khoá theo heuristic + report, ngưỡng không công bố | Luôn tồn tại |

Hệ quả: **không tồn tại cách "chắc chắn an toàn"**, chỉ giảm xác suất. Và "dùng API cho sạch" là
**ngược**: Voyager API cần `JSESSIONID` + `csrf-token`, request shape khác hoàn toàn traffic SPA, rate
limit chặt theo account, và có thể trả `200` mà **không lưu** (hỏng âm thầm). Không dùng API trực tiếp
cho LinkedIn.

### Phân tầng field — chỉ làm tầng 1 khi chưa có lý do rõ ràng

| Tầng | Field | Vì sao | Ai làm |
|---|---|---|---|
| **1 · an toàn** | Headline (220), About (2600), Location, Contact/Website | 1 modal, 1 request, không typeahead, không date picker | agent điền được |
| **2 · trung bình** | Skills (mỗi skill = 1 request, max 50), Education | nhiều request nhỏ liên tiếp = mẫu bất thường rõ nhất; đổi thứ tự = xoá + thêm lại | người dùng, hoặc ≤5 skill/phiên |
| **3 · rủi ro cao** | Experience (typeahead company + title + date picker + checkbox "currently working here") | nhiều bước trong 1 modal; chọn sai gợi ý → **tạo company entity trùng**; tạo mới nhiều entry liên tiếp = mẫu xấu nhất | **người dùng copy từ pack** |

### Pre-flight (làm trước khi mở browser — không có bước này thì không sửa gì)

1. **Backup**: đọc Headline/About/Experience hiện tại → `sync/linkedin.before.md`. LinkedIn **không có
   undo, không có version history** — ghi đè About là mất bản cũ vĩnh viễn.
2. Người dùng tắt **Settings → Visibility → "Share profile updates with your network"**: mỗi Save bắn
   notification cho toàn network.
3. Chốt các quyết định nội dung **trước** phiên (vd có giữ nhiều entry cùng một công ty không, entry gần
   nhất đã kết thúc thì **bỏ tick** "currently working here") — sửa lại lần hai là thêm 1 phiên rủi ro.
4. Đo fingerprint 1 tool call: `navigator.webdriver`, UA. Nếu `webdriver=true` → **dừng**, không phải
   browser của người dùng.

### Trong phiên

- **≤2 section / phiên**, **≤1 field mỗi lần Save**, **không 2 phiên trong cùng 1 giờ**.
- Chỉ `fill` / `click` qua a11y uid. **Cấm** `evaluate_script` set `value` + `dispatchEvent`
  (`isTrusted=false` — đo được từ phía trang). Widget bắt buộc JS → bàn giao.
- Mỗi field: mở modal → `fill` → `take_screenshot` → **dừng**, người dùng Save → verify bằng DOM →
  mới sang field tiếp.
- Save là live ngay, **không có preview**. Counter không đồng nhất: About **không có** counter,
  Highlights/description của role **có** (`0/2,000`) → field nào không có counter thì tự đếm trước khi `fill`.
  Sau mỗi Save: đọc lại DOM đối chiếu độ dài + nội dung cuối.

## Thứ tự nền tảng & điểm cần biết

| Thứ tự | Nền tảng | Ghi chú riêng |
|---|---|---|
| 1 | **ITviec** | Text thuần điền được (Title, About Me 2500). `<select>` Tom Select **điền được** (§Date picker). Cover Letter **500** ký tự. Skills max 20/group. Upload CV **tự submit**. Modal mở bằng icon bút chì. Close = huỷ |
| 2 | **TopCV** | Không có profile text. Chỉ upload CV: `/upload-cv` → chọn file → **người dùng bấm `Tải CV lên`**. Một lượt duy nhất, không nhảy trang |
| 3 | **GitHub** | Settings → Public profile cho bio; README là file trong repo `<user>/<user>` → **hỏi trước khi commit**; pinned là thao tác UI |
| 4 | **LinkedIn** | Chống automation mạnh nhất, chặn ở tầng **tài khoản**. Chỉ làm field tầng 1 (Headline/About/Location/Contact); Experience + Skills để người dùng. ≤2 section/phiên. Backup trước. §"LinkedIn — ưu tiên an toàn tài khoản" |

## Field dạng autocomplete / entity matching

Áp cho **company, skill, school, location, title** — mọi field có danh sách gợi ý của nền tảng.
Bài học từ ITviec: gõ **tên thương mại** ("Acme") chỉ ra gợi ý lộn xộn; entry thật nằm dưới **tên pháp lý tiếng Việt**
(`CÔNG TY CỔ PHẦN GIẢI PHÁP ACME`). Tên pháp lý thật lấy từ `profile.md` §4, không đoán.

**Luật:**
1. **Không bao giờ để lại text gõ tay.** Luôn chọn từ danh sách gợi ý (suggestion là `button`/`link` →
   click được). Text tự do tạo entity "ma"/trùng lặp và làm hỏng filter của nền tảng.
2. **Thứ tự thử tên:** tên thương mại → **tên pháp lý đầy đủ** (VN: `CÔNG TY CỔ PHẦN …`, `CÔNG TY TNHH …`)
   → tên viết tắt → tên tiếng Anh. Mỗi lần `fill` rồi đọc lại danh sách gợi ý.
3. **Xác nhận đúng entry:** value sau khi click phải bằng **nhãn của suggestion**, không phải chuỗi mình gõ.
   Đọc lại `textbox value` để kiểm.
4. **Không có trong danh sách** → hỏi người dùng, **không** tự tạo entry mới, **không** ghi tên gần đúng.
5. Gợi ý là **button**: `click` được, khác option trong `<select>` bị che (không click được). Phân biệt 2 loại
   này trước khi kết luận "không điền được".
6. Tên hiển thị trên hồ sơ có thể khác `profile.md` (pháp lý vs thương mại) — **không phải sai lệch dữ liệu**;
   đó là ràng buộc của nền tảng. Ghi lại vào `platforms.md` nếu khác thường.

## Combobox search — kỹ thuật đúng (đã kiểm chứng)

Áp cho field có `role=combobox` là `<input type=text>` (ITviec: Job expertise, Month/Year nếu search được).

```text
1. click combobox            -> mở list, input nhận focus
2. press_key từng ký tự      -> "b","a","c","k","e","n","d"
3. take_snapshot / screenshot -> xác nhận list chỉ còn đúng option cần chọn
4. Enter                      -> commit option đang highlight
5. đọc lại value              -> phải đúng nhãn option, không phải chuỗi query
```

- **Không** dùng `fill` cho bước 2 (không filter).
- **Không** dùng `ArrowDown` (không biết highlight đang ở đâu).
- Nếu sau bước 2 list vẫn nhiều option → gõ thêm ký tự cho tới khi còn 1, rồi mới `Enter`.
- Nếu option nằm trong nhóm khác (vd "Web Application Development") → phải lọc, không click được vào option
  trong list (option bị virtualize, `click` fail "did not become interactive").

## Field chưa từng điền được (đừng thử lại)

| Nền tảng | Field | Đã thử | Kết luận |
|---|---|---|---|
| ITviec | General Information: years / level / industry / salary | click, fill, click option, type-ahead | **Người dùng chọn tay** |
| ITviec | Work Experience **và** Highlight Project: From/To Month + Year | ~~người dùng chọn tay~~ → **điền được** bằng công thức Tom Select (xem mục "Date picker Tom Select" bên dưới) | ✅ Đã giải |
| ITviec | Skills — ô `Search skills` (Tom Select) | click, `fill`, `press_key` gõ chuỗi, `Enter`, click option, JS `.focus()` | **Người dùng thêm tay** (gõ chuỗi thì vào được nhưng không commit; option không nhận click; input không nhận focus) |
| TopCV | *(không có form — chỉ upload)* | — | — |

Lý do chung: `<select>` thật bị custom UI che, danh sách option bị virtualize → option không nhận `click`
("did not become interactive"), và key event không tới được `<select>` gốc. Không có cách nào qua
đường "làm như người dùng" → giao người dùng, **không** dispatch event bằng JS.

## Date picker của ITviec — Tom Select bọc `<select>` (ĐIỀN ĐƯỢC)

**Verify 2026-10-28**: đổi `endMonth 3 → 6` và `endYear 2026 → 2023` trên modal Highlight Project,
`select.value` và text `.ts-control` đổi đúng.

Cấu trúc thật: native `<select id="endMonth" name="project[ended_at][month]">` bị Tom Select thay thế
(`class="… tomselected ts-hidden-accessible"`, kích thước **1×1px**, `tabindex=-1`). Control người dùng
thấy là `.ts-wrapper .ts-control`; option chỉ tồn tại trong DOM **sau khi** dropdown mở.

Công thức (4 bước, verify ngay sau đó):

```js
const el = document.getElementById('endMonth');        // id dạng <prefix><Month|Year>
el.tomselect.open();                                    // = click mở dropdown
el.tomselect.refreshOptions(false);                     // render option NGAY (thiếu bước này: 0 option)
el.parentElement
  .querySelector('.ts-wrapper .option[data-value="6"]') // data-value KHÔNG pad số ("6", không phải "06")
  .click();                                             // option thật, có handler của app
// verify: el.value === "6" && .ts-control.innerText === "06"
```

Đừng dùng lại (đều đã fail): `click` theo a11y uid ("did not become interactive"), `press_key` trên
`<select>` (key không tới Tom Select, dù `activeElement` đúng), `fill` trên combobox (fail),
`element.focus()` trên `.ts-control` (focus bị từ chối, trả `false`), `select.value = x` + dispatch
`change` (set value trực tiếp — chỉ dùng nếu người dùng cho phép rõ ràng).

Áp dụng cho: Month/Year của Work Experience & Highlight Project, và mọi `<select>` ITviec khác có
class `tomselected` (General Information: years / level / industry / salary-currency).

## Counter giới hạn: đọc chuỗi đầy đủ, đừng đoán

Counter của ITviec có dạng `1441/500 characters` — **cảnh báo lỗi** nằm ngay cạnh con số giới hạn.
Đã mắc: đọc `1441/500` thành `5000` rồi viết Cover Letter 1441 ký tự → trang báo
*"Please reduce the number of characters"*.

Luật: trước khi viết nội dung dài, **lấy đúng cặp `x/y`** từ DOM (`textContent.match(/\d+\/\d+ characters/)`)
và ghi limit vào pack. Cover Letter ITviec = **500**, About Me = 2500, Experience/Project description = 2500.

## Salary range có validation cặp (ITviec General Information)

- `From` có `data-rule-less-than="#…to_expect_salary"`. Nếu `To` đang là `2.000` (chuỗi có dấu chấm),
  JS parse thành **2.0** → `1500 < 2` false → **field bị xoá trắng**. Đã mắc.
  → **Xoá `To` trước, điền `From` trước, rồi mới điền `To`.**
- `fill` (set value + input) **không** được mask nhận: phải `focus()` + `select()` rồi `press_key` từng chữ số.
  Sau khi gõ, giá trị hiển thị theo dấu chấm nghìn (`1500` → `1.500`).
- Đổi `currency` (VND → USD) có thể **reset** field đã chọn trước đó trong cùng form (đã thấy `Total years`
  về rỗng). Sau khi đổi currency → **đọc lại toàn bộ field** trước khi báo xong.
- Cảnh báo validation cũ (`.invalid-feedback`) **không tự xoá** khi field đã đúng; nó là di chứng của lần
  validate lúc field còn trống. Đừng cố xoá bằng JS — nói người dùng bấm Save, validation sẽ chạy lại.

## Ngoại lệ có điều kiện — control không có accessible name

Có control thật nhưng a11y tree chỉ trả về text (không có `button`/`link` để `click`): ví dụ nút **×** xoá
skill của ITviec (`<span class="core-skill-remove"><svg…></span>`). Khi đó **được phép** gọi
`element.click()` trên chính control đó qua `evaluate_script`, với 4 điều kiện:

1. Là control UI thật của trang (có handler của app), không phải node tự bịa.
2. **Không** set `value`, không dispatch synthetic input/keyboard event.
3. **Không** submit form, không bấm nút lưu.
4. **Verify ngay sau mỗi lần** bằng dữ liệu nhìn thấy được (chip biến mất, counter `21/20 → 15/20`).

Việc này vẫn nằm trong tinh thần "làm như người dùng click" — khác hoàn toàn với nhét value để lách
validation. Nếu control đổi *dữ liệu quan trọng* (xoá hàng loạt, submit) → **hỏi người dùng trước**.

## Khi fill không ăn

Thứ tự thử (dừng ở cách đầu tiên chạy được):

1. `fill` (textarea/input thường)
2. Combobox search được: `click` → `fill` đúng nhãn option → `Enter` → verify
3. Báo người dùng: "field này editor/native select chặn, bạn chọn tay giúp" — **không** dùng JS để nhét giá trị

Sau mỗi lần điền, `take_snapshot` lại để xác nhận text đã vào đúng ô. Đừng tin là đã vào chỉ vì
không có lỗi — đã chọn nhầm option một lần vì đúng lý do này.

## Xác nhận trước khi handover

Screenshot + đọc lại value phải cho thấy: đúng nền tảng, đúng field, text khớp pack. Nếu text khớp
nhưng **field sai** → sửa, chụp lại. Không handover khi chưa chắc.
