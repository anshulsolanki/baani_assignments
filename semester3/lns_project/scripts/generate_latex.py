"""Convert the 6 filled Creator Analysis Worksheets (.md) into Overleaf-ready
LaTeX (.tex) files that mirror the exact layout and typography of `analysis_form.pdf`.

Generates:
1. Six individual standalone Overleaf `.tex` files in `analysis_forms/latex/`:
   - `01_Sarthak_Goswami_Analysis.tex`
   - `02_Dhruv_Rathee_Analysis.tex`
   - `03_Mohak_Mangal_Analysis.tex`
   - `04_Aaj_Tak_Analysis.tex`
   - `05_Republic_TV_Analysis.tex`
   - `06_The_Wire_Analysis.tex`
2. One combined master Overleaf `.tex` file in `analysis_forms/latex/`:
   - `All_6_Creators_Analysis_Overleaf.tex` (all 6 worksheets in a single compilation unit)
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

PROJECT_DIR = Path(__file__).resolve().parent.parent
FORMS_DIR = PROJECT_DIR / "analysis_forms"
LATEX_DIR = FORMS_DIR / "latex"

LATEX_PREAMBLE = r"""\documentclass[10pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[a4paper,top=20mm,bottom=20mm,left=16mm,right=16mm,headheight=14pt]{geometry}
\usepackage{fancyhdr}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{enumitem}
\usepackage{amssymb}
\usepackage{xcolor}
\usepackage[hyphens]{url}
\usepackage[colorlinks=true,urlcolor=blue!60!black,linkcolor=blue!60!black]{hyperref}

\setlength{\parindent}{0pt}
\setlength{\parskip}{3pt}
\renewcommand{\arraystretch}{1.28}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small LANGUAGE \& SOCIETY}
\fancyhead[R]{\small TRANSCRIPT ANALYSIS WORKSHEET}
\fancyfoot[C]{\small\thepage}
\renewcommand{\headrulewidth}{0.4pt}
"""

WORKSHEET_TITLE_BANNER = r"""\begin{center}
    {\large\bfseries LANGUAGE \& SOCIETY PROJECT}\\[3pt]
    {\LARGE\bfseries Transcript Analysis Worksheet}\\[3pt]
    {\normalsize Qualitative analysis of political news discourse}
