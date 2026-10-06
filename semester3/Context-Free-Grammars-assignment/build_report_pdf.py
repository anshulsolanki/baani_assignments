"""
Generates a clean, well-formatted 6-page PDF Report ('Report.pdf') with embedded
syntax tree figures for the NLTK Context-Free Grammars assignment.
"""

import os
from fpdf import FPDF


class AssignmentReportPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8.5)
            self.set_text_color(100, 116, 139)
            self.cell(0, 6, "Writing Context-Free Grammars using NLTK -- Assignment Report", align="L")
            self.cell(0, 6, f"Page {self.page_no()}", align="R", new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(203, 213, 225)
            self.line(15, 16, 195, 16)
            self.ln(3)

    def footer(self):
        if self.page_no() == 1:
            self.set_y(-15)
            self.set_font("Helvetica", "I", 8.5)
            self.set_text_color(100, 116, 139)
            self.cell(0, 10, "Page 1", align="C")

    def section_title(self, title):
        self.ln(1)
        self.set_fill_color(30, 58, 138)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 11.5)
        self.cell(0, 8, f"  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def sub_title(self, title):
        self.ln(1)
        self.set_text_color(15, 23, 42)
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(0.8)

    def body_text(self, text):
        self.set_text_color(30, 41, 59)
        self.set_font("Helvetica", "", 9.3)
        self.multi_cell(0, 4.8, text)
        self.ln(1.2)

    def bullet_item(self, bold_prefix, text):
        self.set_text_color(30, 41, 59)
        self.set_font("Helvetica", "B", 9.2)
        self.write(4.8, f"  * {bold_prefix}: ")
        self.set_font("Helvetica", "", 9.2)
        self.write(4.8, text + "\n")
        self.ln(0.8)

    def code_block(self, code_str):
        self.set_fill_color(248, 250, 252)
        self.set_draw_color(203, 213, 225)
        self.set_text_color(15, 23, 42)
        self.set_font("Courier", "", 8.0)
        self.multi_cell(0, 4.0, code_str, border=1, fill=True)
        self.ln(2)


def build_report(base_dir):
    fig_dir = os.path.join(base_dir, "figures")
    pdf = AssignmentReportPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(15, 12, 15)
    pdf.set_auto_page_break(auto=True, margin=12)

    # ---------------- Page 1: Title & Part A ----------------
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 9, "Writing Context-Free Grammars using NLTK", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(0, 5.5, "Complete Assignment Report (Parts A, B, C, and D)", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_draw_color(59, 130, 246)
    pdf.set_line_width(0.6)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.set_line_width(0.2)
    pdf.ln(3)

    # Part A
    pdf.section_title("Part A (5 Marks)")
    pdf.sub_title("1. Visualizing the 5 Parse Trees Emitted by the NLTK Parser")
    pdf.body_text(
        "The initial grammar parses the 11-word noun phrase 'a joke about the woman with the umbrella "
        "on the street' with start symbol NP using nltk.parse.BottomUpChartParser. Because the phrase "
        "contains a base NP ('a joke') followed by three Prepositional Phrases (PP1 = 'about the woman', "
        "PP2 = 'with the umbrella', PP3 = 'on the street'), the recursive production NP -> NP PP allows "
        "each PP to attach to different preceding NPs. This yields C_3 = 5 distinct parse trees:"
    )
    pdf.bullet_item(
        "Tree 1",
        "[[[[a joke] [about the woman]] [with the umbrella]] [on the street]] -- All 3 PPs attach to 'a joke'."
    )
    pdf.bullet_item(
        "Tree 2",
        "[[[a joke] [about [[the woman] [with the umbrella]]]] [on the street]] -- 'with the umbrella' modifies 'the woman'; 'on the street' modifies 'a joke...'."
    )
    pdf.bullet_item(
        "Tree 3",
        "[[a joke] [about [[[the woman] [with the umbrella]] [on the street]]]] -- Both 'with the umbrella' and 'on the street' modify 'the woman'."
    )
    pdf.bullet_item(
        "Tree 4",
        "[[a joke] [about [[the woman] [with [[the umbrella] [on the street]]]]]] -- 'on the street' modifies 'the umbrella', which modifies 'the woman', which modifies 'a joke'."
    )
    pdf.bullet_item(
        "Tree 5",
        "[[[a joke] [about the woman]] [with [[the umbrella] [on the street]]]] -- 'about the woman' modifies 'a joke'; 'on the street' modifies 'the umbrella', which attaches to 'a joke about the woman'."
    )

    pdf.sub_title("2. Top-Down Recursive Traversal (Non-Terminal Count & Word Positions)")
    pdf.body_text(
        "We recurse through each emitted nltk.Tree top-down (pre-order) starting from the root node. "
        "In NLTK, every non-word node (both phrasal nodes [NP, PP] and pre-terminal POS nodes [Det, N, P]) "
        "is an instance of nltk.tree.Tree, while words are string leaves."
    )
    pdf.code_block(
        "def recurse_tree_top_down(node, word_index=None, is_root=True):\n"
        "    if word_index is None:\n"
        "        word_index = [0]\n"
        "    if not isinstance(node, Tree):  # Base Case: leaf word printed during recursion\n"
        "        idx = word_index[0]\n"
        "        print(f'Word [{idx:2d}] (Position {idx + 1:2d}): {node}')\n"
        "        word_index[0] += 1\n"
        "        return 0, 0\n"
        "    total_nt = 1\n"
        "    phrasal_nt = 1 if node.height() > 2 else 0\n"
        "    for child in node:              # Top-Down recursion left-to-right\n"
        "        c_tot, c_phr = recurse_tree_top_down(child, word_index, is_root=False)\n"
        "        total_nt += c_tot; phrasal_nt += c_phr\n"
        "    if is_root:\n"
        "        print(f'Number of non-terminal nodes: {total_nt}')\n"
        "    return total_nt, phrasal_nt"
    )
    pdf.body_text(
        "Output across all 5 parse trees (identical for Trees 1 to 5 because every tree applies "
        "4 Det N rules, 3 P NP rules, 3 NP PP rules, and 11 POS rules):"
    )
    pdf.code_block(
        "1. Number of non-terminal nodes (nodes which aren't words): 21\n"
        "   (Breakdown: 10 phrasal nodes [7 NP + 3 PP] + 11 POS-tag nodes [4 Det + 4 N + 3 P] = 21)\n"
        "2. Words with numerical index indicating position in the sentence:\n"
        "   Index  0 (Pos  1): a          Index  6 (Pos  7): the\n"
        "   Index  1 (Pos  2): joke       Index  7 (Pos  8): umbrella\n"
        "   Index  2 (Pos  3): about      Index  8 (Pos  9): on\n"
        "   Index  3 (Pos  4): the        Index  9 (Pos 10): the\n"
        "   Index  4 (Pos  5): woman      Index 10 (Pos 11): street\n"
        "   Index  5 (Pos  6): with"
    )

    # ---------------- Page 2: Part A Trees 1, 2, 3 ----------------
    pdf.add_page()
    pdf.sub_title("Part A.1 Visualizations: Emitted Parse Trees 1, 2, and 3")
    for i in [1, 2, 3]:
        img_path = os.path.join(fig_dir, f"part_a_tree_{i}.png")
        if os.path.exists(img_path):
            pdf.image(img_path, x=35, w=140)
            pdf.ln(1)

    # ---------------- Page 3: Part A Trees 4 and 5 ----------------
    pdf.add_page()
    pdf.sub_title("Part A.1 Visualizations: Emitted Parse Trees 4 and 5")
    for i in [4, 5]:
        img_path = os.path.join(fig_dir, f"part_a_tree_{i}.png")
        if os.path.exists(img_path):
            pdf.image(img_path, x=23, w=164)
            pdf.ln(3)

    # ---------------- Page 4: Part B ----------------
    pdf.add_page()
    pdf.section_title("Part B (5 Marks): Structural Ambiguity in 'They are flying planes'")
    pdf.body_text(
        "The sentence 'They are flying planes' has two distinct structural interpretations:\n"
        "  1. Progressive Action Reading ('They [pilots] are in the act of flying planes'): 'are' is an "
        "auxiliary verb (Aux) combining with the verb phrase [VP [V flying] [NP planes]] via VP -> Aux VP.\n"
        "  2. Copular Description Reading ('Those objects are planes that fly'): 'are' is a main/copular "
        "verb (V) combining with the modified noun phrase [NP [Adj flying] [N planes]] via VP -> V NP.\n"
        "Both required linguistic constraints are respected: (i) NP -> Pro allows an NP to be substituted "
        "with a pronoun ('They'), and (ii) VP -> V NP allows a verb and an immediately following NP to form a VP."
    )
    pdf.code_block(
        "S -> NP VP                   Pro -> 'They' | 'they'\n"
        "VP -> Aux VP | V NP          Aux -> 'are'\n"
        "NP -> Pro | N | Adj N        V -> 'are' | 'flying'\n"
        "Adj -> 'flying'              N -> 'planes'"
    )
    pdf.sub_title("Part B Visualizations: Both Parse Trees Emitted by NLTK")
    for i in [1, 2]:
        img_path = os.path.join(fig_dir, f"part_b_tree_{i}.png")
        if os.path.exists(img_path):
            pdf.image(img_path, x=45, w=120)
            pdf.ln(1)

    # ---------------- Page 5: Part C ----------------
    pdf.add_page()
    pdf.section_title("Part C (5 Marks): Extending Grammar for 'Flying planes can be dangerous'")
    pdf.body_text(
        "In 'Flying planes can be dangerous', the subject 'Flying planes' is structurally ambiguous:\n"
        "  1. Non-Finite VP Subject ('The activity of flying planes can be dangerous'): 'Flying' (V_nf) "
        "and 'planes' (NP) combine via VP_nf -> V_nf NP. Following the Hint, we use the unary rewrite rule "
        "NP -> VP_nf (whose right-hand side is the phrasal category VP_nf) so a non-finite VP can serve "
        "as the subject NP of the sentence.\n"
        "  2. Modified NP Subject ('Planes that are flying can be dangerous'): 'Flying' (Adj) modifies "
        "'planes' (N) via NP -> Adj N."
    )
    pdf.code_block(
        "S -> NP VP                                       Pro -> 'They' | 'they'    Aux -> 'are'\n"
        "VP -> Aux VP_nf | Modal VP | V NP | V AdjP       Modal -> 'can'            V -> 'are' | 'be'\n"
        "VP_nf -> V_nf NP                                 V_nf -> 'flying' | 'Flying'\n"
        "NP -> Pro | N | Adj N | VP_nf                    Adj -> 'flying' | 'Flying' | 'dangerous'\n"
        "AdjP -> Adj                                      N -> 'planes'"
    )
    pdf.sub_title("Part C Visualizations: Both Parse Trees Emitted by NLTK")
    for i in [1, 2]:
        img_path = os.path.join(fig_dir, f"part_c_tree_{i}.png")
        if os.path.exists(img_path):
            pdf.image(img_path, x=42, w=126)
            pdf.ln(1)

    # ---------------- Page 6: Part D ----------------
    pdf.add_page()
    pdf.section_title("Part D (5 Marks): Disambiguation with 'is' vs. 'are'")
    pdf.body_text(
        "Why Ambiguity is Eliminated: The modal auxiliary 'can' ('can be') is uninflected for grammatical "
        "number, so it accepts both singular and plural subjects. Replacing 'can be' with 'is' or 'are' "
        "enforces Subject-Verb Number Agreement:\n"
        "  1. 'Flying planes is dangerous' (Singular Agreement -> 1 Parse): 'is' (V_sg) requires a singular "
        "subject (NP_sg). A non-finite VP acting as a subject ('the act of flying planes', NP_sg -> VP_nf) "
        "is always grammatically singular (as in 'To err is human'). The plural noun 'planes' is embedded "
        "as the object of 'Flying' and is not the head of the subject.\n"
        "  2. 'Flying planes are dangerous' (Plural Agreement -> 1 Parse): 'are' (V_pl) requires a plural "
        "subject (NP_pl). When 'Flying' is an adjective modifying the plural head noun 'planes' "
        "(NP_pl -> Adj N_pl), the noun phrase is plural and agrees exclusively with 'are'."
    )
    pdf.code_block(
        "S -> NP_sg VP_sg | NP_pl VP_pl                            Pro_pl -> 'They' | 'they'\n"
        "NP_sg -> VP_nf                NP_pl -> Pro_pl | N_pl | Adj N_pl\n"
        "VP_nf -> V_nf NP_pl           VP_inf -> V_inf AdjP        Aux_sg -> 'is'   Aux_pl -> 'are'\n"
        "VP_sg -> V_sg AdjP | V_sg NP_sg | Aux_sg VP_nf | Modal VP_inf\n"
        "VP_pl -> V_pl AdjP | V_pl NP_pl | Aux_pl VP_nf | Modal VP_inf\n"
        "AdjP -> Adj                   V_sg -> 'is'   V_pl -> 'are'   V_inf -> 'be'   Modal -> 'can'\n"
        "V_nf -> 'flying' | 'Flying'   Adj -> 'flying' | 'Flying' | 'dangerous'       N_pl -> 'planes'"
    )
    pdf.sub_title("Part D Visualizations: Disambiguated Parse Trees ('is' vs. 'are')")
    for name in ["part_d_is.png", "part_d_are.png"]:
        img_path = os.path.join(fig_dir, name)
        if os.path.exists(img_path):
            pdf.image(img_path, x=45, w=120)
            pdf.ln(1)

    out_path = os.path.join(base_dir, "Report.pdf")
    pdf.output(out_path)
    print(f"Saved formal report PDF to: {out_path}")


if __name__ == "__main__":
    build_report(os.path.dirname(os.path.abspath(__file__)))
