---
name: profile-sync
description: Sinh và đồng bộ "profile pack" từ profile.md lên LinkedIn, ITviec, TopCV, GitHub — mỗi nền tảng một file copy-paste đúng giới hạn ký tự, kèm prefill bằng chrome-devtools MCP (người dùng tự bấm Save) và theo dõi drift. Dùng khi user nói "cập nhật LinkedIn", "sync profile", "cập nhật hồ sơ ITviec/TopCV", "viết lại bio GitHub", "profile pack", "hồ sơ bị lệch", "re-sync".
license: MIT
compatibility: opencode
metadata:
  audience: vietnamese-it-jobseekers
  outputs: linkedin, itviec, topcv, github
---

# Profile Sync — profile.md → nền tảng

`profile.md` là **nguồn sự thật duy nhất**. Skill này chỉ **chọn / sắp xếp / viết lại** nội dung
cho phù hợp từng nền tảng, không bao giờ thêm kinh nghiệm, số liệu hay kỹ năng mới.

**Base dir:** thư mục chứa skill này (`.opencode/skills/profile-sync/` trong repo `job-copilot`).

**Files:**
- `references/platforms.md` — field + giới hạn ký tự từng nền tảng, kèm trạng thái verify
- `references/writing-style.md` — cách viết cho từng nền tảng (khác nhau thật, không dùng chung template)
- `references/prefill.md` — điền form bằng `chrome-devtools` MCP, dừng trước nút Save
- `scripts/pack_check.py` — gate: vượt giới hạn ký tự hoặc evidence id không tồn tại → fail

**Output:** `sync/<platform>.md` (gitignored — dữ liệu cá nhân).

## Bước 0 — Routing

| User nói | Workflow |
|---|---|
| "cập nhật LinkedIn", "sync profile", "làm pack cho ITviec/TopCV/GitHub" | **GENERATE** |
| "điền giúp tôi lên LinkedIn/ITviec", "prefill" | **PREFILL** (cần pack có sẵn) |
| "tôi đã lưu rồi", "đánh dấu đã sync" | **MARK** |
| "hồ sơ có lệch không", "profile đổi rồi" | **DRIFT** |
| Không rõ | Hỏi: muốn tạo pack, điền form, hay kiểm tra drift? |

## GUARDRAILS (bắt buộc, mọi workflow)

1. **KHÔNG BAO GIỜ bấm nút lưu.** Không click Save / Lưu / Cập nhật / Update / Publish / Submit /
   Đăng / Apply — kể cả khi user bảo bấm. Người dùng luôn tự bấm. Không có ngoại lệ.
2. **Không bịa.** Mọi bullet/số liệu phải trace về `profile.md` và mang `[eNNN]`. Thiếu thông tin →
   hỏi hoặc để `[cần xác nhận: ...]`, không tự điền.
3. **Chỉ skill `confirmed: true`** trong `profile.md` §3 được đưa vào pack. Skill `exploring` /
   `confirmed: false` → không.
4. **Không đổi ngày tháng, chức danh, tên công ty** — lấy nguyên từ §4.
5. **Ngôn ngữ output: EN** (đã chốt), kể cả cho ITviec/TopCV. Giao tiếp với user: tiếng Việt.
6. **Không auto-publish, không upload thay người dùng.** Upload CV là thao tác của người dùng
   (agent có thể chọn file qua `upload_file`, nhưng không bấm nút xác nhận cuối).
7. **Giới hạn ký tự lấy từ `references/platforms.md`**, không lấy từ trí nhớ. Mục nào ghi
   `chưa verify` thì phải kiểm tra trên trang thật trước khi khẳng định.
8. **Không đưa lên hồ sơ công khai:** CEFR tự đánh giá, work authorization/sponsorship,
   mức lương mong muốn (guardrail 3b của `vn-it-cv`).
9. **Verify trước khi viết, không đoán:** chưa `take_snapshot`/đọc DOM trang thật thì **không** được
   sinh pack theo giả định. Pack sai hình dạng = mất cả lượt prefill.
10. **Đóng modal = huỷ dữ liệu.** Đã điền thì để nguyên cho người dùng Save; không Close/×/Cancel
    rồi định quay lại. Một modal một lượt.
11. **Mỗi nền tảng một lượt duy nhất**, không nhảy trang qua lại (TopCV đã chặn Cloudflare vì việc này).
12. Danh sách lỗi đã mắc + quy trình đúng: `references/prefill.md` mục "Sai sót đã mắc — không lặp lại".
    **Giới hạn thử:** 2 kỹ thuật / nhóm control là đủ để đổi cách làm; riêng `<select>` bị Tom Select bọc
    thì dùng ngay công thức 4 bước ở mục "Date picker của ITviec" — không thử mò lại.
    Đọc mục đó **trước** mọi lần prefill.
13. **Tuân ngân sách điều hướng + dừng khi có dấu hiệu block** (`references/prefill.md` mục
    "Chống block"). Gặp 403/429, Cloudflare/WAF, captcha, checkpoint → **kết thúc phiên**, không retry,
    không probe lại. Việc ≤3 thao tác → để người dùng làm ngay từ đầu.
