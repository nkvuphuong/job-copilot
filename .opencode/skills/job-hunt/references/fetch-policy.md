# Fetch policy — throttle + Cloudflare (429/403) cho scan

> Đúc kết từ scan 2026-10-09 (ITViec + TopCV). Áp dụng cho **mọi** board fetch bằng
> `chrome-devtools` MCP. Nguồn chân lý chung cho `itviec.md` / `topcv.md` / các board khác.

## 1. Vì sao (case đã gặp)

| Board | Hành vi | Chi tiết |
|---|---|---|
| **ITViec** | Burst `fetch` detail → **HTTP 429** | 12 request OK rồi 19 request bị chặn. Header `cf-mitigated: challenge`, body = trang Cloudflare *"Just a moment..."* (`_cf_chl_opt`), **KHÔNG có `Retry-After`**. Parser đọc HTML challenge → `"no JSON-LD"` = **mất dữ liệu âm thầm**. |
| **TopCV** | `fetch` **list** → **HTTP 403** | `/tim-viec-lam-<kw>?type_keyword=1&page=N` trả 403 mọi trang (anti-bot); **detail `fetch` → 200**. |

Cả hai đều là **Cloudflare bot-mitigation**, không phải rate-limit thuần. Không có `Retry-After` để chờ theo.

## 2. Luật cứng

1. **Throttle, đừng burst:** ≤ **1 request / 1.5s** mỗi origin; **batch ≤ 8 URL / lần script**; jitter 300–700ms.
   - Verified: burst 31 → 12 OK + 19×429; throttle 1.5s → 31/31 OK.
2. **List = `navigate_page` + DOM; Detail = throttled `fetch`.**
   - ITViec + TopCV list đều chạy được bằng navigate (document load vượt challenge). TopCV list **bắt buộc** navigate (fetch → 403).
3. **Phát hiện challenge/403 — KHÔNG coi là rỗng.** Đánh dấu `blocked` (khác `no JSON-LD`):
   `res.status ∈ {403,429}` **hoặc** body chứa `cf-mitigated` / `Just a moment` / `_cf_chl_opt`.
4. **Khi `blocked`:** chờ **5–10s** cho browser giải challenge rồi retry (tối đa 2–3); vẫn chặn → **fallback `navigate_page`** + parse DOM.
5. **Chunk + checkpoint:** xử lý ~8–10 detail/lần, checkpoint sau mỗi chunk (challenge giữa chừng không mất cả batch).
6. **Không im lặng:** trả counts `{ok, blocked, retried, skipped}`, log URL bị chặn (vào `runs.counts_json`), và báo user *"N JD bị Cloudflare chặn, chưa lấy được"*.

## 3. Snippet tái dùng — `throttledFetch`

Chạy từ **1 tab cùng origin** (cookies/`cf_clearance` tự kèm). Trả `{ok|blocked|error}` thay vì nhầm challenge thành dữ liệu rỗng.

```js
// params: { urls:[...], gapMs:1500, maxRetry:3 }
async (params) => {
  const { urls, gapMs = 1500, maxRetry = 3 } = params;
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const jitter = () => 300 + Math.floor(Math.random() * 400);
  const isChallenge = (status, text) =>
    status === 403 || status === 429 ||
    /cf-mitigated|Just a moment|_cf_chl_opt/i.test(text);
  const out = [];
  for (const url of urls) {
    let rec = { url, status: 'error' };
    for (let attempt = 0; attempt <= maxRetry; attempt++) {
      try {
        const r = await fetch(url, { credentials: 'include' });
        const text = await r.text();
        if (isChallenge(r.status, text)) {
          rec = { url, status: 'blocked', http: r.status, attempts: attempt + 1 };
          await sleep(5000 + attempt * 3000);   // chờ browser giải challenge
          continue;
        }
        rec = { url, status: 'ok', http: r.status, html: text };
        break;
      } catch (e) { rec = { url, status: 'error', error: String(e) }; }
    }
    out.push(rec);
    await sleep(gapMs + jitter());
  }
  return out;
}
```

**Fallback khi vẫn `blocked`:** `navigate_page` tới URL đó (document load), rồi parse DOM/JSON-LD từ trang đang mở — chậm hơn nhưng không dính 403/challenge như `fetch`.

## 4. Số liệu đã verify (2026-10-09)

- ITViec: burst 31 fetch → 429 từ request #13. Throttle 1.5s + retry 3 → 31/31 OK.
- TopCV: list `fetch` 403; list `navigate_page` + DOM OK; detail `fetch` 200.
