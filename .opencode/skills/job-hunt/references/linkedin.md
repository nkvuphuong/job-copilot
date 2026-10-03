# LinkedIn Jobs — DOM/URL reference (SKELETON — NOT VERIFIED)

> ⚠️ **Chưa verify.** Cấu trúc dưới đây là giả thuyết dựa trên kiến thức chung về LinkedIn Jobs.
> Trước khi dùng: mở LinkedIn trong Chrome (đã login, MCP), xác minh từng mục, sửa lại file này
> rồi đổi tiêu đề thành "verified <ngày>".

## Vì sao LinkedIn khó hơn ITViec

- **Login bắt buộc** (guest search bị chặn / giới hạn). Kể cả khi đã login, LinkedIn chặn pagination sâu.
- **Virtualized / lazy-load list** — không phải phân trang `?page=N`; phải scroll và thu thập dần.
- **DOM obfuscated**: class name kiểu `job-card-container__...` hay đổi; ưu tiên thuộc tính `data-*`
  và link (`a[href*="/jobs/view/"]`) hơn class.
- **Rate limit**: quét nhanh/nhiều trang dễ bị captcha. Duy trì nhịp chậm, số trang nhỏ.

## 1. URL search / filter (giả thuyết)

```
https://www.linkedin.com/jobs/search/?keywords=<kw>&location=<city>&f_E=<level>&f_WT=<worktype>&f_TPR=r604800&start=<offset>
```

| Tham số | Giá trị | Ghi chú |
|---|---|---|
| `keywords` | role/keyword | |
| `location` | `Ho%20Chi%20Minh%20City,%20Vietnam` | |
| `f_E` | experience: `2` entry, `3` associate, `4` mid-senior, `5` director | "Senior" ≈ `4` |
| `f_WT` | work type: `1` onsite, `2` remote, `3` hybrid | lặp được |
| `f_TPR` | time posted: `r604800` = last 7 days | |
| `start` | offset (0, 25, 50, …) | LinkedIn là **phân trang theo offset**, không `page=N` |

## 2. List page — job card (cần verify)

| Field | Cách lấy (giả thuyết) |
|---|---|
| container | `li[data-occludable-job-id]` (data attribute đáng tin hơn class) |
| title + url | `a[href*="/jobs/view/"]` → text; url = href cắt `?` |
| company | `.job-card-container__company-name` hoặc `a[href*="/company/"]` |
| location | `.job-card-container__metadata-item` |
| posted | `<time>` hoặc text "X days ago" |
| salary | thường vắng; nếu có nằm trong metadata |
| id | `data-occludable-job-id` (dùng để dedupe) |

## 3. Detail page (cần verify)

- Ưu tiên mở JD qua click (list→detail dùng cùng origin), hoặc `https://www.linkedin.com/jobs/view/<id>`.
- Không có JSON-LD `JobPosting` như ITViec. Parse DOM:
  - header: `.job-details-jobs-unified-top-card__job-title` / company / location
  - description: `.jobs-description__content` / `.jobs-box__html-content`
  - criteria (level/type): `.job-details-jobs-unified-top-card__job-insight`
- Fallback tổng quát: parse `document.querySelector('main').innerText` (mục "About the job").

## 4. Gotchas

- **Không** cào khi chưa login → dễ chặn.
- `start` offset quay vòng nếu filter quá rộng → cap số trang, dedupe theo `data-occludable-job-id`.
- Salary hiếm khi công khai.
- Snippet list ngắn → Jev preview-screen cần thêm keyword từ title.

## 5. Checklist trước khi đánh dấu verified

- [ ] Đã login, `list_pages` thấy feed LinkedIn.
- [ ] Xác nhận selector container + title/company/location thật.
- [ ] Xác nhận cơ chế phân trang (offset) và cap an toàn.
- [ ] Parse được 1 JD mẫu sang field cấu trúc.
- [ ] Cập nhật tiêu đề file + ngày verify.
