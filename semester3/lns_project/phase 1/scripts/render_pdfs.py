"""Render all 6 filled Creator Analysis Worksheets (.md) into clean, black-and-white
academic PDFs (.pdf) matching the exact look and typography of `analysis_form.pdf`
(Computer Modern / serif font, black-and-white `booktabs` tables, no colors, no
hyperlinks, no grey code boxes, and horizontal form rules).
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

EXACT_FORM_CSS = """
@page {
    size: A4;
    margin: 16.5mm 16.5mm 16.5mm 16.5mm;
}
* {
    box-sizing: border-box;
}
body {
    font-family: "Latin Modern Roman", "Computer Modern", "Times New Roman", Times, Georgia, serif;
    font-size: 10pt;
    line-height: 1.42;
    color: #000000;
    background-color: #ffffff;
    margin: 0;
    padding: 0;
}
.worksheet-banner {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 9pt;
    font-weight: normal;
    color: #000000;
    border-bottom: 0.4pt solid #000000;
    padding-bottom: 4px;
    margin-bottom: 14px;
    text-transform: uppercase;
}
.title-block {
    text-align: center;
    margin-top: 4px;
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 0.4pt solid #000000;
}
.title-block .t1 {
    font-size: 12pt;
    font-weight: bold;
    margin-bottom: 3px;
}
.title-block .t2 {
    font-size: 17pt;
    font-weight: bold;
    margin-bottom: 4px;
}
.title-block .t3 {
    font-size: 10pt;
    font-weight: normal;
}
h1 {
    display: none;
}
h2 {
    font-size: 14pt;
    font-weight: bold;
    color: #000000;
    background: none;
    border: none;
    padding: 0;
    margin-top: 14px;
    margin-bottom: 8px;
    page-break-after: avoid;
}
h3 {
    font-size: 11.8pt;
    font-weight: bold;
    color: #000000;
    background: none;
    border: none;
    padding: 0;
    margin-top: 12px;
    margin-bottom: 6px;
    page-break-after: avoid;
}
p, li {
    margin-top: 3px;
    margin-bottom: 5px;
    text-align: left;
    color: #000000;
}
ul, ol {
    padding-left: 18px;
    margin-top: 4px;
    margin-bottom: 8px;
}
li > ul, li > ol {
    margin-top: 3px;
    margin-bottom: 5px;
    list-style-type: none;
    padding-left: 0;
}
code {
    font-family: inherit;
    font-size: inherit;
    background: none;
    color: #000000;
    padding: 0;
    border: none;
}
a {
    color: #000000;
    text-decoration: none;
}
blockquote {
    margin: 4px 0 6px 0;
    padding: 4px 0;
    background: none;
    border-left: none;
    border-bottom: 0.35pt solid #000000;
    color: #000000;
    font-size: 9.2pt;
}
blockquote p {
    margin: 2px 0;
}
table {
    width: 94%;
    margin: 8px auto 12px auto;
    border-collapse: collapse;
    font-size: 9pt;
    border-top: 1.2pt solid #000000;
    border-bottom: 1.2pt solid #000000;
}
th {
    background: none;
    color: #000000;
    font-weight: bold;
    text-align: left;
    padding: 5px 6px;
    border: none;
    border-bottom: 0.6pt solid #000000;
}
td {
    padding: 6px 6px;
    border: none;
    vertical-align: top;
    background: none;
    color: #000000;
}
tr:nth-child(even) td {
    background: none;
}
hr {
    border: none;
    border-top: 0.4pt solid #000000;
    margin: 12px 0;
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
    """Prepare Markdown for exact black-and-white `analysis_form.pdf` HTML rendering."""
    # Remove the subtitle line at top since .title-block renders it
    md_text = re.sub(r"(?m)^\*\*Qualitative analysis of political news discourse\*\*\s*$", "", md_text)
    # Strip raw parenthesized YouTube URLs (`https://youtu.be/...`)
    md_text = re.sub(r"\s*\(`https?://[^`]+`\)", "", md_text)
    # Normalize 2- or 3-space nested bullets inside numbered lists to 4 spaces
    return re.sub(r"(?m)^ {2,3}(-\s+)", r"    \1", md_text)


def render_markdown_to_pdf(md_path: Path, pdf_path: Path, chrome_bin: str, tmpdir: Path) -> None:
    """Convert a single Markdown worksheet to styled black-and-white HTML and print to PDF."""
    raw_md = md_path.read_text(encoding="utf-8")
    normalized_md = normalize_markdown_for_html(raw_md)
    body_html = markdown.markdown(
        normalized_md,
        extensions=["tables", "fenced_code", "sane_lists"],
    )
    body_html = body_html.replace("[x]", "&#9746;")
    body_html = body_html.replace("[ ]", "&#9744;")

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{md_path.stem}</title>
<style>
{EXACT_FORM_CSS}
</style>
</head>
<body>
<div class="worksheet-banner">
  <span>LANGUAGE &amp; SOCIETY</span>
  <span>TRANSCRIPT ANALYSIS WORKSHEET</span>
</div>
<div class="title-block">
  <div class="t1">LANGUAGE &amp; SOCIETY PROJECT</div>
  <div class="t2">Transcript Analysis Worksheet</div>
  <div class="t3">Qualitative analysis of political news discourse</div>
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
