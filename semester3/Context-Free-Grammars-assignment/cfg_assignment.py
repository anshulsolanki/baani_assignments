"""
Writing Context-Free Grammars using NLTK
========================================
Complete implementation for Parts A, B, C, and D.

Contents:
  - Part A:
      1. Parse 'a joke about the woman with the umbrella on the street' using
         NLTK's BottomUpChartParser (emitting 5 trees) and export visual parse
         trees to PDF ('Part_A_Parse_Trees.pdf').
      2. Recurse through each tree in top-down fashion starting from the root
         node and print:
           (1) Number of non-terminal nodes (nodes which aren't words)
           (2) Each word with a numerical index indicating its position in the sentence.
  - Part B:
      Context-free grammar capturing the structural ambiguity in
      'They are flying planes' respecting:
        (i)  an NP is substitutable with a pronoun given the right context; and
        (ii) a verb and an immediately following NP can combine to form a VP.
  - Part C:
      Extended grammar capturing the structural ambiguity in
      'Flying planes can be dangerous' using a unary rewrite rule allowing a
      non-finite VP to serve as the subject of a sentence.
  - Part D:
      Modified grammar incorporating Subject-Verb Number Agreement (singular vs.
      plural) to capture the disambiguation when 'can be' is replaced by 'is'
      or 'are'.
"""

import os
import nltk
from nltk import Nonterminal, nonterminals, Production, CFG
from nltk.tree import Tree
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


# ==============================================================================
# Tree Visualization Helper (Matplotlib -> Vector PDF / PNG)
# ==============================================================================

def _compute_tree_layout(tree):
    """
    Computes (x, y) coordinates for every node in an nltk.Tree so that leaves
    are evenly spaced horizontally and internal nodes are centered above their
    children, matching standard linguistic syntax tree diagrams.
    """
    leaf_counter = [0]
    coords = {}
    edges = []
    nodes_info = []

    def _assign_coords(node, depth=0):
        node_id = id(node) if isinstance(node, Tree) else (id(node), leaf_counter[0], depth)
        if not isinstance(node, Tree):
            # Leaf (word)
            x = float(leaf_counter[0])
            leaf_counter[0] += 1
            y = -float(depth)
            coords[node_id] = (x, y)
            nodes_info.append((node_id, str(node), False, depth))
            return node_id, x, depth

        child_xs = []
        max_d = depth
        for child in node:
            cid, cx, cd = _assign_coords(child, depth + 1)
            child_xs.append(cx)
            edges.append((node_id, cid))
            if cd > max_d:
                max_d = cd

        x = sum(child_xs) / len(child_xs)
        y = -float(depth)
        coords[node_id] = (x, y)
        nodes_info.append((node_id, node.label(), True, depth))
        return node_id, x, max_d

    _, _, max_depth = _assign_coords(tree, 0)
    total_leaves = max(leaf_counter[0], 1)
    return coords, edges, nodes_info, total_leaves, max_depth


