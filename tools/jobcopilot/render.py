"""Minimal markdown -> standalone HTML for reading in a browser (stdlib only).

Not a general markdown engine: it covers the shapes our content actually uses
(headings, bullets, bold, inline code, links, tables, paragraphs). Anything
unrecognised falls through as plain escaped text, which renders fine — no crash.

Honesty tags like `[jd]` / `[profile:e0xx]` are plain text and are kept; HTML
comments (`<!-- e001 -->`) are stripped, so no evidence-tripping id leaks.
"""
from __future__ import annotations

import html
import re

_CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body { margin:0; padding:40px 20px; background:#f5f6f8; color:#1d2430;
  font:15px/1.6 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; }
main { max-width:820px; margin:0 auto; background:#fff; border:1px solid #e2e6ec;
  border-radius:12px; padding:36px 44px; box-shadow:0 1px 3px #0000000d; }
h1 { font-size:26px; margin:0 0 4px; } h2 { font-size:18px; margin:28px 0 8px;
  border-bottom:1px solid #e2e6ec; padding-bottom:6px; }
h3 { font-size:15px; margin:20px 0 6px; color:#2b3a4d; }
h4 { font-size:14px; margin:14px 0 4px; }
p { margin:8px 0; } ul { margin:6px 0; padding-left:22px; } li { margin:3px 0; }
code { background:#eef1f5; border-radius:4px; padding:1px 5px; font-size:.9em;
  font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }
a { color:#2f6fd0; }
table { border-collapse:collapse; width:100%; margin:10px 0; font-size:14px; }
th, td { border:1px solid #e2e6ec; padding:6px 9px; text-align:left; vertical-align:top; }
th { background:#f0f3f7; }
hr { border:0; border-top:1px solid #e2e6ec; margin:22px 0; }
blockquote { margin:8px 0; padding:6px 14px; border-left:3px solid #cdd6e0; color:#5a6675; }
.tag { color:#7a8698; font-size:12px; }
"""

_INLINE_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _inline(text: str) -> str:
    out = html.escape(text, quote=False)
    out = _LINK.sub(lambda m: f'<a href="{html.escape(m.group(2), quote=True)}" '
                             f'target="_blank" rel="noopener">{m.group(1)}</a>', out)
    out = _BOLD.sub(r"<strong>\1</strong>", out)
    out = _INLINE_CODE.sub(r"<code>\1</code>", out)
    return out


def to_html(md: str, title: str = "") -> str:
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)  # strip evidence comments
    lines = md.splitlines()
    body: list[str] = []
    i, n = 0, len(lines)
    in_ul = False

    def close_list():
        nonlocal in_ul
        if in_ul:
            body.append("</ul>")
            in_ul = False

    while i < n:
        line = lines[i]
        s = line.strip()

        if s.startswith("|") and i + 1 < n and set(lines[i + 1].strip()) <= set("|-: "):
            close_list()
            header = [c.strip() for c in s.strip("|").split("|")]
            body.append("<table><thead><tr>" +
                        "".join(f"<th>{_inline(c)}</th>" for c in header) +
                        "</tr></thead><tbody>")
            i += 2
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                body.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in cells) + "</tr>")
                i += 1
            body.append("</tbody></table>")
            continue

        h = re.match(r"^(#{1,4})\s+(.*)$", s)
        if h:
            close_list()
            lvl = len(h.group(1))
            body.append(f"<h{lvl}>{_inline(h.group(2))}</h{lvl}>")
            i += 1
            continue

        if re.match(r"^([-*]|\d+\.)\s+", s):
            if not in_ul:
                body.append("<ul>")
                in_ul = True
            item = re.sub(r"^([-*]|\d+\.)\s+", "", s)
            body.append(f"<li>{_inline(item)}</li>")
            i += 1
            continue

        if s.startswith(">"):
            close_list()
            body.append(f"<blockquote>{_inline(s.lstrip('> '))}</blockquote>")
            i += 1
            continue

        if s in ("---", "***", "___"):
            close_list()
            body.append("<hr>")
            i += 1
            continue

        if not s:
            close_list()
            i += 1
            continue

        close_list()
        body.append(f"<p>{_inline(s)}</p>")
        i += 1

    close_list()
    doc_title = html.escape(title or "job-copilot")
    return (f'<!doctype html>\n<html lang="vi"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">'
            f"<title>{doc_title}</title><style>{_CSS}</style></head>"
            f"<body><main>{''.join(body)}</main></body></html>")


def _demo() -> None:
    md = ("# Title\n\n- one **bold** item `code`\n- two [link](https://x.y)\n\n"
          "| A | B |\n|---|---|\n| 1 | 2 |\n\n> quote [jd]\n\n<!-- e001 -->para")
    out = to_html(md, "t")
    assert out.startswith("<!doctype html>")
    assert "<!--" not in out, "comment leaked"
    assert "__UL__" not in out, "list sentinel leaked"
    assert out.count("<ul>") == out.count("</ul>") == 1, "bullet list not closed once"
    assert "<strong>bold</strong>" in out and "<code>code</code>" in out
    assert "<table>" in out and "<blockquote>quote [jd]</blockquote>" in out
    assert 'href="https://x.y"' in out
    print("render selfcheck OK")


if __name__ == "__main__":
    _demo()
