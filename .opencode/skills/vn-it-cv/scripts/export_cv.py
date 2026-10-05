#!/usr/bin/env python3
"""Export tailored CV Markdown -> text-based PDF (and optional DOCX).

Reuses render_cv.render() for the HTML, then drives headless Chrome to print
it to PDF. Chrome is the only reliable zero-dependency HTML->PDF engine already
present on macOS/Linux dev machines; no LaTeX, weasyprint or wkhtmltopdf needed.

    python3 export_cv.py cv/foo-en.md              # -> cv/foo-en.pdf
    python3 export_cv.py cv/*.md                   # batch -> one PDF each
    python3 export_cv.py cv/foo-en.md --docx        # also cv/foo-en.docx (pandoc)

The PDF is text-based (selectable), which is what an ATS parser needs.
"""

import html as _html
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_cv  # noqa: E402

_CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "chromium",
    "chromium-browser",
]


def _find_chrome() -> str:
    for c in _CHROME_CANDIDATES:
        if Path(c).exists():
            return c
        found = shutil.which(c)
        if found:
            return found
    raise SystemExit("Chrome/Chromium not found — install Google Chrome or Chromium.")


def to_pdf(md: Path, dst: Path) -> None:
    html = render_cv.render(md)
    chrome = _find_chrome()
    with tempfile.TemporaryDirectory() as td:
        htmp = Path(td) / "cv.html"
        htmp.write_text(html, encoding="utf-8")
        subprocess.run(
            [chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
             "--print-to-pdf=" + str(dst), "file://" + str(htmp)],
            check=True, capture_output=True,
        )
    data = dst.read_bytes()
    assert data[:5] == b"%PDF-", f"not a PDF: {dst}"
    # A text-based PDF embeds fonts; a rasterized one has only image XObjects.
    assert b"/Font" in data, f"PDF has no embedded text layer: {dst}"
    print(f"{md} -> {dst}")


def to_docx(md: Path, dst: Path) -> None:
    if not shutil.which("pandoc"):
        print(f"skip docx (pandoc not installed): {md}", file=sys.stderr)
        return
    subprocess.run(["pandoc", str(md), "-o", str(dst)], check=True)
    print(f"{md} -> {dst}")


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    want_docx = "--docx" in argv
    args = [a for a in argv if a != "--docx"]
    for arg in args:
        src = Path(arg)
        if not src.exists():
            print(f"missing: {src}", file=sys.stderr)
            continue
        to_pdf(src, src.with_suffix(".pdf"))
        if want_docx:
            to_docx(src, src.with_suffix(".docx"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