def draw_nltk_tree_on_ax(ax, tree, title=None, subtitle=None):
    """
    Draws an nltk.Tree on a matplotlib Axes in clean linguistic syntax tree style.
    """
    coords, edges, nodes_info, total_leaves, max_depth = _compute_tree_layout(tree)

    ax.set_axis_off()

    # Draw parent-to-child connecting lines
    for parent_id, child_id in edges:
        px, py = coords[parent_id]
        cx, cy = coords[child_id]
        ax.plot(
            [px, cx],
            [py - 0.14, cy + 0.16],
            color="#334155",
            linewidth=1.4,
            solid_capstyle="round",
            zorder=1,
        )

    # Draw node labels
    for node_id, label, is_nonterminal, depth in nodes_info:
        x, y = coords[node_id]
        if is_nonterminal:
            # Distinguish phrasal categories vs pre-terminal POS tags by color
            is_pos = label in {
                "Det", "N", "P", "Pro", "Aux", "V", "Adj", "Modal",
                "V_nf", "V_inf", "Pro_pl", "Aux_sg", "Aux_pl",
                "V_sg", "V_pl", "N_pl"
            }
            bg_color = "#EFF6FF" if not is_pos else "#F8FAFC"
            border_color = "#3B82F6" if not is_pos else "#94A3B8"
            text_color = "#1E3A8A" if not is_pos else "#334155"
            ax.text(
                x, y, label,
                ha="center", va="center",
                fontsize=10, fontweight="bold", family="sans-serif",
                color=text_color,
                bbox=dict(
                    boxstyle="round,pad=0.25",
                    facecolor=bg_color,
                    edgecolor=border_color,
                    linewidth=1.0,
                ),
                zorder=3,
            )
        else:
            # Terminal word leaf
            ax.text(
                x, y, f"'{label}'",
                ha="center", va="center",
                fontsize=9.5, style="italic", fontweight="semibold",
                family="serif", color="#0F172A",
                bbox=dict(
                    boxstyle="round,pad=0.22",
                    facecolor="#FEFCE8",
                    edgecolor="#FACC15",
                    linewidth=0.9,
                ),
                zorder=3,
            )

    ax.set_xlim(-0.7, max(total_leaves - 0.3, 1.5))
    ax.set_ylim(-max_depth - 0.7, 0.9)

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", color="#0F172A", pad=14)
    if subtitle:
        ax.text(
            (total_leaves - 1) / 2.0, 0.58, subtitle,
            ha="center", va="center",
            fontsize=9.5, color="#475569", style="italic"
        )


def save_trees_to_pdf(trees_with_meta, pdf_path, fig_dir=None):
    """
    Saves a list of (tree, title, subtitle, png_filename) tuples to a multi-page
    vector PDF file and optionally exports individual PNG images.
    """
    if fig_dir:
        os.makedirs(fig_dir, exist_ok=True)

    with PdfPages(pdf_path) as pdf:
        for tree, title, subtitle, png_name in trees_with_meta:
            _, _, _, total_leaves, max_depth = _compute_tree_layout(tree)
            fig_w = max(9.0, total_leaves * 1.05)
            fig_h = max(5.2, (max_depth + 1) * 0.92)
            fig, ax = plt.subplots(figsize=(fig_w, fig_h))
            draw_nltk_tree_on_ax(ax, tree, title=title, subtitle=subtitle)
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches="tight")
            if fig_dir and png_name:
                fig.savefig(os.path.join(fig_dir, png_name), dpi=220, bbox_inches="tight")
            plt.close(fig)


# ==============================================================================
# PART A: Visualizing Parse Trees & Top-Down Tree Recursion
# ==============================================================================

def recurse_tree_top_down(node, word_index=None, is_root=True):
    """
    Part A.2:
    Recurses through an NLTK parse tree in top-down (pre-order) fashion starting
    from the root node and prints:
      1. Number of non-terminal nodes (nodes which aren't words)
      2. Each word with a numerical index indicating its position in the sentence.
    """
    if word_index is None:
        word_index = [0]  # Mutable counter tracking word position across recursive calls

    # Base Case: Leaf node (a terminal word string, not an nltk.Tree)
    if not isinstance(node, Tree):
        idx = word_index[0]
        print(f"       Word [{idx:2d}] (Position {idx + 1:2d}): {node}")
        word_index[0] += 1
        return 0, 0

    # Top-Down Step: Count current non-terminal node first (root -> children)
    total_non_terminals = 1
    phrasal_non_terminals = 1 if node.height() > 2 else 0

    if is_root:
        print("  -> Top-down recursive traversal starting from root node:")
        print("     Words with numerical index indicating position in the sentence:")

    # Recurse left-to-right through children
    for child in node:
        child_total_nt, child_phrasal_nt = recurse_tree_top_down(
            child, word_index=word_index, is_root=False
        )
        total_non_terminals += child_total_nt
        phrasal_non_terminals += child_phrasal_nt

    if is_root:
        pos_nt = total_non_terminals - phrasal_non_terminals
        print(
            f"     Number of non-terminal nodes (nodes which aren't words): {total_non_terminals} "
            f"({phrasal_non_terminals} phrasal nodes [NP, PP] + {pos_nt} POS-tag nodes [Det, N, P])"
        )

    return total_non_terminals, phrasal_non_terminals


