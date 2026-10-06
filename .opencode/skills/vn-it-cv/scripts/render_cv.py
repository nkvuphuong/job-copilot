#!/usr/bin/env python3
"""Render a tailored CV Markdown -> print-ready HTML (A4, Cmd+P -> Save as PDF).

Source of truth is the .md. This is a small, dependency-free converter that
understands the fixed shape emitted by the vn-it-cv templates:

    # Name
    Target title
    <blank>
    contact line(s) (· separated, may contain markdown links; one or more lines,
                       each rendered on its own row — keep URLs from wrapping)
    <blank>
    ## Section
    ### Heading            (company / role heading, or plain heading)
    <context line>         -> rendered as .meta (immediately after an ###)
    - bullet
    - bullet <!-- e001 -->  (evidence comments are stripped)

Usage:
    python3 render_cv.py cv/foo-en.md            # writes cv/foo-en.html
    python3 render_cv.py cv/*.md                 # batch
    python3 render_cv.py cv/foo-en.md out.html
"""

import html
import re
import sys
from pathlib import Path

_COMMENT = re.compile(r"<!--.*?-->", re.S)
_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_MD_LINKSLASH = re.compile(r"(?<![\w/])(github\.com/[\w.-]+|linkedin\.com/in/[\w.-]+|[\w.\-]+@[\w.\-]+\.\w+)(?![\w/])")

