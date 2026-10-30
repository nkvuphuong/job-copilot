# ITViec — DOM/URL reference (verified spike 2026-10)

Cấu trúc trang ITViec để scanner tái sử dụng. **Ưu tiên parse `body.innerText` khi DOM đổi.**

## 1. URL search / filter

```
https://itviec.com/it-jobs/<city-slug>?query=<keyword>&job_level_names[]=Senior&job_level_names[]=Manager&working_models[]=hybrid&page=<n>
```

| Tham số | Giá trị | Ghi chú |
|---|---|---|
| **city** | path segment: `ho-chi-minh-hcm`, `ha-noi`, `da-nang` | **KHÔNG** dùng `?city=` (bị bỏ qua). Bỏ trống = toàn quốc. |
| `query` | keyword (vd `full-stack`) | có thể bỏ trống |
| `job_level_names[]` | `Internship`, `Fresher`, `Junior`, `Senior`, `Manager` | lặp lại được. "Lead" ≈ `Manager` |
| `working_models[]` | `onsite`, `remote`, `hybrid` | |
| `job_domain_ids[]` | numeric | lấy từ page; ít dùng |
| `page` | `1..N` | phân trang, 20 job/trang |
| `job_selected` | slug | ITViec tự thêm sau khi load (auto-select) — bỏ qua |

> **KHÔNG virtualized**: 20 card render thẳng, phân trang `?page=N` (KHÔNG infinite-scroll).

## 2. List page — job card

Container: `.job-card` (20/trang).

| Field | Selector / cách lấy |
|---|---|
| title | `.job-card h3 a[href*="/it-jobs/"]` → text; url = `href` cắt `?` |
| company | `.job-card a[href*="/companies/"]` (chọn phần tử CÓ text); fallback `[data-bs-original-title]` |
| salary | phần tử lá có text khớp `/(USD\|VND\|Cạnh tranh\|Thương lượng\|Sign in to view\|\$\|₫)/`; class thường `span.ips-2.fw-500`; rỗng → `?` |
| job function | `.job-card .imt-1.d-flex.align-items-center` (cái KHÔNG có `text-dark-grey`) |
| work model + location | `.job-card .imt-1.d-flex.align-items-center.text-dark-grey` → text dạng `"At office Ha Noi"` / `"Hybrid"` / `"Remote Ho Chi Minh - Da Nang"`. Tách: work model = regex `/\b(At office\|Onsite\|Hybrid\|Remote)\b/`, còn lại = location |
| tags | `.job-card .itag` (loại bỏ `+N`) |
| posted | `.job-card .small-text.text-dark-grey` (cái đầu) |
| badge | `.job-card .ilabel` (`HOT` / `SUPER HOT`) |

## 3. Detail page — parse = **JSON-LD** (nguồn chính, robust)

```js
script[type="application/ld+json"]            // JobPosting (có thể nằm trong @graph)
```

| JSON-LD field | Ý nghĩa |
|---|---|
| `title` | tiêu đề |
| `hiringOrganization.name` | công ty |
| `datePosted` / `validThrough` | ngày đăng / hết hạn |
| `employmentType` | `FULL_TIME`... |
| `skills` | CSV string (vd `"PHP, PostgreSql, JavaScript"`) |
| `jobLocation[0].address.addressLocality` / `.addressRegion` | quận / TP |
| `baseSalary.currency` + `baseSalary.value.{minValue,maxValue,value}` | lương |
| `description` | HTML → strip tag để lấy text |

- **Salary bị ẩn** → `baseSalary.value.text == "You'll love it"` (không có min/max) — kể cả khi đã login.
- **Fetch hàng loạt không cần mở tab**: từ 1 trang itviec.com, chạy
  `fetch(url, {credentials:'include'})` + `DOMParser` → bóc JSON-LD. (same-origin, cookie tự kèm)

### Fallback DOM (khi job thiếu JSON-LD, vd Nami 1822)

| Field | Selector |
|---|---|
| header | `.job-show-header` → `h1`, `.employer-name`, `.salary` (`span.ips-2.fw-500`) |
| sections | `.jd-main div.paragraph` (h2: "Job description", "Your skills and experience", "Why you'll love working here") |

**Snippet chạy được** (fetch + parse cả 2 path, trả field thống nhất; chạy từ 1 tab itviec.com bất kỳ):

