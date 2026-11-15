"""
render_pdfs.py - Render Phase 2 Non-Verbal Analysis Markdown worksheets (.md) into
clean black-and-white academic PDFs (.pdf) matching NonVerbal_AnalysisForm.pdf.

Author: Baani Solanki (2025114016)
Course: Language and Society (Phase 2 - Non-Verbal & Multimodal Discourse Analysis)
"""

import os
import re
import shutil
import subprocess
import tempfile
import markdown


CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
]


def get_form_css():
    """Return black-and-white academic CSS matching NonVerbal_AnalysisForm.pdf."""
    return """
    @page {
        size: A4;
        margin: 16.5mm 16.5mm 16.5mm 16.5mm;
    }
    * {
        box-sizing: border-box;
    }
    body {
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
        font-size: 9.8pt;
        line-height: 1.42;
        color: #000000;
        background-color: #ffffff;
        margin: 0;
        padding: 0;
    }
    h1 {
        font-size: 16pt;
        font-weight: bold;
        color: #000000;
        margin-top: 0;
        margin-bottom: 6px;
    }
    h2 {
        font-size: 13pt;
        font-weight: bold;
        color: #000000;
        margin-top: 14px;
        margin-bottom: 6px;
        page-break-after: avoid;
    }
    h3 {
        font-size: 11pt;
        font-weight: bold;
        color: #333333;
        margin-top: 10px;
        margin-bottom: 5px;
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
    code {
        font-family: "Menlo", "Consolas", "Courier New", monospace;
        font-size: 8.8pt;
        background-color: #f4f4f4;
        color: #000000;
        padding: 1px 3px;
        border-radius: 2px;
    }
    a {
        color: #000000;
        text-decoration: underline;
    }
    table {
        width: 100%;
        margin: 8px 0 12px 0;
        border-collapse: collapse;
        font-size: 8.8pt;
        table-layout: fixed;
        word-wrap: break-word;
    }
    th, td {
        border: 0.75pt solid #000000;
        padding: 5px 6px;
        vertical-align: top;
        text-align: left;
        overflow-wrap: break-word;
    }
    th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    tr {
        page-break-inside: avoid;
    }
    hr {
        border: none;
        border-top: 0.5pt solid #666666;
        margin: 12px 0;
    }
    """


def find_chrome():
    """Find the Google Chrome binary on macOS or Linux."""
    for path in CHROME_PATHS:
        if path and os.path.isfile(path):
            return path
    raise FileNotFoundError("Google Chrome binary not found for PDF rendering.")


def render_markdown_file(md_path, pdf_path, chrome_bin, temp_dir):
    """Convert one Markdown worksheet to HTML and print to PDF via headless Chrome."""
    with open(md_path, "r", encoding="utf-8") as infile:
        raw_md = infile.read()

    normalized_md = re.sub(r"(?m)^ {2,3}(\*\s+|-\s+)", r"    \1", raw_md)
    normalized_md = re.sub(r"_([^_]+)_", r"<strong>\1</strong>", normalized_md)
    body_html = markdown.markdown(
        normalized_md,
        extensions=["tables", "fenced_code", "sane_lists"],
    )
    body_html = re.sub(r"\*\"([^\"]+)\"\*", r"<em>&ldquo;\1&rdquo;</em>", body_html)
    body_html = re.sub(r"`([^`]+)`", r"<code>\1</code>", body_html)
    body_html = body_html.replace("<code>[x]</code>", "&#9746;")
    body_html = body_html.replace("<code>[ ]</code>", "&#9744;")
    body_html = body_html.replace("[x]", "&#9746;")
    body_html = body_html.replace("[ ]", "&#9744;")

    html_doc = (
        "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
        f"<style>{get_form_css()}</style></head>"
        f"<body>{body_html}</body></html>"
    )

    base_name = os.path.splitext(os.path.basename(md_path))[0]
    html_path = os.path.join(temp_dir, base_name + ".html")
    with open(html_path, "w", encoding="utf-8") as outfile:
        outfile.write(html_doc)

    cmd = [
        chrome_bin,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        f"file://{html_path}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0 or not os.path.isfile(pdf_path):
        raise RuntimeError(f"Failed to render {pdf_path}: {result.stderr}")


def main():
    """Render all 6 creator Non-Verbal Markdown forms into PDFs."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    forms_dir = os.path.join(base_dir, "analysis_forms")
    chrome_bin = find_chrome()

    md_files = sorted(
        f for f in os.listdir(forms_dir)
        if f.endswith("_NonVerbal_Analysis.md")
    )

    print(f"=== Rendering {len(md_files)} Non-Verbal Analysis PDFs ===")
    with tempfile.TemporaryDirectory(prefix="lns_phase2_pdf_") as temp_dir:
        for filename in md_files:
            md_path = os.path.join(forms_dir, filename)
            pdf_filename = filename.replace(".md", ".pdf")
            pdf_path = os.path.join(forms_dir, pdf_filename)
            render_markdown_file(md_path, pdf_path, chrome_bin, temp_dir)
            size_kb = os.path.getsize(pdf_path) / 1024.0
            print(f"  [OK] {pdf_filename} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
