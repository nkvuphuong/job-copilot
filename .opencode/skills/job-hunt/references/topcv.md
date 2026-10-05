# TopCV — DOM/URL reference (verified 2026-10-05)

Cấu trúc trang TopCV để scanner tái sử dụng. **Ưu tiên parse JSON-LD `JobPosting` ở trang detail.**

## 1. URL search / filter

```
https://www.topcv.vn/tim-viec-lam-<keyword-slug>?type_keyword=1&page=<n>
```

| Tham số | Giá trị | Ghi chú |
|---|---|---|
| path | `<keyword-slug>` (vd `backend-developer`) | TopCV dùng slug trong path |
| `type_keyword` | `1` | bật tìm theo keyword |
| `location` | id tỉnh/thành | tuỳ chọn |
| `salary` | id khoảng lương | tuỳ chọn |
| `page` | `1..N` | phân trang chuẩn, **52 card trang 1 / 50 card trang 2** |

> Phân trang `?page=N` hoạt động và cho item khác nhau (verified page 1 vs page 2).

### Lọc theo địa điểm (đã thử, KHÔNG dùng URL filter)

⚠️ **URL filter location của TopCV không lọc sạch** — đừng tin param, hãy lọc client-side:

| Cách thử | Kết quả |
|---|---|
| `?locations=l2lv2` | ❌ keyword bị bỏ, trả mọi ngành ở HCM |
| `/…-tai-ho-chi-minh-l2lv2?locations=l2_l1_l8` | ⚠️ 20/51 HCM (lẫn HN + quảng cáo) |
| `/…-tai-ho-chi-minh` (path) | ❌ 0 job |

**Cách chạy được:** quét list keyword gốc (`?type_keyword=1&page=N`), rồi **lọc `city-text` client-side** (`/hồ chí minh/i.test(loc)`). Verified 2026-10-05: page 1 có 51 card, 12 HCM.

> Hố `?type_keyword=1&location=1` / `&city=…` trả **403** (param sai → chặn) — không dùng.

## 2. List page — job card

Container: `.job-item-search-result` (đếm được ~52/trang). Mỗi card có `data-job-id="<id>"`.

| Field | Selector / cách lấy |
|---|---|
| title | `.title a` → text; url = `href` cắt `?` |
| company | `a.company .company-name` |
| salary | `.info .salary` (fallback `.box-right .title-salary`); hay gặp `Thoả thuận` |
| location | `.info .address .city-text` (vd `Hồ Chí Minh (mới) & 2 nơi khác`) |
| exp | `.info .exp` (vd `Không yêu cầu`, `3 năm`) |
| tags | `.tag .item-tag` |
| posted | `.icon .address.label-update` (vd `Đăng 1 tuần trước`) |
| job id | `data-job-id` (dùng dedupe) |

> `.title a` href dính tracking `?ta_source=...&u_sr_id=...` — **luôn cắt `?`**. Hai param này đã nằm trong `_TRACKING` của `identity.py` nên `url_canonical` tự bỏ.

## 3. Detail page — parse = **JSON-LD** (nguồn chính, verified)

```js
script[type="application/ld+json"]            // 1 node JobPosting
```

| JSON-LD field | Ý nghĩa |
|---|---|
| `title` | tiêu đề |
| `hiringOrganization.name` / `.sameAs` | công ty / trang công ty |
| `datePosted` / `validThrough` | ngày đăng / hết hạn |
| `employmentType` | `FULL_TIME` / `INTERN`... |
| `jobLocation.address.addressLocality` / `.addressRegion` | phường / TP |
| `baseSalary.currency` + `baseSalary.value.value` | lương (`value` dạng text `"Thoả thuận"` khi ẩn) |
| `skills` | CSV string (vd `"Java, Linux, MySQL, Redis, Docker..."`) |
| `occupationalCategory` / `industry` | cấp bậc / ngành |
| `description` | HTML → strip tag để lấy text |
| `jobBenefits` / `employerOverview` | phúc lợi / giới thiệu công ty |

- **Salary bị ẩn** → `baseSalary.value.value == "Thoả thuận"` (không có số).
- **Fetch hàng loạt không cần mở tab**: từ 1 tab topcv.vn, chạy
  `fetch(url, {credentials:'include'})` + `DOMParser` → bóc JSON-LD. (same-origin, cookie tự kèm)

### Snippet chạy được (fetch JSON-LD, trả field thống nhất)

```js
async (url) => {
  const strip = t => (t||'').replace(/<[^>]+>/g,' ').replace(/&nbsp;/g,' ').replace(/\s+/g,' ').trim();
  const res = await fetch(url, {credentials:'include'});
  const doc = new DOMParser().parseFromString(await res.text(), 'text/html');
  for (const s of doc.querySelectorAll('script[type="application/ld+json"]')) {
    let o; try { o = JSON.parse(s.textContent); } catch(e){ continue; }
    const nodes = Array.isArray(o) ? o : (o['@graph'] || [o]);
    for (const n of nodes) if (n['@type'] === 'JobPosting') {
      const addr = (n.jobLocation && n.jobLocation.address) || {};
      const v = (n.baseSalary && n.baseSalary.value) || {};
      return {
        title: n.title, company: n.hiringOrganization && n.hiringOrganization.name,
        skills: (n.skills || '').split(',').map(s => s.trim()).filter(Boolean),
        location: [addr.addressLocality, addr.addressRegion].filter(Boolean).join(', '),
        salary_text: typeof v.value === 'string' ? v.value : '',
        salary_min: v.minValue || (typeof v.value === 'number' ? v.value : 0),
        salary_max: v.maxValue || (typeof v.value === 'number' ? v.value : 0),
        currency: n.baseSalary && n.baseSalary.currency || '',
        datePosted: n.datePosted, validThrough: n.validThrough,
        employmentType: n.employmentType,
        description: strip(n.description || ''),
      };
    }
  }
  return null;
}
```

> Verified 2026-10-05: 1 JD thật (`/viec-lam/senior-backend-developer/2319984.html`) trả đủ field trên.

## 4. Gotchas

- URL detail: `https://www.topcv.vn/viec-lam/<slug>/<id>.html` — id là segment **trước `.html`** (không phải số cuối path). `extract_external_id()` đã hỗ trợ pattern này.
- `.title a` href dính `?ta_source=&u_sr_id=` → cắt `?` trước khi lưu; hai param đã được loc trong `_TRACKING`.
- Salary đa số ẩn (`Thoả thuận`).
- Site tiếng Việt — hỗ trợ cả keyword có dấu và không dấu.
- Có thể có banner/redirect — kiểm tra `location.href` sau khi load (dùng `res.url`).

## 5. Trạng thái

- [x] Xác nhận container card + title/company/location/salary.
- [x] Xác nhận phân trang (`?page=N`) và URL detail.
- [x] JSON-LD `JobPosting` **có** → dùng path 1.
- [x] Parse 1 JD mẫu sang field cấu trúc + `jc add` vào DB thật.
- [x] Ghi nhận URL filter location không dùng được → lọc `city-text` client-side.
- [x] Cập nhật tiêu đề file + ngày verify.