def run_part_a(output_dir="."):
    print("=" * 80)
    print("PART A: Prepositional Phrase Attachment & Top-Down Tree Traversal")
    print("=" * 80)

    grammar_a = CFG.fromstring("""
    NP -> Det N | NP PP
    PP -> P NP
    Det -> 'the' | 'a' | 'an'
    N -> 'joke' | 'woman' | 'umbrella' | 'street'
    P -> 'about' | 'with' | 'on'
    """)

    parser_a = nltk.parse.BottomUpChartParser(grammar_a)
    sentence_a = [
        'a', 'joke', 'about', 'the', 'woman',
        'with', 'the', 'umbrella', 'on', 'the', 'street'
    ]

    trees_a = list(parser_a.parse(sentence_a))
    print(f"\nSentence: {' '.join(sentence_a)}")
    print(f"Total parses emitted by BottomUpChartParser: {len(trees_a)}\n")

    pp_attachment_descriptions = [
        "PP1 ('about the woman'), PP2 ('with the umbrella'), and PP3 ('on the street') all attach to 'a joke'",
        "PP2 ('with the umbrella') attaches to 'the woman'; PP3 ('on the street') attaches to 'a joke...'",
        "PP2 ('with the umbrella') and PP3 ('on the street') both attach to 'the woman'",
        "PP3 ('on the street') attaches to 'the umbrella', which attaches to 'the woman', which attaches to 'a joke'",
        "PP1 ('about the woman') attaches to 'a joke'; PP3 ('on the street') attaches to 'the umbrella', which attaches to 'a joke...'"
    ]

    pdf_items = []
    for idx, tree in enumerate(trees_a, start=1):
        print("-" * 80)
        print(f"Part A - Parse Tree {idx}:")
        print(f"Interpretation: {pp_attachment_descriptions[idx - 1]}")
        print("-" * 80)
        tree.pretty_print()

        # Question A.2: Top-down recursive traversal starting from the root node
        print(f"[Part A.2 Output for Tree {idx}]")
        recurse_tree_top_down(tree)
        print()

        pdf_items.append((
            tree,
            f"Part A — Parse Tree {idx} of {len(trees_a)}",
            pp_attachment_descriptions[idx - 1],
            f"part_a_tree_{idx}.png"
        ))

    pdf_path = os.path.join(output_dir, "Part_A_Parse_Trees.pdf")
    fig_dir = os.path.join(output_dir, "figures")
    save_trees_to_pdf(pdf_items, pdf_path, fig_dir=fig_dir)
    print(f"Saved Part A.1 PDF visualization to: {pdf_path}\n")
    return trees_a, pdf_items


# ==============================================================================
# PART B: Structural Ambiguity in "They are flying planes"
# ==============================================================================

def run_part_b(output_dir="."):
    print("=" * 80)
    print("PART B: Structural Ambiguity in 'They are flying planes'")
    print("=" * 80)

    # Respects:
    # (i)  an NP is substitutable with a pronoun (NP -> Pro)
    # (ii) a verb and an immediately following NP can combine to form a VP (VP -> V NP)
    grammar_b = CFG.fromstring("""
    S -> NP VP
    VP -> Aux VP | V NP
    NP -> Pro | N | Adj N
    Pro -> 'They' | 'they'
    Aux -> 'are'
    V -> 'are' | 'flying'
    Adj -> 'flying'
    N -> 'planes'
    """)

    parser_b = nltk.parse.BottomUpChartParser(grammar_b)
    sentence_b = ['They', 'are', 'flying', 'planes']
    trees_b = list(parser_b.parse(sentence_b))

    print("\nPart B Grammar:")
    print(grammar_b)
    print(f"\nSentence: {' '.join(sentence_b)}")
    print(f"Total parses emitted: {len(trees_b)}\n")

    descriptions_b = [
        "Reading 1 (Progressive Action): 'are' is an Auxiliary + [VP [V flying] [NP planes]] ('They are piloting planes')",
        "Reading 2 (Copular Description): 'are' is a main/copular Verb + [NP [Adj flying] [N planes]] ('Those objects are planes that fly')"
    ]

    pdf_items = []
    for idx, tree in enumerate(trees_b, start=1):
        print(f"--- Part B Parse Tree {idx}: {descriptions_b[idx - 1]} ---")
        tree.pretty_print()
        pdf_items.append((
            tree,
            f"Part B — Parse Tree {idx} ('They are flying planes')",
            descriptions_b[idx - 1],
            f"part_b_tree_{idx}.png"
        ))

    return trees_b, pdf_items


