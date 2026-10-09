# Project presentation in Experience (ATS + human)

> Đúc kết từ review nội bộ + review ngoài (bản Dekon, 2026-10-06). Áp dụng cho **mọi**
> tailored CV: dự án công ty nằm **trong Experience**, mỗi dự án có **nhãn tên** để cả
> máy (keyword anchor) lẫn người (scan) nhận ra ngay. Dùng cùng `cv-format-ats.md`.

## 1. Công thức một bullet dự án

```
- **<Nhãn dự án>:** <Động từ> + <việc + quy mô> + <tech nếu chưa ở dòng Tech> — <kết quả có số> <!-- e0xx -->
```

- **Nhãn dự án** in đậm ở ĐẦU bullet: tên sản phẩm (`UrBox`, `EzyBook`, `RealtorVietnam`,
  `MyHair`, `iDECAF`, `AZpay`, `Gearment CRM`) hoặc nhãn chức năng ngắn nếu dự án không có
  tên riêng (`AWS migration`, `Customer data migration`, `Performance`, `Reliability`,
  `Reporting`, `Team leadership`).
- Tối đa **2 dòng**; mỗi bullet có **≥1 trong 3**: số liệu · quy mô · một quyết định kỹ thuật cụ thể.
- Viết **"tôi làm gì"** (Built/Owned/Led/Designed), không "team làm gì". Không nâng cấp động từ:
  `Contributed to` giữ nguyên nếu đó là sự thật (đừng đổi thành "Built" khi chưa chắc).

**Ví dụ (chỉ dùng thông tin có trong profile):**
- Trước: `Led DigitalOcean → AWS migration (web: zero downtime; DB: planned 12h window) for the 3M-orders/year platform.`
- Sau: `**AWS migration:** Led the move from DigitalOcean to AWS — zero-downtime web, one planned 12-hour DB window.`
- Trước: `Introduced PostgreSQL for the Customer Portal V3 data layer — schema design, queries, and migration from the legacy MySQL stack.`
- Sau: `**Customer Portal V3:** Introduced PostgreSQL for the data layer — schema, queries, and migration from the legacy MySQL stack.`

## 2. Nhiều vai trò trong một công ty (thăng tiến)

Dùng `#### ` cho từng vai trò — mỗi vai trò có bullet riêng + `**Tech:**` riêng:

```
### Gearment Inc — Technical Lead · 09/2020 – 04/2026
Print-on-Demand B2B SaaS for the US market · 350+ employees · 3M+ orders/year.

#### Technical Lead · 01/2025 – 04/2026
- **AWS migration:** ... <!-- e001 -->
- **Customer data migration:** ... <!-- e003 -->
- **Team leadership:** ... <!-- e004 -->
**Tech:** AWS, DigitalOcean, Docker, Kubernetes

#### Senior Developer · 09/2020 – 06/2023
- **Order Management System (OMS):** ... <!-- e009 -->
- **Performance:** ... <!-- e012 -->
**Tech:** PHP/Laravel, MySQL, PostgreSQL, Redis, MongoDB
```

- Heading `### ` = **công ty + chức danh cao nhất + toàn bộ nhiệm kỳ** (không dùng `/`).
- Liệt kê **đủ các vai trò** (kể cả vai trò concurrent) để **không hở khoảng trống thời gian**.
- Thứ tự trong công ty: vai trò mới nhất trước (reverse-chron theo `start`).

## 3. Luật cứng (ATS + human)

1. **Chức danh không gộp bằng `/`** — "Technical Lead / Senior Developer" bị đọc thành một chức danh sai
   và mất lộ trình. Tách bằng `#### ` (mục 2).
