# VietnamWorks — DOM/URL reference (SKELETON — NOT VERIFIED)

> ⚠️ **Chưa verify.** Giả thuyết dựa trên kiến thức chung về VietnamWorks. Xác minh trong Chrome (MCP) trước khi dùng,
> rồi đổi tiêu đề thành "verified <ngày>".

## 1. URL search / filter (giả thuyết)

```
https://www.vietnamworks.com/<keyword-slug>-<location>?page=<n>
```

| Tham số | Giá trị | Ghi chú |
|---|---|---|
| path | `<keyword-slug>` (vd `backend-developer`) | có thể ghép location |
| `page` | số trang | cần verify (1-based) |
| query | có thể hỗ trợ `?q=` | verify |

## 2. List page — job card (cần verify)

| Field | Cách lấy (giả thuyết) |
|---|---|
| container | `.job-item` / `[class*="job"]` |
| title + url | `a[href*="/vi/"]` / `h3 a` → text; href tới `/vi/<slug>-<id>-j` |
| company | `.company-name` |
| salary | `.salary` |
| location | `.location` |
| posted | `.date` / `.time` |

## 3. Detail page (cần verify)

- URL dạng `https://www.vietnamworks.com/vi/<slug>-<id>-j`.
- Kiểm tra `script[type="application/ld+json"]` trước (một số ATS có `JobPosting`); fallback DOM.
- Fallback: `.job-description` → mục mô tả + yêu cầu.

## 4. Gotchas

- VietnamWorks đôi khi redirect qua trang trung gian — kiểm tra URL cuối.
- Có thể yêu cầu login để xem một số JD/ứng tuyển.
- Salary hay ẩn hoặc ghi "Negotiable".

## 5. Checklist trước khi đánh dấu verified

- [ ] Xác nhận selector card + title/company/location.
- [ ] Xác nhận phân trang và URL detail.
- [ ] Kiểm tra JSON-LD có/không; chốt path parse.
- [ ] Parse 1 JD mẫu sang field cấu trúc.
- [ ] Cập nhật tiêu đề file + ngày verify.
