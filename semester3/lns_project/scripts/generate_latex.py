r"""Generate Overleaf-ready LaTeX (.tex) files that reproduce the EXACT look,
typography, fonts, margins, form rules, and black-and-white layout of
`analysis_form.pdf` (compiled originally with pdfTeX / Computer Modern).

Key fidelity features matching `analysis_form.pdf`:
- Standard `10pt` `a4paper` `article` class in classic Computer Modern (OT1/UTF-8)
- Exact `46.77pt` (`1.65cm`) left/right margins (`501.73pt` text width)
- Running `fancyhdr` header: `LANGUAGE & SOCIETY` (left) and `TRANSCRIPT ANALYSIS WORKSHEET` (right)
- Zero colors (`xcolor` removed), zero hyperlinks (`hyperref`/`url` removed), zero `\texttt` code blocks
- Exact Page 1 title block and centered `\small` `booktabs` Guidelines table
- Exact underlined/ruled form fields (`Outlet:`, `Date:`, `Video title:`, `Timestamp(s):`, `Analyst:`, `Language:`)
- Exact `Event-specific questions` (normal Roman question text followed by the answer)
- Exact `Apply the five shared features` table (`Naming`, `Presupposition`, `Agency`, `Antagonisation`, `Intensification / softening`)
- Exact `Short summary`, `Common form: Blank excerpt record`, and `Common form: End-of-event summary`
  layout using bold prompt lines and `0.35pt` full-width horizontal form rules (`\rule{\textwidth}{0.35pt}`).
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

PROJECT_DIR = Path(__file__).resolve().parent.parent
FORMS_DIR = PROJECT_DIR / "analysis_forms"
LATEX_DIR = FORMS_DIR / "latex"

LATEX_PREAMBLE = r"""\documentclass[10pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[a4paper,left=46.77pt,right=46.77pt,top=48pt,bottom=48pt,headheight=14pt,headsep=14pt]{geometry}
\usepackage{fancyhdr}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{enumitem}
\usepackage{amssymb}

\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}
\renewcommand{\arraystretch}{1.35}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small LANGUAGE \& SOCIETY}
\fancyhead[R]{\small TRANSCRIPT ANALYSIS WORKSHEET}
\fancyfoot[C]{\small\thepage}
\renewcommand{\headrulewidth}{0.4pt}

\newcommand{\formrule}{\par\vspace{3pt}\noindent\rule{\textwidth}{0.35pt}\par\vspace{7pt}}
\newcommand{\sectionrule}{\par\vspace{4pt}\noindent\rule{\textwidth}{0.4pt}\par\vspace{8pt}}
"""

PAGE1_GUIDELINES_LATEX = r"""\begin{center}
{\large\textbf{LANGUAGE \& SOCIETY PROJECT}}\\[4pt]
{\LARGE\textbf{Transcript Analysis Worksheet}}\\[4pt]
{\normalsize Qualitative analysis of political news discourse}
\end{center}
\vspace{2pt}
\noindent\rule{\textwidth}{0.4pt}

\section*{Guidelines: Five features to look for in every event}

\begin{center}
\small
\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.18\textwidth} >{\raggedright\arraybackslash}p{0.21\textwidth} >{\raggedright\arraybackslash}p{0.23\textwidth} >{\raggedright\arraybackslash}p{0.29\textwidth}@{}}
\toprule
\textbf{Feature} & \textbf{What to look for} & \textbf{Illustrative example} & \textbf{Questions to answer} \\
\midrule
\textbf{1. Naming} & What are people, groups, actions, or events called? & ``Students'', ``protesters'', ``agitators''; ``irregularity'', ``scam'', ``controversy''. & What exact label is used? Who or what does it refer to? Who uses it? What alternative label could have been used? \\[6pt]
\textbf{2. Presupposition} & What is treated as already true or taken for granted? & ``Why are students creating chaos again?'' may presuppose earlier disruption. & What does the wording assume? Is that assumption supported, disputed, or left unexamined? Does it appear in a question or words such as ``again'', ``still'', or ``finally''? \\[6pt]
\textbf{3. Agency} & Who is shown doing something? Who is acted upon? Who disappears? & ``Police injured protesters'' vs.\ ``Protesters were injured.'' & Who is the actor? Who experiences the action? Is responsibility named, backgrounded, or omitted? \\[6pt]
\textbf{4. Antagonisation} & Who is positioned against whom? & ``Ordinary citizens'' vs.\ ``political troublemakers''. & Which groups are contrasted? Is one presented as more legitimate, moral, patriotic, dangerous, or disloyal? Is an ``us vs.\ them'' division implied? \\[6pt]
\textbf{5. Intensification / softening} & What is exaggerated, minimised, softened, or euphemised? & ``Violent mob'' vs.\ ``peaceful demonstrators''; ``incident'' instead of a direct description. & Which words heighten emotion or seriousness? Which minimise it? Are metaphors, dramatic adjectives, hedges, or euphemisms used? Does the wording match the evidence? \\
\bottomrule
\end{tabular}
\end{center}