2. **Không dùng ký tự mũi tên `→`** — thay bằng chữ: "from DigitalOcean to AWS".
3. **Không lặp thông tin quy mô** (vd "3M+ orders/year") — giữ **một lần** ở dòng context công ty.
4. **`Tech:` riêng cho mỗi vai trò** — không dùng chung nhiều vai trò; đặt ở dòng riêng (không dính bullet).
   Tech chính của dự án có thể xuất hiện trong bullet; dòng `Tech:` là hợp nhất của vai trò đó.
   **Chỉ chứa tầng A (stack: language/framework/DB/infra/platform).** KHÔNG đưa practices
   (Agile/CI-CD/TDD/DDD/Spec-Driven Development), tools (Jira/Bitbucket/…) hay concepts (OOP/MVC/Design
   Patterns) vào `Tech:` — chúng thuộc nhóm Skills riêng (`cv-format-ats.md` §3).
5. **Thứ tự bullet theo độ liên quan**: dự án/kết quả lớn nhất trước, mảng **quản lý** (review/hiring/KPI)
   đặt **sau cùng**.
6. **Viết tắt định nghĩa ở lần đầu**: `Order Management System (OMS)`, `Profit & Loss (PnL)`,
   `Business Intelligence (BI)`, `Progressive Web App (PWA)`.
7. **Nhất quán tên dự án** toàn CV: chốt một tên cho Portal — `Customer Portal (Portal App)` lần đầu,
   sau gọi `Portal`.
8. **Dự án cá nhân/open-source** để ở `## Side Projects` (không phải dự án công ty).

## 4. Khi thiếu dữ liệu (số liệu/quy mô)

**Luật: KHÔNG ước lượng.** Số ước lượng có thể lệch nhiều → phá honesty guarantee + rủi ro khi phỏng vấn
(interviewer hỏi ngược không defend được → mất credibility toàn CV).

**Test một dòng:** *"Tôi dám bảo vệ con số này khi bị hỏi ngược không?"* — Không chắc → **bỏ số**.

Một bullet **không có số vẫn đạt** luật "≥1 trong {số · quy mô · quyết định kỹ thuật}" nếu có **quy mô
định tính** hoặc **quyết định kỹ thuật**:

- **Quy mô định tính:** `multi-module`, `end-to-end (DB → UI → deploy)`, `role-based portals`,
  `offline-capable`, `POS + payment + maps/search integrations`, `regulated fintech domain`.
- **Quyết định kỹ thuật:** `separate DB`, `schema migration`, `transaction-management refactor`, `AES-GCM at rest`.
- **Vai trò:** `built` / `owned` / `architected` / `from scratch`.
- **Proxy hợp lệ nếu NHỚ:** thời lượng (`over 5 years`), team size (`with a 4-dev team`).

**Cây quyết định:**

```
Có số thật (dám defend)? ── có ──▶ dùng (ghi "~" nếu là range bạn chắc)
        │ không
        ▼
Dự án còn liên quan JD? ── có ──▶ giữ bullet ĐỊNH TÍNH (quy mô chữ + quyết định kỹ thuật + vai trò)
        │ không
        ▼
     Nén 1 dòng HOẶC bỏ (tailor) — KHÔNG tạo "section phụ" (dễ bị đọc là padding)
```

- **KHÔNG bịa.** Placeholder `[cần xác nhận: ...]` chỉ dùng ở **bản nháp**, **phải giải quyết trước khi
  render PDF cuối** (không để lọt vào CV gửi đi).
- **Muốn có số thật?** Lục artefact cũ — git history, DB dump, tên khách hàng, hoá đơn, file cấu hình.
  Có thì dùng, không thì thôi (giữ định tính).
- **Dự án outsource/chưa thương mại** (không có user-scale thương mại): dùng proxy **định tính** ở trên;
  chỉ thêm số nếu có artefact xác nhận.

## 5. Nguồn
- Nội bộ: review `render_cv.py`/template + `profile.md` §4 (2026-10-06).
- Ngoài: review bản Dekon (2026-10-06) — nhãn dự án, tách vai trò, chức danh `/`, mũi tên `→`,
  lặp scale, Tech dùng chung, công thức bullet.