14. **Work Experience vs Highlight Project — không lặp nội dung.** Achievement/metric thuộc Work
    Experience. Highlight Project chỉ mô tả **bối cảnh · quy mô · vai trò · kiến trúc · integrations ·
    team size** + tối đa 1 metric mạnh nhất. Copy bullet Experience sang Project là lỗi đã mắc (trùng
    ~90%): `references/platforms.md` §ITviec, mục "Project ≠ Work Experience".
15. **Tab = dữ liệu chưa lưu.** Khi còn form/modal chưa Save: **không** `new_page`, **không** `close_page`,
    không navigate. Trước khi đóng bất kỳ tab nào: `list_pages` và so **URL + title** với id định đóng
    (đã đóng nhầm tab hồ sơ vì id đổi sau `new_page` → mất form vừa điền).
16. **LinkedIn — an toàn tài khoản trên hết.** Chặn ở LinkedIn là chặn **tài khoản** (checkpoint, buộc
    upload giấy tờ), không phải block IP. Không có "chắc chắn an toàn", chỉ giảm xác suất →
    đọc `references/prefill.md` §"LinkedIn — ưu tiên an toàn tài khoản" **trước** khi mở browser.
17. **LinkedIn: cấm JS ghi giá trị.** Không `evaluate_script` để set `value` rồi `dispatchEvent` (sự kiện
    `isTrusted=false` — đo được từ phía trang). Chỉ `fill` / `click` qua a11y uid. Widget nào **bắt buộc**
    JS mới điền được (như Tom Select) → **bàn giao người dùng**, không lách.
18. **LinkedIn: ngân sách tính bằng số lần Save,** không chỉ `navigate_page`: **≤2 section / phiên**,
    **≤1 field mỗi lần Save**, và **không 2 phiên trong cùng 1 giờ**. Vượt → dừng, hẹn phiên sau.
20. **LinkedIn: sau khi Save phải verify, không tin form.** Đọc lại top card + entry vừa sửa: **headline**
    (LinkedIn ghi đè thành `{title} at {company}` khi thêm role), trạng thái `current role`, và giá trị
    typeahead (`Location` từng tự đổi thành một huyện). Checklist 7 dòng: `prefill.md` §"LinkedIn — kỹ thuật
    đã kiểm chứng trên form thật".
19. **LinkedIn: backup trước khi sửa.** LinkedIn **không có undo / version history** — ghi đè là mất.
    Bắt buộc: đọc Headline/About/Experience hiện tại → lưu `sync/linkedin.before.md` (gitignored) →
    rồi mới mở modal. Người dùng tắt **"Share profile updates with your network"** trước phiên đầu
    (mỗi Save bắn notification cho network).


## Workflow GENERATE

1. Đọc `profile.md` (§1 Meta, §1b Positioning, §3 Skills, §4 Experiences, §5 Projects, §6 Education).
2. Đọc `references/platforms.md` + `references/writing-style.md`.
3. Nếu `sync/<platform>.md` đã tồn tại: đọc để giữ giọng văn đã duyệt, chỉ cập nhật phần lệch.
4. Sinh/cập nhật pack theo format field-block:

   ````
   ## Field name  <!-- limit: 220 -->
   ```text
   nội dung
   ```
   ````

   Chỉ gắn `<!-- limit: N -->` khi biết giới hạn thật. Không ghi số ký tự vào file — script tự đếm
   (số ghi tay sẽ lệch ngay sau lần sửa đầu tiên).
5. Chạy gate: `python3 .opencode/skills/profile-sync/scripts/pack_check.py [sync/<platform>.md]`
   → phải in `PACK CHECK OK`.
6. Báo user: field nào đã đổi, field nào cần họ quyết định (vd chọn repo để pin), và nhắc bước tiếp
   (PREFILL hoặc tự paste).

## Workflow PREFILL

Theo `references/prefill.md`. Tóm tắt: `navigate_page` → `take_snapshot` → `fill_form`/`fill` →
`take_screenshot` → **dừng**, user bấm Save → `jc sync mark <platform>`.

## Workflow MARK / DRIFT

```bash
python3 tools/jobcopilot/cli.py sync mark <platform> [--at YYYY-MM-DD]
python3 tools/jobcopilot/cli.py sync status
python3 tools/jobcopilot/cli.py sync drift
```

`mark` chỉ chạy **sau khi user xác nhận đã lưu**. `drift` so hash `profile.md` hiện tại với
`profile_hash` lưu lúc mark → nền tảng nào cần re-sync.

## Không làm (YAGNI)

- Không quản lý ảnh đại diện, banner, cover, theme hồ sơ.
- Không viết nội dung repo con, không tạo repo mới.
- Không theo dõi reach/impression (không có API công khai ổn định).
- Không hỗ trợ nền tảng ngoài LinkedIn / ITviec / TopCV / GitHub (VietnamWorks, TopDev… → hỏi trước).