\vspace{4pt}
\noindent{\small\emph{Reminder:} A label or implication is not automatically false or manipulative. Examine the surrounding context and evidence.}

\newpage
"""


def convert_quotes_to_tex(text: str) -> str:
    """Convert straight ASCII double quotes "..." into TeX quotes ``...''."""
    return re.sub(r'"([^"]*)"', r"``\1''", text)


def escape_latex_plain(text: str) -> str:
    """Escape plain text for LaTeX (pure ASCII, Computer Modern serif, no \\texttt)."""
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

    text = convert_quotes_to_tex(text)

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
    res = res.replace(r"Rs.\textbackslash{},", r"Rs.\,")
    res = res.replace(r"\textbackslash{}ldots\{\}", r"\ldots{}")
    return res


def format_inline(text: str) -> str:
    """Convert Markdown inline markup into clean serif LaTeX without colors, URLs, or \\texttt."""
    # Strip parenthesized raw YouTube URLs like (`https://youtu.be/...`)
    text = re.sub(r"\s*\(`https?://[^`]+`\)", "", text)
    text = re.sub(r"`https?://[^`]+`", "", text)

    # Replace <br> tags with a newline placeholder
    text = re.sub(r"<br\s*/?>", " @@BR@@ ", text)

    # Replace checkboxes [x] and [ ] (with or without backticks)
    text = text.replace("`[x]`", "@@CBCHECKED@@").replace("`[ ]`", "@@CBUNCHECKED@@")
    text = text.replace("[x]", "@@CBCHECKED@@").replace("[ ]", "@@CBUNCHECKED@@")

    # Strip backticks around inline code/quotes so everything renders in clean Computer Modern serif
    text = re.sub(r"`([^`]+)`", r"\1", text)

    # Tokenize **bold** and *italic*
    bold_tokens: List[str] = []

    def replace_bold(match: re.Match) -> str:
        idx = len(bold_tokens)
        bold_tokens.append(match.group(1))
        return f"@@BOLD{idx}@@"

    text = re.sub(r"\*\*([^*]+)\*\*", replace_bold, text)

    italic_tokens: List[str] = []

    def replace_italic(match: re.Match) -> str:
        idx = len(italic_tokens)
        italic_tokens.append(match.group(1))
        return f"@@ITALIC{idx}@@"

    text = re.sub(r"\*([^*]+)\*", replace_italic, text)

    # Replace ASCII arrow
    text = text.replace(" -> ", " @@ARROW@@ ")

    escaped = escape_latex_plain(text)

    for idx, inner in enumerate(italic_tokens):
        escaped = escaped.replace(f"@@ITALIC{idx}@@", f"\\emph{{{escape_latex_plain(inner)}}}")

    for idx, inner in enumerate(bold_tokens):
        inner_esc = escape_latex_plain(inner)
        for i_idx, i_inner in enumerate(italic_tokens):
            inner_esc = inner_esc.replace(f"@@ITALIC{i_idx}@@", f"\\emph{{{escape_latex_plain(i_inner)}}}")
        escaped = escaped.replace(f"@@BOLD{idx}@@", f"\\textbf{{{inner_esc}}}")

    escaped = escaped.replace("@@CBCHECKED@@", r"$\boxtimes$")
    escaped = escaped.replace("@@CBUNCHECKED@@", r"$\square$")
    escaped = escaped.replace("@@ARROW@@", r"$\rightarrow$")
    escaped = escaped.replace("@@BR@@", r"\newline ")
    return escaped


def render_metadata_header_block(meta: Dict[str, str], small_font: bool = False) -> str:
    """Render the exact 6-field metadata header block from Pages 2, 4, and 5 of `analysis_form.pdf`."""
    outlet = meta.get("Outlet", "")
    date = meta.get("Date", "")
    title = meta.get("Video title", "")
    timestamps = meta.get("Timestamp(s)", "")
    analyst = meta.get("Analyst", "")
    language = meta.get("Language", "")

    open_sz = "{\\small\n" if small_font else ""
    close_sz = "\n}" if small_font else ""
    lines = [
        r"\par\vspace{6pt}",
        f"{open_sz}\\noindent\\textbf{{Outlet:}} {outlet} \\hfill \\textbf{{Date:}} {date}",
        r"\formrule",
        f"\\noindent\\textbf{{Video title:}} {title}",
        r"\formrule",
        f"\\noindent\\textbf{{Timestamp(s):}} {timestamps}",
        r"\formrule",
        f"\\noindent\\textbf{{Analyst:}} {analyst} \\hfill \\textbf{{Language:}} {language}{close_sz}",
        r"\sectionrule",
    ]
    if "Note" in meta:
        lines.append(f"\\noindent{{\\small\\emph{{Note:}} {meta['Note']}\\par\\vspace{{6pt}}}}")
    return "\n".join(lines)


def render_shared_features_table(table_lines: List[str]) -> str:
    """Render the `Apply the five shared features` table matching `analysis_form.pdf` Pages 2 & 4."""
    rows: List[List[str]] = []
    for ln in table_lines:
        stripped = ln.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped[1:-1].split("|")]
            if all(re.match(r"^:?-{2,}:?$", c) for c in cells):
                continue
            rows.append(cells)

    if len(rows) <= 1:
        return ""

    colspec = (
        r"@{}>{\raggedright\arraybackslash}p{0.18\textwidth}"
        r" >{\raggedright\arraybackslash}p{0.38\textwidth}"
        r" >{\raggedright\arraybackslash}p{0.38\textwidth}@{}"
    )
    out = [
        r"\par\vspace{4pt}",
        r"{\small",
        f"\\begin{{longtable}}{{{colspec}}}",
        r"\toprule",
        r"\textbf{Feature} & \textbf{Exact wording + timestamp} & \textbf{What it does in context} \\",
        r"\midrule",
        r"\endhead",
    ]
    for r_idx, row in enumerate(rows[1:]):
        while len(row) < 3:
            row.append("")
        # Strip leading '1. ', '2. ' etc. and bolding from Feature name to match analysis_form.pdf Page 2 & 4
        feat_raw = re.sub(r"^\*\*(\d+\.\s*)?([^*]+)\*\*$", r"\2", row[0].strip())
        feat_raw = re.sub(r"^\d+\.\s*", "", feat_raw)
        feat_cell = format_inline(feat_raw)
        wording_cell = format_inline(row[1])
        context_cell = format_inline(row[2])
        out.append(f"{feat_cell} & {wording_cell} & {context_cell} \\\\")
        if r_idx < len(rows[1:]) - 1:
            out.append(r"\addlinespace[6pt]")

    out.append(r"\bottomrule")
    out.append(r"\end{longtable}")
    out.append(r"}")
    return "\n".join(out)


def parse_metadata_bullets(lines: List[str], start_idx: int) -> Tuple[Dict[str, str], int]:
    """Parse `- **Outlet:** ...` style metadata lines into a dictionary."""
    meta: Dict[str, str] = {}
    i = start_idx
    n = len(lines)
    while i < n:
        ln = lines[i].strip()
        if not ln:
            i += 1
            continue
        if ln.startswith("- **"):
            # Handle single line `- **Outlet:** ... | **Date:** ...` or `- **Key:** Value`
            if " | **" in ln:
                parts = [p.strip() for p in ln[2:].split("|")]
                for p in parts:
                    m = re.match(r"^\*\*([^*:]+):?\*\*:?\s*(.*)$", p)
                    if m:
                        meta[m.group(1).strip()] = format_inline(m.group(2).strip())
            else:
                m = re.match(r"^-\s+\*\*([^*:]+):?\*\*:?\s*(.*)$", ln)
                if m:
                    key = m.group(1).strip()
                    val = format_inline(m.group(2).strip())
                    if "Analytical Note" in key:
                        meta["Note"] = val
                    else:
                        meta[key] = val
            i += 1
        else:
            break
    return meta, i


def convert_event_section(lines: List[str], start_idx: int, is_event2: bool = False) -> Tuple[str, int]:
    """Convert `## Event1...` or `## Event2...` section into exact `analysis_form.pdf` LaTeX."""
    out: List[str] = []
    if is_event2:
        out.append(r"\newpage")

    header_line = lines[start_idx].strip()[3:].strip()
    out.append(f"\\section*{{{format_inline(header_line)}}}")
    i = start_idx + 1
    n = len(lines)

    # Parse Focus line
    while i < n and not lines[i].strip():
        i += 1
    if i < n and lines[i].strip().startswith("**Focus:**"):
        focus_body = lines[i].strip()[len("**Focus:**") :].strip()
        font_prefix = r"\small " if is_event2 else ""
        out.append(f"\\noindent{{{font_prefix}Focus: {format_inline(focus_body)}}}")
        i += 1

    # Parse metadata fields
    meta, i = parse_metadata_bullets(lines, i)
    out.append(render_metadata_header_block(meta, small_font=is_event2))

    # Parse subsections inside Event 1 / Event 2 (`### Event-specific questions`, `### Apply...`, `### Short summary`)
    while i < n:
        ln = lines[i].strip()
        if not ln:
            i += 1
            continue
        if ln == "---" or ln.startswith("## "):
            if ln == "---":
                i += 1
            break

        if ln.startswith("### Event-specific questions"):
            out.append(r"\subsection*{Event-specific questions}")
            if is_event2:
                out.append(r"{\small")
            out.append(r"\begin{enumerate}[leftmargin=1.5em, itemsep=6pt, topsep=4pt]")
            i += 1
            while i < n:
                cur = lines[i]
                cur_str = cur.strip()
                if not cur_str:
                    i += 1
                    continue
                if cur_str.startswith("### ") or cur_str.startswith("## ") or cur_str == "---":
                    break
                m_q = re.match(r"^(\d+)\.\s+\*\*([^*]+)\*\*\s*$", cur_str)
                if not m_q:
                    m_q = re.match(r"^(\d+)\.\s+(.*)$", cur_str)
                if m_q:
                    q_text = format_inline(m_q.group(2).strip())
                    i += 1
                    ans_parts: List[str] = []
                    while i < n:
                        sub_ln = lines[i]
                        m_sub = re.match(r"^ {2,4}-\s+(.*)$", sub_ln)
                        if m_sub:
                            ans_parts.append(format_inline(m_sub.group(1).strip()))
                            i += 1
                        elif not sub_ln.strip():
                            i += 1
                        else:
                            break
                    ans_joined = "\n\n  ".join(ans_parts)
                    out.append(f"  \\item {q_text}\\par\\smallskip\n  {ans_joined}")
                else:
                    i += 1
            out.append(r"\end{enumerate}")
            if is_event2:
                out.append(r"}")
            continue

        if ln.startswith("### Apply the five shared features"):
            out.append(r"\subsection*{Apply the five shared features}")
            i += 1
            while i < n and not lines[i].strip():
                i += 1
            table_lines: List[str] = []
            while i < n and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            out.append(render_shared_features_table(table_lines))
            continue

        if ln.startswith("### Short summary"):
            out.append(r"\subsection*{Short summary}")
            i += 1
            while i < n:
                cur = lines[i]
                cur_str = cur.strip()
                if not cur_str:
                    i += 1
                    continue
                if cur_str.startswith("### ") or cur_str.startswith("## ") or cur_str == "---":
                    break
                m_prompt = re.match(r"^-\s+\*\*([^*]+)\*\*\s*(.*)$", cur_str)
                if m_prompt:
                    prompt_label = format_inline(m_prompt.group(1).strip())
                    first_ans = format_inline(m_prompt.group(2).strip()) if m_prompt.group(2).strip() else ""
                    i += 1
                    cont_ans: List[str] = [first_ans] if first_ans else []
                    while i < n and lines[i].startswith("  ") and lines[i].strip():
                        cont_ans.append(format_inline(lines[i].strip()))
                        i += 1
                    full_ans = " ".join(cont_ans)
                    out.append(f"\\noindent{{\\small\\textbf{{{prompt_label}}}}}\\par\\smallskip")
                    out.append(f"\\noindent{{\\small {full_ans}}}")
                    out.append(r"\formrule")
                else:
                    i += 1
            continue

        i += 1

    return "\n".join(out), i


def convert_excerpt_records_section(lines: List[str], start_idx: int) -> Tuple[str, int]:
    """Convert `## Common form: Blank excerpt record` into Page 5 layout of `analysis_form.pdf`."""
    out: List[str] = []
    i = start_idx + 1
    n = len(lines)

    # Skip blank lines and the instruction line (we print the header + instruction on each Excerpt Record)
    while i < n:
        cur_str = lines[i].strip()
        if not cur_str or cur_str.startswith("*Copy or print"):
            i += 1
            continue
        break

    while i < n:
        cur_str = lines[i].strip()
        if not cur_str:
            i += 1
            continue
        if cur_str == "---" or cur_str.startswith("## "):
            if cur_str == "---":
                i += 1
            break

        if cur_str.startswith("### Excerpt Record"):
            rec_title = format_inline(cur_str[4:].strip())
            out.append(r"\newpage")
            out.append(r"\section*{Common form: Blank excerpt record}")
            out.append(
                r"\noindent{\small Copy or print this page whenever you find a passage worth analysing. "
                r"Keep the exact wording and enough context to interpret it.}"
            )
            out.append(f"\\par\\smallskip\\noindent{{\\small\\emph{{{rec_title}}}}}")
            i += 1

            # First 3 bullets are Outlet/Date, Video title, Timestamp(s)/Analyst/Language
            meta_lines: List[str] = []
            while i < n:
                s = lines[i].strip()
                if s.startswith("- **Exact transcript excerpt"):
                    break
                if s.startswith("- **"):
                    meta_lines.append(lines[i])
                i += 1
            meta, _ = parse_metadata_bullets(meta_lines, 0)
            out.append(render_metadata_header_block(meta, small_font=True))

            # Now parse the remaining prompts of this Excerpt Record
            while i < n:
                s = lines[i].strip()
                if not s:
                    i += 1
                    continue
                if s.startswith("### Excerpt Record") or s.startswith("## ") or s == "---":
                    break
                m_p = re.match(r"^-\s+\*\*([^*]+)\*\*\s*(.*)$", s)
                if m_p:
                    raw_label = m_p.group(1).strip()
                    inline_rest = m_p.group(2).strip()
                    i += 1
                    body_lines: List[str] = []
                    if inline_rest:
                        body_lines.append(format_inline(inline_rest))
                    while i < n and lines[i].startswith("  ") and lines[i].strip():
                        b_ln = lines[i].strip()
                        if b_ln.startswith("> "):
                            b_ln = b_ln[2:].strip()
                        body_lines.append(format_inline(b_ln))
                        i += 1
                    body_text = " ".join(body_lines)

                    # Match exact label punctuation from Page 5 of analysis_form.pdf
                    if raw_label.startswith("Exact transcript excerpt"):
                        out.append(r"\noindent{\small\textbf{Exact transcript excerpt}}\par\smallskip")
                        out.append(f"\\noindent{{\\small ``{body_text}''}}")
                        out.append(r"\formrule")
                    elif raw_label.startswith("Feature(s)"):
                        out.append(f"\\noindent{{\\small\\textbf{{Feature(s):}} {body_text}}}\\par\\vspace{{6pt}}")
                    elif raw_label.startswith("My interpretation, with reasons"):
                        out.append(r"\noindent{\small\textbf{My interpretation, with reasons}}\par\smallskip")
                        out.append(f"\\noindent{{\\small {body_text}}}")
                        out.append(r"\formrule")
                    else:
                        label_clean = format_inline(raw_label)
                        out.append(f"\\noindent{{\\small\\textbf{{{label_clean}}}}}\\par\\smallskip")
                        out.append(f"\\noindent{{\\small {body_text}}}")
                        out.append(r"\formrule")
                else:
                    i += 1
            continue

        i += 1

    return "\n".join(out), i


def convert_end_of_event_summary_section(lines: List[str], start_idx: int) -> Tuple[str, int]:
    """Convert `## Common form: End-of-event summary` into Page 6 layout of `analysis_form.pdf`."""
    out: List[str] = [
        r"\newpage",
        r"\section*{Common form: End-of-event summary}",
    ]
    i = start_idx + 1
    n = len(lines)

    while i < n:
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        if s.startswith("### End-of-Event Summary"):
            sub_title = format_inline(s[4:].strip())
            out.append(f"\\subsection*{{{sub_title}}}")
            i += 1
            continue
        if s.startswith("*Research reminder:"):
            rem_text = format_inline(s.strip("*"))
            out.append(r"\vfill")
            out.append(f"\\noindent{{\\small {rem_text}}}")
            i += 1
            continue
        m_p = re.match(r"^-\s+\*\*([^*]+)\*\*\s*(.*)$", s)
        if m_p:
            label = format_inline(m_p.group(1).strip())
            rest = format_inline(m_p.group(2).strip()) if m_p.group(2).strip() else ""
            i += 1
            cont: List[str] = [rest] if rest else []
            while i < n and lines[i].startswith("  ") and lines[i].strip():
                cont.append(format_inline(lines[i].strip()))
                i += 1
            full_val = " ".join(cont)
            out.append(f"\\noindent{{\\small\\textbf{{{label}}}}}\\par\\smallskip")
            out.append(f"\\noindent{{\\small {full_val}}}")
            out.append(r"\formrule")
            continue
        i += 1

    return "\n".join(out), i


def convert_worksheet_markdown_to_exact_form_latex(md_text: str) -> str:
    """Convert a Creator Analysis Worksheet Markdown file into the exact LaTeX structure of `analysis_form.pdf`."""
    lines = md_text.splitlines()
    n = len(lines)
    sections_out: List[str] = [PAGE1_GUIDELINES_LATEX]

    i = 0
    while i < n:
        s = lines[i].strip()
        if s.startswith("## Event1."):
            ev1_latex, i = convert_event_section(lines, i, is_event2=False)
            sections_out.append(ev1_latex)
            continue
        if s.startswith("## Event2."):
            ev2_latex, i = convert_event_section(lines, i, is_event2=True)
            sections_out.append(ev2_latex)
            continue
        if s.startswith("## Common form: Blank excerpt record"):
            exc_latex, i = convert_excerpt_records_section(lines, i)
            sections_out.append(exc_latex)
            continue
        if s.startswith("## Common form: End-of-event summary"):
            sum_latex, i = convert_end_of_event_summary_section(lines, i)
            sections_out.append(sum_latex)
            continue
        i += 1

    return "\n\n".join(sections_out)


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
        body_latex = convert_worksheet_markdown_to_exact_form_latex(md_text)
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
        + "\n\n\\clearpage\n\\setcounter{page}{1}\n\n".join(combined_bodies)
        + "\n\n\\end{document}\n"
    )
    master_path = LATEX_DIR / "All_6_Creators_Analysis_Overleaf.tex"
    master_path.write_text(master_tex, encoding="utf-8")
    print(f"Generated {master_path.relative_to(PROJECT_DIR)} ({master_path.stat().st_size / 1024:.1f} KB)")

    return individual_paths, master_path


if __name__ == "__main__":
    generate_all_latex_files()
    sys.exit(0)
