"""
generate_latex.py - Convert Phase 2 Non-Verbal Markdown forms into Overleaf LaTeX (.tex).

Author: Baani Solanki (2025114016)
Course: Language and Society (Phase 2 - Non-Verbal & Multimodal Discourse Analysis)
"""

import os
import re


def escape_latex(text):
    """Escape special LaTeX characters and convert multimodal symbols cleanly."""
    replacements = [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
        ("↑", r"$\uparrow$"),
        ("↓", r"$\downarrow$"),
        ("°", r"$^\circ$"),
        ("—", "---"),
        ("–", "--"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def format_inline_markdown(line):
    """Convert bold, italic, and inline code spans into LaTeX commands."""
    line = escape_latex(line)
    line = re.sub(r"`([^`]+)`", r"\\texttt{\1}", line)
    line = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", line)
    line = re.sub(r"\*([^*]+)\*", r"\\textit{\1}", line)
    line = re.sub(
        r"\[([^\]]+)\]\((https?://[^\)]+)\)",
        r"\\href{\2}{\1}",
        line,
    )
    return line


def convert_table_block(table_lines):
    """Convert a Markdown pipe table into a LaTeX longtable environment."""
    rows = []
    for raw in table_lines:
        stripped = raw.strip().strip("|")
        cells = [c.strip() for c in stripped.split("|")]
        if all(set(c) <= set(":-") and len(c) > 0 for c in cells):
            continue
        rows.append(cells)

    if not rows:
        return []

    num_cols = len(rows[0])
    col_width = round(0.92 / num_cols, 2)
    col_spec = "|" + "|".join([f"p{{{col_width}\\textwidth}}"] * num_cols) + "|"

    out = [f"\\begin{{longtable}}{{{col_spec}}}", "\\hline"]
    header = " & ".join(format_inline_markdown(c) for c in rows[0]) + r" \\ \hline \endhead"
    out.append(header)

    for row in rows[1:]:
        padded = (row + [""] * num_cols)[:num_cols]
        line_str = " & ".join(format_inline_markdown(c) for c in padded) + r" \\ \hline"
        out.append(line_str)

    out.append("\\end{longtable}")
    return out


def markdown_to_latex_body(md_text):
    """Convert full Markdown worksheet text into LaTeX body lines."""
    lines = md_text.splitlines()
    out = []
    table_buf = []
    in_itemize = False

    for line in lines:
        if line.strip().startswith("|"):
            if in_itemize:
                out.append("\\end{itemize}")
                in_itemize = False
            table_buf.append(line)
            continue
        elif table_buf:
            out.extend(convert_table_block(table_buf))
            table_buf = []

        stripped = line.strip()
        if not stripped:
            if in_itemize:
                out.append("\\end{itemize}")
                in_itemize = False
            out.append("")
        elif stripped == "---":
            out.append("\\bigskip\\hrule\\bigskip")
        elif stripped.startswith("# "):
            out.append(f"\\section*{{{format_inline_markdown(stripped[2:])}}}")
        elif stripped.startswith("## "):
            out.append(f"\\subsection*{{{format_inline_markdown(stripped[3:])}}}")
        elif stripped.startswith("### "):
            out.append(f"\\subsubsection*{{{format_inline_markdown(stripped[4:])}}}")
        elif stripped.startswith("* ") or stripped.startswith("- "):
            if not in_itemize:
                out.append("\\begin{itemize}")
                in_itemize = True
            out.append(f"  \\item {format_inline_markdown(stripped[2:])}")
        elif re.match(r"^\d+\.\s+", stripped):
            content = re.sub(r"^\d+\.\s+", "", stripped)
            num = stripped.split(".")[0]
            out.append(f"\\noindent\\textbf{{{num}.}} {format_inline_markdown(content)}\\par\\smallskip")
        else:
            out.append(format_inline_markdown(stripped) + "\\par\\smallskip")

    if in_itemize:
        out.append("\\end{itemize}")
    if table_buf:
        out.extend(convert_table_block(table_buf))
    return "\n".join(out)


def wrap_latex_document(body_tex):
    """Wrap LaTeX body content with standard A4 article preamble."""
    preamble = (
        "\\documentclass[10pt,a4paper]{article}\n"
        "\\usepackage[utf8]{inputenc}\n"
        "\\usepackage[T1]{fontenc}\n"
        "\\usepackage[margin=18mm]{geometry}\n"
        "\\usepackage{longtable}\n"
        "\\usepackage{hyperref}\n"
        "\\usepackage{enumitem}\n"
        "\\setlist[itemize]{noitemsep, topsep=2pt}\n"
        "\\setlength{\\parindent}{0pt}\n"
        "\\begin{document}\n\n"
    )
    return preamble + body_tex + "\n\n\\end{document}\n"


def main():
    """Generate individual and combined Overleaf .tex files for all 6 creators."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    forms_dir = os.path.join(base_dir, "analysis_forms")
    latex_dir = os.path.join(forms_dir, "latex")
    os.makedirs(latex_dir, exist_ok=True)

    md_files = sorted(
        f for f in os.listdir(forms_dir)
        if f.endswith("_NonVerbal_Analysis.md")
    )

    combined_bodies = []
    print(f"=== Generating {len(md_files)} LaTeX (.tex) Files ===")
    for filename in md_files:
        md_path = os.path.join(forms_dir, filename)
        with open(md_path, "r", encoding="utf-8") as infile:
            md_text = infile.read()

        body_tex = markdown_to_latex_body(md_text)
        combined_bodies.append(body_tex)

        tex_filename = filename.replace(".md", ".tex")
        tex_path = os.path.join(latex_dir, tex_filename)
        with open(tex_path, "w", encoding="utf-8") as outfile:
            outfile.write(wrap_latex_document(body_tex))
        print(f"  [OK] latex/{tex_filename}")

    combined_path = os.path.join(latex_dir, "All_6_Creators_Combined_NonVerbal_Analysis.tex")
    with open(combined_path, "w", encoding="utf-8") as outfile:
        outfile.write(wrap_latex_document("\n\\newpage\n".join(combined_bodies)))
    print("  [OK] latex/All_6_Creators_Combined_NonVerbal_Analysis.tex")


if __name__ == "__main__":
    main()