```js
async (url) => {
  const strip = (t) => t.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim();
  const res = await fetch(url, {credentials:'include'});
  const doc = new DOMParser().parseFromString(await res.text(), 'text/html');

  // path 1: JSON-LD
  let ld = null;
  for (const s of doc.querySelectorAll('script[type="application/ld+json"]')) {
    try {
      const o = JSON.parse(s.textContent);
      const nodes = Array.isArray(o) ? o : (o['@graph'] || [o]);
      for (const n of nodes) if (n['@type'] === 'JobPosting') {
        const addr = (n.jobLocation && n.jobLocation[0] && n.jobLocation[0].address) || {};
        const v = n.baseSalary && n.baseSalary.value || {};
        ld = {
          title: n.title, company: n.hiringOrganization && n.hiringOrganization.name,
          skills: (n.skills || '').split(',').map(s => s.trim()).filter(Boolean),
          location: [addr.addressLocality, addr.addressRegion].filter(Boolean).join(', '),
          salary_min: v.minValue || v.value || 0, salary_max: v.maxValue || v.value || 0,
          currency: n.baseSalary && n.baseSalary.currency || '',
          description: strip(n.description || ''),
        };
      }
    } catch(e) {}
  }
  if (ld) return ld;

  // path 2: fallback DOM
  const q = (s, r=doc) => r.querySelector(s);
  const txt = (el) => el ? el.textContent.replace(/\s+/g,' ').trim() : '';
  const h = q('.job-show-header');
  const sects = {};
  doc.querySelectorAll('.jd-main div.paragraph').forEach(p => {
    const h2 = txt(p.querySelector('h2'));
    if (h2) sects[h2] = strip(p.innerHTML);
  });
  const sal = txt(h && (h.querySelector('.salary') || h.querySelector('span.ips-2.fw-500')));
  return {
    title: txt(h && h.querySelector('h1')), company: txt(h && h.querySelector('.employer-name')),
    skills: [], location: '', salary_min: 0, salary_max: 0, currency: '',
    salary_text: sal, description: Object.values(sects).join(' '),
  };
}
```

> Verified 2026-10: cả 2 path trả field thống nhất. JD thiếu JSON-LD → path 2 bắt được `salary_text` (dạng `"1,300 - 1,600 USD"`) mà JSON-LD có thể giấu.

## 4. Gotchas

- **Cloudflare challenge khi burst fetch:** fetch detail dồn dập (không delay) → sau ~12 request trả **429** với header `cf-mitigated: challenge` (body là trang *"Just a moment..."*, KHÔNG phải JSON-LD). Throttle **1.5s + batch ≤8 + retry**; vẫn chặn → `navigate_page`. Chi tiết + snippet: `fetch-policy.md`.
- Company logo link có thể **rỗng text** → chọn `a[href*="/companies/"]` có text.
- Level filter không có link sẵn → phải dùng query param `job_level_names[]`.
- Một số JD **thiếu JSON-LD** → fallback DOM mục 3.
- Salary: đa số ẩn (`You'll love it`); chỉ job nhà tuyển dụng công khai mới có số.

## 5. Agency postings — employer bị che

ITviec có các job đăng qua chính chi nhánh tuyển dụng của họ (`ITviec Recruitment Consulting`). Trang company là
**công ty tuyển dụng**, không phải employer → `industry: Staffing and Recruiting`, `company size: 1-50`, và
`jobLocation.addressLocality` thường **rỗng hoặc `Not Available`** trong khi bản trực tiếp của cùng employer ghi rõ quận.

Dấu hiệu trên JD: mở đầu bằng "công ty sản phẩm 100% vốn đầu tư nước ngoài…" thay vì tên công ty; nêu **quy mô team**
và **danh sách phân hệ được chọn**; bar kinh nghiệm có thể **cao hơn** bản gốc (vd 5 năm → 6 năm + 1 năm lead);
JD **ngắn hơn** (một cặp đã kiểm: ~3.900 vs ~5.700 ký tự `description`).

Cách xử lý:

1. `dedupe-check` **không** bắt được cặp này (khác `company_slug` + `title_norm`) → chạy
   `dedupe-check '<url>' --jd-file jobs/<id>.md`: tool so token *số + đơn vị* / acronym trong JD và trả
   `repost_candidates` + `probable_employer [infer]`. Cặp agency ↔ bản trực tiếp của cùng employer (cặp đã kiểm): score **0,92**, 12 JD còn lại 0
   false positive. Theo luật repost ở `job-hunt/SKILL.md` mục "Trước khi score": **mỗi listing một row**
   (dedupe_key `itviec:<id>` riêng, title đúng như tin đăng), nối bằng `duplicate_of` chỉ sau khi so **scope**
   — fingerprint phúc lợi chỉ xác định *khách hàng*, không xác định *vacancy*.
2. Lấy employer thật từ JD (tên sản phẩm, gói phúc lợi đặc trưng) để chấm domain; không nêu tên → `[confirm]`.
3. So `JSON-LD.validThrough` của hai listing và nộp **một lần** ở cửa sổ còn hạn lâu hơn.
4. Địa chỉ làm việc: agency hay giấu → lấy từ bản trực tiếp của cùng employer, đừng suy từ "City, Ho Chi Minh".
