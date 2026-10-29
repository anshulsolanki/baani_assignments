"""Render all 6 filled Creator Analysis Worksheets (.md) into clean, print-ready
academic PDFs (.pdf) modeled after `analysis_form.pdf`.

Uses Python's `markdown` library (with `tables`, `fenced_code`, `sane_lists`) to
produce styled standalone HTML inside an ephemeral temporary directory and
renders each worksheet to PDF via headless Google Chrome.
"""

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List

import markdown

PROJECT_DIR = Path(__file__).resolve().parent.parent
FORMS_DIR = PROJECT_DIR / "analysis_forms"

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
]

ACADEMIC_CSS = """
@page {
    size: A4;
    margin: 15mm 15mm 15mm 15mm;
}
* {
    box-sizing: border-box;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 9.6pt;
    line-height: 1.48;
    color: #1a202c;
    margin: 0;
    padding: 0;
}
.worksheet-banner {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 8.5pt;
    font-weight: 700;
    letter-spacing: 0.6px;
    color: #4a5568;
    border-bottom: 1.5px solid #cbd5e1;
    padding-bottom: 5px;
    margin-bottom: 12px;
    text-transform: uppercase;
}
h1 {
    font-size: 15pt;
    font-weight: 700;
    color: #0f2942;
    border-bottom: 2.5px solid #0f2942;
    padding-bottom: 5px;
    margin-top: 0;
    margin-bottom: 6px;
    letter-spacing: 0.2px;
}
h2 {
    font-size: 12pt;
    font-weight: 700;
    color: #163a5f;
    background-color: #f0f5fa;
    border-left: 4px solid #1e568a;
    padding: 6px 10px;
    margin-top: 15px;
    margin-bottom: 9px;
    page-break-after: avoid;
}
h3 {
    font-size: 10.5pt;
    font-weight: 700;
    color: #1e466e;
    border-bottom: 1px solid #cbd5e1;
    padding-bottom: 3px;
    margin-top: 12px;
    margin-bottom: 7px;
    page-break-after: avoid;
}
p, li {
    margin-top: 3px;
    margin-bottom: 5px;
    text-align: left;
}
ul, ol {
    padding-left: 20px;
    margin-top: 4px;
    margin-bottom: 7px;
}
li > ul, li > ol {
    margin-top: 3px;
    margin-bottom: 4px;
}
code {
    font-family: "SFMono-Regular", Menlo, Consolas, "Liberation Mono", monospace;
    font-size: 8.7pt;
    background-color: #f1f5f9;
    color: #0f172a;
    padding: 1px 4px;
    border-radius: 3px;
    border: 1px solid #e2e8f0;
}
blockquote {
    margin: 7px 0 9px 0;
    padding: 7px 12px;
    background-color: #f8fafc;
    border-left: 3.5px solid #475569;
    color: #1e293b;
    font-size: 9.2pt;
}
blockquote p {
    margin: 3px 0;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 9px 0 13px 0;
    font-size: 8.9pt;
}
th {
    background-color: #163a5f;
    color: #ffffff;
    font-weight: 600;
    text-align: left;
    padding: 6px 8px;
    border: 1px solid #163a5f;
}
td {
    padding: 6px 8px;
    border: 1px solid #cbd5e1;
    vertical-align: top;
}
tr:nth-child(even) td {
    background-color: #f8fafc;
}
hr {
    border: none;
    border-top: 1.5px solid #cbd5e1;
    margin: 13px 0;
}
.cb-checked {
    font-weight: 700;
    color: #0f2942;
}
.cb-unchecked {
    color: #64748b;
}
"""


def find_chrome_binary() -> str:
    """Locate Google Chrome / Chromium executable for headless PDF generation."""
    for candidate in CHROME_CANDIDATES:
        if candidate and Path(candidate).is_file():
            return candidate
    raise FileNotFoundError(
        "Google Chrome executable not found. Expected at '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'."
    )


def normalize_markdown_for_html(md_text: str) -> str:
    """Ensure 2- or 3-space nested bullets inside numbered lists use 4 spaces for python-markdown."""
    return re.sub(r"(?m)^ {2,3}(-\s+)", r"    \1", md_text)


def render_markdown_to_pdf(md_path: Path, pdf_path: Path, chrome_bin: str, tmpdir: Path) -> None:
    """Convert a single Markdown worksheet to styled HTML and print to PDF."""
    raw_md = md_path.read_text(encoding="utf-8")
    normalized_md = normalize_markdown_for_html(raw_md)
    body_html = markdown.markdown(
        normalized_md,
        extensions=["tables", "fenced_code", "sane_lists"],
    )
    body_html = body_html.replace("[x]", '<span class="cb-checked">&#9745;</span>')
    body_html = body_html.replace("[ ]", '<span class="cb-unchecked">&#9744;</span>')

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{md_path.stem}</title>
<style>
{ACADEMIC_CSS}
</style>
</head>
<body>
<div class="worksheet-banner">
  <span>LANGUAGE &amp; SOCIETY</span>
  <span>TRANSCRIPT ANALYSIS WORKSHEET</span>
</div>
{body_html}
</body>
</html>
"""
    html_path = tmpdir / f"{md_path.stem}.html"
    html_path.write_text(full_html, encoding="utf-8")

    cmd = [
        chrome_bin,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path.as_uri(),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0 or not pdf_path.is_file():
        raise RuntimeError(
            f"Headless Chrome failed on {md_path.name} (exit={proc.returncode}): {proc.stderr}"
        )


def render_all_worksheets() -> List[Path]:
    """Render all `*.md` worksheets in `analysis_forms/` to `.pdf`."""
    chrome_bin = find_chrome_binary()
    md_files = sorted(FORMS_DIR.glob("*_Analysis.md"))
    if not md_files:
        raise FileNotFoundError(f"No *_Analysis.md files found in {FORMS_DIR}")

    rendered: List[Path] = []
    with tempfile.TemporaryDirectory(prefix="lns_pdf_html_", dir=str(PROJECT_DIR)) as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        for md_path in md_files:
            pdf_path = md_path.with_suffix(".pdf")
            print(f"Rendering {md_path.name} -> {pdf_path.name} ...")
            render_markdown_to_pdf(md_path, pdf_path, chrome_bin, tmpdir)
            size_kb = pdf_path.stat().st_size / 1024.0
            print(f"  -> Generated {pdf_path.name} ({size_kb:.1f} KB)")
            rendered.append(pdf_path)

    return rendered


if __name__ == "__main__":
    pdfs = render_all_worksheets()
    print(f"\nSuccessfully rendered {len(pdfs)} PDF analysis worksheets!")
    sys.exit(0)