_HEAD = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  :root {{ --ink:#1a1a1a; --muted:#555; --rule:#d9d9d9; --accent:#0f4c81; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; color:var(--ink); font:13.5px/1.5 Arial,Helvetica,sans-serif; background:#f3f3f3; }}
  .page {{ width:210mm; min-height:297mm; margin:12px auto; padding:16mm 15mm; background:#fff; }}
  header {{ border-bottom:2px solid var(--accent); padding-bottom:10px; margin-bottom:14px; }}
  h1 {{ font-size:24px; margin:0 0 2px; letter-spacing:.3px; }}
  .title {{ color:var(--accent); font-weight:600; font-size:14px; margin-bottom:6px; }}
  .contact {{ color:var(--muted); font-size:12.5px; }}
  .contact a {{ color:var(--muted); text-decoration:none; }}
  h2 {{ font-size:13px; text-transform:uppercase; letter-spacing:1.1px; color:var(--accent); margin:16px 0 6px; border-bottom:1px solid var(--rule); padding-bottom:3px; }}
  h3 {{ font-size:14px; margin:10px 0 1px; break-after: avoid; }}
  .meta {{ color:var(--muted); font-size:12px; margin:0 0 4px; break-after: avoid; }}
  ul {{ margin:4px 0 8px; padding-left:18px; }}
  li {{ margin-bottom:3px; break-inside: avoid; }}
  p {{ margin:4px 0; }}
  .skills p {{ margin:2px 0; }}
  a {{ color:var(--accent); text-decoration:none; }}
  @media print {{ body{{background:#fff;}} .page{{width:auto;min-height:auto;margin:0;padding:0;}} @page{{size:A4;margin:14mm 13mm;}} }}
</style>
</head>
<body>
<div class="page">
"""

_TAIL = """</div>
</body>
</html>
"""


def _inline(text: str) -> str:
    """Escape, then apply the only two inline constructs the CVs use."""
    text = html.escape(text, quote=False)
    text = _LINK.sub(r'<a href="\2">\1</a>', text)
    text = _BOLD.sub(r"<strong>\1</strong>", text)
    return text


_ENTRY_HEADING_SECTIONS = ("education", "certifications", "certifications and languages",
                           "languages", "projects", "selected achievements")


def _is_entry_heading(section: str) -> bool:
    """A bold paragraph acts as a sub-heading in these sections (not + pending meta)."""
    return section.strip().lower() in _ENTRY_HEADING_SECTIONS


def _contact(text: str) -> str:
    """Contact line: emit links, then auto-linkify bare github/linkedin/email."""
    text = _inline(text)

    def _auto(m):
        v = m.group(1)
        if "@" in v and not v.startswith("mailto:"):
            return f'<a href="mailto:{v}">{v}</a>'
        return f'<a href="https://{v}">{v}</a>'

    return _MD_LINKSLASH.sub(_auto, text)


def render(md_path: Path) -> str:
    raw = md_path.read_text(encoding="utf-8")
    raw = _COMMENT.sub("", raw)  # drop evidence_id comments before anything else
    lines = raw.splitlines()

    name = ""
    target = ""
    contact_lines = []
    # --- header block: # Name / Target title / (blank) / contact (1..n lines) ---
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith("# "):
            name = s[2:].strip()
            i += 1
            break
        i += 1
    header_rest = []
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith("## "):
            break
        if s:
            header_rest.append(s)
        i += 1
    if header_rest:
        target = header_rest[0]
    contact_lines = header_rest[1:]

    lang = "vi" if md_path.stem.endswith("-vn") else "en"
    title = " — ".join(p for p in (name, target, "CV") if p)
    out = [_HEAD.format(lang=lang, title=html.escape(title), name=html.escape(name))]

    # --- header ---
    out.append("  <header>")
    out.append(f"    <h1>{html.escape(name)}</h1>")
    if target:
        out.append(f'    <div class="title">{_inline(target)}</div>')
    if contact_lines:
        joined = "<br>".join(_contact(line) for line in contact_lines)
        out.append(f'    <div class="contact">{joined}</div>')
    out.append("  </header>")

    # --- body ---
    mode = None  # None | 'ul' | 'skills'
    pending_meta = False
    section = ""
    for line in lines[i:]:
        s = line.strip()
        if not s:
            continue
        if s.startswith("### "):
            if mode == "ul":
                out.append("</ul>")
                mode = None
            pending_meta = True
            out.append(f"<h3>{_inline(s[4:].strip())}</h3>")
        elif s.startswith("## "):
            if mode == "ul":
                out.append("</ul>")
            if mode == "skills":
                out.append("</section>")
            mode = None
            pending_meta = False
            section = s[3:].strip()
            label = section.lower().replace(" & ", " and ").replace("/", "").strip()
            if label in ("skills", "technical skills", "core skills", "skills and tools"):
                out.append('<section class="skills"><h2>' + html.escape(section) + "</h2>")
                mode = "skills"
            else:
                out.append(f"<h2>{html.escape(section)}</h2>")
        elif s.startswith("- "):
            if section.lower() in ("skills", "technical skills", "core skills", "skills and tools"):
                out.append(f"<p>{_inline(s[2:].strip())}</p>")
            else:
                if mode is None:
                    out.append("<ul>")
                    mode = "ul"
                out.append(f"<li>{_inline(s[2:].strip())}</li>")
        else:  # paragraph / meta line
            if mode == "ul":  # e.g. a `**Tech:**` line closing out a bullet list
                out.append("</ul>")
                mode = None
            if _BOLD.search(s) and not pending_meta and _is_entry_heading(section):
                out.append(f"<h3>{_inline(s)}</h3>")
                pending_meta = True
            elif pending_meta:
                out.append(f'<p class="meta">{_inline(s)}</p>')
                pending_meta = False
            else:
                out.append(f"<p>{_inline(s)}</p>")

    if mode == "ul":
        out.append("</ul>")
    if mode == "skills":
        out.append("</section>")

    out.append(_TAIL)
    return "\n".join(out)


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    # explicit output path only for `render_cv.py <in.md> <out.html>` (2 args, last not .md)
    explicit_dst = len(argv) == 2 and not argv[1].endswith(".md")
    for arg in (argv[:-1] if explicit_dst else argv):
        src = Path(arg)
        dst = Path(argv[1]) if explicit_dst else src.with_suffix(".html")
        html_out = render(src)
        assert "<!--" not in html_out and "&lt;!--" not in html_out, f"comment leaked into {dst}"
        dst.write_text(html_out, encoding="utf-8")
        print(f"{src} -> {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
