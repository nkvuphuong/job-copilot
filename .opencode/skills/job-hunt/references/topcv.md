# TopCV — DOM/URL reference (SKELETON — NOT VERIFIED)

> ⚠️ **Chưa verify.** Giả thuyết dựa trên kiến thức chung về TopCV. Xác minh trong Chrome (MCP) trước khi dùng,
> rồi đổi tiêu đề thành "verified <ngày>".

## 1. URL search / filter (giả thuyết)

```
https://www.topcv.vn/tim-viec-lam-<keyword-slug>?sba=&type_keyword=1&salary=...&location=...
```

| Tham số | Giá trị | Ghi chú |
|---|---|---|
| path | `<keyword-slug>` (vd `backend-developer`) | topcv dùng slug trong path |
| `location` | id tỉnh/thành (vd HCM) | |
| `salary` | id khoảng lương | |
| `page` | số trang | |

> TopCV thường có **phân trang chuẩn** (`?page=N`) nhưng tổng số item/page cần verify.

## 2. List page — job card (cần verify)

| Field | Cách lấy (giả thuyết) |
|---|---|
| container | `.job-item-search-result` |
| title + url | `.title a` / `h3 a` → text; href tới `/viec-lam/...` |
| company | `.company-name` / `a[href*="/cong-ty/"]` |
| salary | `.salary` |
| location | `.location` / `.address` |
| tags | `.tag` |
| posted | `.time` / `.label` |

## 3. Detail page (cần verify)

- URL dạng `https://www.topcv.vn/viec-lam/<slug>/<id>.html`.
- Không chắc có JSON-LD `JobPosting` — kiểm tra `script[type="application/ld+json"]` trước, fallback DOM.
- Fallback: `.job-description` / `.job-detail` → các mục "Mô tả công việc", "Yêu cầu ứng viên".

## 4. Gotchas

- Site tiếng Việt — keyword search nên có cả dạng không dấu và có dấu.
- Salary đôi khi hiện dạng text ("Thương lượng", "Cạnh tranh").
- Có thể có banner/redirect — kiểm tra `location.href` sau khi load.

## 5. Checklist trước khi đánh dấu verified

- [ ] Xác nhận selector card + title/company/location.
- [ ] Xác nhận phân trang và URL detail.
- [ ] Kiểm tra JSON-LD có/không; chốt path parse.
- [ ] Parse 1 JD mẫu sang field cấu trúc.
- [ ] Cập nhật tiêu đề file + ngày verify.