# ==============================================================================
# PART C: Extending Grammar for "Flying planes can be dangerous"
# ==============================================================================

def run_part_c(output_dir="."):
    print("=" * 80)
    print("PART C: Structural Ambiguity in 'Flying planes can be dangerous'")
    print("=" * 80)

    # Uses the Hint:
    # "A non-finite VP can serve as the subject of an English sentence, such as in
    #  the sentences 'To err is human'. It is OK to use a unary rewrite rule with a
    #  right-hand-side element that is a phrasal category."
    # Here:
    #   VP_nf -> V_nf NP   (non-finite VP, e.g., 'Flying planes')
    #   NP -> VP_nf        (unary rewrite rule with a phrasal category on the RHS)
    grammar_c = CFG.fromstring("""
    S -> NP VP
    VP -> Aux VP_nf | Modal VP | V NP | V AdjP
    VP_nf -> V_nf NP
    NP -> Pro | N | Adj N | VP_nf
    AdjP -> Adj
    Pro -> 'They' | 'they'
    Aux -> 'are'
    Modal -> 'can'
    V -> 'are' | 'be'
    V_nf -> 'flying' | 'Flying'
    Adj -> 'flying' | 'Flying' | 'dangerous'
    N -> 'planes'
    """)

    parser_c = nltk.parse.BottomUpChartParser(grammar_c)
    sentence_c = ['Flying', 'planes', 'can', 'be', 'dangerous']
    trees_c = list(parser_c.parse(sentence_c))

    print("\nPart C Extended Grammar:")
    print(grammar_c)
    print(f"\nSentence: {' '.join(sentence_c)}")
    print(f"Total parses emitted: {len(trees_c)}\n")

    descriptions_c = [
        "Reading 1 (Gerundive / Non-Finite VP Subject): [NP [VP_nf [V_nf Flying] [NP planes]]] ('The act of flying planes can be dangerous')",
        "Reading 2 (Modified Noun Phrase Subject): [NP [Adj Flying] [N planes]] ('Planes that are flying can be dangerous')"
    ]

    pdf_items = []
    for idx, tree in enumerate(trees_c, start=1):
        print(f"--- Part C Parse Tree {idx}: {descriptions_c[idx - 1]} ---")
        tree.pretty_print()
        pdf_items.append((
            tree,
            f"Part C — Parse Tree {idx} ('Flying planes can be dangerous')",
            descriptions_c[idx - 1],
            f"part_c_tree_{idx}.png"
        ))

    return trees_c, pdf_items


# ==============================================================================
# PART D: Disambiguation via Number Agreement ("is" vs. "are")
# ==============================================================================