\end{center}
\vspace{2pt}
\noindent\rule{\textwidth}{0.4pt}
\vspace{4pt}
"""


def escape_latex_text(text: str) -> str:
    """Escape plain text for LaTeX while normalizing Unicode punctuation to pure ASCII."""
    # Normalize Unicode characters first
    replacements = [
        ("₹", "Rs.\\,"),
        ("–", "--"),
        ("—", "---"),
        ("“", "``"),
        ("”", "''"),
        ("‘", "`"),
        ("’", "'"),
        ("…", "\\ldots{}"),
        ("\u00a0", " "),
    ]
    for src, dst in replacements:
        text = text.replace(src, dst)

    # Escape special LaTeX characters in plain text
    out: List[str] = []
    for ch in text:
        if ch == "\\":
            out.append(r"\textbackslash{}")
        elif ch == "&":
            out.append(r"\&")
        elif ch == "%":
            out.append(r"\%")
        elif ch == "$":
            out.append(r"\$")
        elif ch == "#":
            out.append(r"\#")
        elif ch == "_":
            out.append(r"\_")
        elif ch == "{":
            out.append(r"\{")
        elif ch == "}":
            out.append(r"\}")
        elif ch == "~":
            out.append(r"\textasciitilde{}")
        elif ch == "^":
            out.append(r"\textasciicircum{}")
        else:
            out.append(ch)
    res = "".join(out)
    # Restore our intentional Rs.\, thinspace command if backslash was escaped
    res = res.replace(r"Rs.\textbackslash{},", r"Rs.\,")
    res = res.replace(r"\textbackslash{}ldots\{\}", r"\ldots{}")
    return res


def format_inline_markdown(text: str, is_quote_block: bool = False) -> str:
    """Convert inline Markdown (`code`, **bold**, *italic*, [x]/[ ], <br>, ->) to LaTeX."""
    # Replace <br> tags with a placeholder before tokenizing
    text = re.sub(r"<br\s*/?>", " @@BR@@ ", text)

    # Tokenize inline code spans `...` first so their contents aren't parsed as bold/italics
    code_tokens: List[str] = []

    def replace_code(match: re.Match) -> str:
        inner = match.group(1)
        idx = len(code_tokens)
        if inner == "[x]":
            code_tokens.append(r"$\boxtimes$")
        elif inner == "[ ]":
            code_tokens.append(r"$\square$")
        elif inner.startswith("http://") or inner.startswith("https://"):
            # Safe URL inside \url{...}
            safe_url = inner.replace("%", r"\%").replace("#", r"\#")
            code_tokens.append(f"\\url{{{safe_url}}}")
        else:
            code_tokens.append(f"\\texttt{{{escape_latex_text(inner)}}}")
        return f"@@CODE{idx}@@"

    text = re.sub(r"`([^`]+)`", replace_code, text)

    # Also support bare [x] and [ ] checkboxes outside backticks
    text = text.replace("[x]", "@@CBCHECKED@@").replace("[ ]", "@@CBUNCHECKED@@")

    # Tokenize **bold** and *italic* before escaping plain text
    bold_tokens: List[str] = []

    def replace_bold(match: re.Match) -> str:
        inner = match.group(1)
        idx = len(bold_tokens)
        bold_tokens.append(inner)
        return f"@@BOLD{idx}@@"

    text = re.sub(r"\*\*([^*]+)\*\*", replace_bold, text)

    italic_tokens: List[str] = []

    def replace_italic(match: re.Match) -> str:
        inner = match.group(1)
        idx = len(italic_tokens)
        italic_tokens.append(inner)
        return f"@@ITALIC{idx}@@"

    text = re.sub(r"\*([^*]+)\*", replace_italic, text)

    # Replace ASCII arrow -> with placeholder
    text = text.replace(" -> ", " @@ARROW@@ ")

    # Escape remaining plain text
    escaped = escape_latex_text(text)

    # Restore italic tokens (and recursively handle any code tokens inside them)
    for idx, inner in enumerate(italic_tokens):
        escaped_inner = escape_latex_text(inner)
        escaped = escaped.replace(f"@@ITALIC{idx}@@", f"\\textit{{{escaped_inner}}}")

    # Restore bold tokens
    for idx, inner in enumerate(bold_tokens):
        escaped_inner = escape_latex_text(inner)
        # Restore any italic tokens inside bold if present
        for i_idx, i_inner in enumerate(italic_tokens):
            escaped_inner = escaped_inner.replace(
                f"@@ITALIC{i_idx}@@", f"\\textit{{{escape_latex_text(i_inner)}}}"
            )
        escaped = escaped.replace(f"@@BOLD{idx}@@", f"\\textbf{{{escaped_inner}}}")

    # Restore checkboxes, arrows, line breaks, and code tokens
    escaped = escaped.replace("@@CBCHECKED@@", r"$\boxtimes$")
    escaped = escaped.replace("@@CBUNCHECKED@@", r"$\square$")
    escaped = escaped.replace("@@ARROW@@", r"$\rightarrow$")
    escaped = escaped.replace("@@BR@@", r"\newline ")

    for idx, token_latex in enumerate(code_tokens):
        escaped = escaped.replace(f"@@CODE{idx}@@", token_latex)

    if is_quote_block:
        return escaped
    return escaped


def render_table(table_lines: List[str]) -> str:
    """Convert a Markdown pipe table into a booktabs + longtable LaTeX environment."""
    rows: List[List[str]] = []
    for ln in table_lines:
        stripped = ln.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped[1:-1].split("|")]
            # Skip alignment separator row | :--- | :--- |
            if all(re.match(r"^:?-{2,}:?$", c) for c in cells):
                continue
            rows.append(cells)

    if not rows:
        return ""

    ncols = len(rows[0])
    if ncols == 4:
        colspec = (
            r"@{}>{\raggedright\arraybackslash}p{0.17\textwidth}"
            r" >{\raggedright\arraybackslash}p{0.20\textwidth}"
            r" >{\raggedright\arraybackslash}p{0.24\textwidth}"
            r" >{\raggedright\arraybackslash}p{0.32\textwidth}@{}"
        )
    elif ncols == 3:
        colspec = (
            r"@{}>{\raggedright\arraybackslash}p{0.19\textwidth}"
            r" >{\raggedright\arraybackslash}p{0.38\textwidth}"
            r" >{\raggedright\arraybackslash}p{0.37\textwidth}@{}"
        )
    else:
        w = round(0.94 / ncols, 2)
        colspec = "@{}" + " ".join([f">{{ \\raggedright\\arraybackslash }}p{{{w}\\textwidth}}"] * ncols) + "@{}"

    out: List[str] = [f"\\begin{{longtable}}{{{colspec}}}", "\\toprule"]
    header_cells = [f"\\textbf{{{format_inline_markdown(c)}}}" for c in rows[0]]
    out.append(" & ".join(header_cells) + r" \\")
    out.append("\\midrule")
    out.append("\\endhead")

    for r_idx, row in enumerate(rows[1:]):
        # Pad or trim if needed
        while len(row) < ncols:
            row.append("")
        formatted_cells = [format_inline_markdown(c) for c in row[:ncols]]
        out.append(" & ".join(formatted_cells) + r" \\")
        if r_idx < len(rows[1:]) - 1:
            out.append(r"\addlinespace[4pt]")

    out.append("\\bottomrule")
    out.append("\\end{longtable}")
    return "\n".join(out)


def convert_markdown_body_to_latex(md_text: str) -> str:
    """Convert a single Creator Analysis Worksheet Markdown document body into LaTeX."""
    lines = md_text.splitlines()
    out: List[str] = [WORKSHEET_TITLE_BANNER]

    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Skip the top H1 and subtitle line since WORKSHEET_TITLE_BANNER renders them
        if i <= 2 and (
            stripped.startswith("# LANGUAGE & SOCIETY PROJECT")
            or stripped == "**Qualitative analysis of political news discourse**"
        ):
            i += 1
            continue

        if not stripped:
            i += 1
            continue

        # Horizontal rule
        if stripped == "---":
            out.append(r"\vspace{4pt}\noindent\rule{\textwidth}{0.4pt}\vspace{4pt}")
            i += 1
            continue

        # Section H2 (## ...)
        if stripped.startswith("## "):
            title = format_inline_markdown(stripped[3:].strip())
            out.append(f"\n\\section*{{{title}}}")
            i += 1
            continue

        # Subsection H3 (### ...)
        if stripped.startswith("### "):
            title = format_inline_markdown(stripped[4:].strip())
            out.append(f"\n\\subsection*{{{title}}}")
            i += 1
            continue

        # Pipe Table
        if stripped.startswith("|") and stripped.endswith("|"):
            table_lines: List[str] = []
            while i < n and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                table_lines.append(lines[i])
                i += 1
            out.append(render_table(table_lines))
            continue

        # Numbered list block (1. ... through 8./9. ...)
        if re.match(r"^\d+\.\s+", stripped):
            out.append(r"\begin{enumerate}[leftmargin=1.6em, itemsep=4pt, topsep=4pt]")
            while i < n:
                cur = lines[i]
                cur_str = cur.strip()
                if not cur_str:
                    # Peek ahead to see if another numbered item or indented sub-bullet follows
                    j = i + 1
                    while j < n and not lines[j].strip():
                        j += 1
                    if j < n and (
                        re.match(r"^\d+\.\s+", lines[j].strip())
                        or re.match(r"^ {2,4}-\s+", lines[j])
                    ):
                        i = j
                        continue
                    else:
                        break

                m_num = re.match(r"^(\d+)\.\s+(.*)$", cur_str)
                if m_num:
                    q_text = format_inline_markdown(m_num.group(2))
                    out.append(f"  \\item {q_text}")
                    i += 1
                    # Collect any indented sub-bullets under this numbered item
                    sub_bullets: List[str] = []
                    while i < n:
                        sub_ln = lines[i]
                        m_sub = re.match(r"^ {2,4}-\s+(.*)$", sub_ln)
                        if m_sub:
                            sub_bullets.append(format_inline_markdown(m_sub.group(1)))
                            i += 1
                        elif not sub_ln.strip():
                            # Peek if another sub-bullet follows
                            k = i + 1
                            while k < n and not lines[k].strip():
                                k += 1
                            if k < n and re.match(r"^ {2,4}-\s+", lines[k]):
                                i = k
                                continue
                            break
                        else:
                            break
                    if sub_bullets:
                        out.append(r"  \begin{itemize}[leftmargin=1.4em, itemsep=2pt, topsep=2pt]")
                        for sb in sub_bullets:
                            out.append(f"    \\item {sb}")
                        out.append(r"  \end{itemize}")
                else:
                    break
            out.append(r"\end{enumerate}")
            continue

        # Top-level unordered bullet list (- ...)
        if line.startswith("- "):
            out.append(r"\begin{itemize}[leftmargin=1.5em, itemsep=3pt, topsep=4pt]")
            while i < n:
                cur = lines[i]
                if cur.startswith("- "):
                    item_text = format_inline_markdown(cur[2:].strip())
                    i += 1
                    # Check for continuation lines (indented by 2 spaces, e.g. `  > ...`, `  - ...`, or `  Text...`)
                    sub_items: List[str] = []
                    continuation_parts: List[str] = []
                    while i < n:
                        nxt = lines[i]
                        if nxt.startswith("  - "):
                            sub_items.append(format_inline_markdown(nxt[4:].strip()))
                            i += 1
                        elif nxt.startswith("  > "):
                            quote_raw = nxt[4:].strip()
                            # Remove surrounding backticks if the whole quote is wrapped in `...`
                            if quote_raw.startswith("`") and quote_raw.endswith("`") and quote_raw.count("`") == 2:
                                quote_raw = quote_raw[1:-1]
                            quote_formatted = format_inline_markdown(quote_raw, is_quote_block=True)
                            continuation_parts.append(
                                f"\n    \\begin{{quote}}\\small\\ttfamily {quote_formatted}\\end{{quote}}"
                            )
                            i += 1
                        elif nxt.startswith("  ") and nxt.strip() and not nxt.startswith("    -"):
                            continuation_parts.append(" " + format_inline_markdown(nxt.strip()))
                            i += 1
                        else:
                            break

                    full_item = item_text + "".join(continuation_parts)
                    out.append(f"  \\item {full_item}")
                    if sub_items:
                        out.append(r"  \begin{itemize}[leftmargin=1.4em, itemsep=2pt, topsep=2pt]")
                        for si in sub_items:
                            out.append(f"    \\item {si}")
                        out.append(r"  \end{itemize}")
                elif not cur.strip():
                    # Check if the next non-empty line is still a `- ` bullet
                    j = i + 1
                    while j < n and not lines[j].strip():
                        j += 1
                    if j < n and lines[j].startswith("- "):
                        i = j
                        continue
                    break
                else:
                    break
            out.append(r"\end{itemize}")
            continue

        # Standalone paragraph (e.g. Focus: ..., Reminder: ..., Copy or print...)
        out.append(format_inline_markdown(stripped) + "\n")
        i += 1

    return "\n".join(out)


def generate_all_latex_files() -> Tuple[List[Path], Path]:
    """Generate individual Overleaf `.tex` files and a combined master `.tex` file."""
    LATEX_DIR.mkdir(parents=True, exist_ok=True)
    md_files = sorted(FORMS_DIR.glob("*_Analysis.md"))
    if not md_files:
        raise FileNotFoundError(f"No *_Analysis.md files found in {FORMS_DIR}")

    individual_paths: List[Path] = []
    combined_bodies: List[str] = []

    for md_path in md_files:
        md_text = md_path.read_text(encoding="utf-8")
        body_latex = convert_markdown_body_to_latex(md_text)
        combined_bodies.append(body_latex)

        full_tex = (
            LATEX_PREAMBLE
            + "\n\\begin{document}\n\n"
            + body_latex
            + "\n\n\\end{document}\n"
        )
        tex_path = LATEX_DIR / f"{md_path.stem}.tex"
        tex_path.write_text(full_tex, encoding="utf-8")
        individual_paths.append(tex_path)
        print(f"Generated {tex_path.relative_to(PROJECT_DIR)} ({tex_path.stat().st_size / 1024:.1f} KB)")

    master_tex = (
        LATEX_PREAMBLE
        + "\n\\begin{document}\n\n"
        + "\n\n\\clearpage\n\n".join(combined_bodies)
        + "\n\n\\end{document}\n"
    )
    master_path = LATEX_DIR / "All_6_Creators_Analysis_Overleaf.tex"
    master_path.write_text(master_tex, encoding="utf-8")
    print(f"Generated {master_path.relative_to(PROJECT_DIR)} ({master_path.stat().st_size / 1024:.1f} KB)")

    return individual_paths, master_path


if __name__ == "__main__":
    generate_all_latex_files()
    sys.exit(0)