def run_part_d(output_dir="."):
    print("=" * 80)
    print("PART D: Disambiguation with 'is' vs. 'are' (Number Agreement)")
    print("=" * 80)

    # Linguistic reason:
    # - Modal 'can' is uninflected for number, so both singular and plural subjects
    #   can combine with 'can be dangerous'.
    # - 'is' requires a 3rd-person SINGULAR subject (NP_sg). A non-finite VP acting
    #   as a subject ('Flying planes' = the act of flying planes) is grammatically
    #   singular (NP_sg -> VP_nf), so 'Flying planes is dangerous' has ONLY 1 parse.
    # - 'are' requires a PLURAL subject (NP_pl). When 'Flying' is an adjective
    #   modifying the plural head noun 'planes' (NP_pl -> Adj N_pl), the NP is plural,
    #   so 'Flying planes are dangerous' has ONLY 1 parse.
    grammar_d = CFG.fromstring("""
    S -> NP_sg VP_sg | NP_pl VP_pl
    NP_sg -> VP_nf
    NP_pl -> Pro_pl | N_pl | Adj N_pl
    VP_nf -> V_nf NP_pl
    VP_sg -> V_sg AdjP | V_sg NP_sg | Aux_sg VP_nf | Modal VP_inf
    VP_pl -> V_pl AdjP | V_pl NP_pl | Aux_pl VP_nf | Modal VP_inf
    VP_inf -> V_inf AdjP
    AdjP -> Adj
    Pro_pl -> 'They' | 'they'
    Aux_sg -> 'is'
    Aux_pl -> 'are'
    V_sg -> 'is'
    V_pl -> 'are'
    V_inf -> 'be'
    V_nf -> 'flying' | 'Flying'
    Modal -> 'can'
    Adj -> 'flying' | 'Flying' | 'dangerous'
    N_pl -> 'planes'
    """)

    parser_d = nltk.parse.BottomUpChartParser(grammar_d)
    print("\nPart D Disambiguated Grammar:")
    print(grammar_d)

    test_sentences = [
        (
            ['Flying', 'planes', 'is', 'dangerous'],
            "Part D — 'Flying planes is dangerous' (Disambiguated: Singular Non-Finite VP Subject)",
            "Only 1 Parse: 'is' (V_sg) agrees solely with singular NP_sg -> VP_nf ('The act of flying planes is dangerous')",
            "part_d_is.png"
        ),
        (
            ['Flying', 'planes', 'are', 'dangerous'],
            "Part D — 'Flying planes are dangerous' (Disambiguated: Plural Modified NP Subject)",
            "Only 1 Parse: 'are' (V_pl) agrees solely with plural NP_pl -> Adj N_pl ('Planes that fly are dangerous')",
            "part_d_are.png"
        ),
        (
            ['Flying', 'planes', 'can', 'be', 'dangerous'],
            "Part D — 'Flying planes can be dangerous' (Still Ambiguous: 2 Parses)",
            "Modal 'can' is unmarked for number and occurs in both VP_sg and VP_pl",
            None
        ),
        (
            ['They', 'are', 'flying', 'planes'],
            "Part D — 'They are flying planes' (Still Captures Both Readings: 2 Parses)",
            "Preserves both progressive (Aux_pl VP_nf) and copular (V_pl NP_pl) readings",
            None
        ),
    ]

    pdf_items = []
    for sent, title, subtitle, png_name in test_sentences:
        trees = list(parser_d.parse(sent))
        print(f"\nSentence: '{' '.join(sent)}' -> Number of parses: {len(trees)}")
        for idx, tree in enumerate(trees, start=1):
            print(f"  [Parse {idx} of {len(trees)}]")
            tree.pretty_print()
            if png_name:
                pdf_items.append((tree, title, subtitle, png_name))

    return pdf_items


def main():
    output_dir = os.path.dirname(os.path.abspath(__file__))
    _, items_a = run_part_a(output_dir)
    _, items_b = run_part_b(output_dir)
    _, items_c = run_part_c(output_dir)
    items_d = run_part_d(output_dir)

    all_pdf_path = os.path.join(output_dir, "All_Assignment_Parse_Trees.pdf")
    fig_dir = os.path.join(output_dir, "figures")
    save_trees_to_pdf(items_a + items_b + items_c + items_d, all_pdf_path, fig_dir=fig_dir)
    print(f"Saved combined parse trees PDF to: {all_pdf_path}")


if __name__ == "__main__":
    main()
