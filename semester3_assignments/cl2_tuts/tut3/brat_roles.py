"""
brat_roles.py
Handles Step 6: Programmatically generates BRAT Standoff annotations (.txt and .ann)
from the PropBank semantic roles extracted in Step 4 (no hardcoded role strings).
"""

import os


def find_offsets(sentence, span_text, start_from=0):
    """
    Finds the 0-indexed (start, end) character offsets of span_text inside sentence.
    """
    clean_sent = sentence.replace("’", "'")
    clean_span = span_text.replace("’", "'")
    idx = clean_sent.find(clean_span, start_from)
    if idx == -1:
        idx = clean_sent.find(clean_span)
    if idx == -1:
        # Handle tokenized spacing differences (e.g. "what 's" vs "what's")
        compact_span = clean_span.replace(" 's", "'s").replace(" ,", ",")
        idx = clean_sent.find(compact_span)
        if idx != -1:
            return idx, idx + len(compact_span), clean_sent[idx:idx + len(compact_span)]
        return 0, len(clean_span), clean_span
    return idx, idx + len(clean_span), clean_sent[idx:idx + len(clean_span)]


def step_6_brat_annotation(sent_num, sentence, assigned_roles, output_dir="brat_annotations"):
    """
    Step 6: Convert the extracted PropBank predicate-argument roles into BRAT
    standoff format (.txt and .ann files) and print the BRAT annotations.
    """
    os.makedirs(output_dir, exist_ok=True)
    clean_sent = sentence.replace("’", "'")

    txt_path = os.path.join(output_dir, f"sentence_{sent_num}.txt")
    ann_path = os.path.join(output_dir, f"sentence_{sent_num}.ann")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(clean_sent + "\n")

    t_id = 1
    e_id = 1
    ann_lines = []
    pred_search_pos = 0

    for item in assigned_roles:
        pred_word = item["predicate"]
        p_start, p_end, p_exact = find_offsets(clean_sent, pred_word, pred_search_pos)
        pred_search_pos = p_end

        pred_tag = f"T{t_id}"
        t_id += 1
        ann_lines.append(f"{pred_tag}\tPredicate {p_start} {p_end}\t{p_exact}")

        event_parts = [f"Predicate:{pred_tag}"]
        for role_label, span_text in item["roles"]:
            a_start, a_end, a_exact = find_offsets(clean_sent, span_text)
            arg_tag = f"T{t_id}"
            t_id += 1
            ann_lines.append(f"{arg_tag}\t{role_label} {a_start} {a_end}\t{a_exact}")
            event_parts.append(f"{role_label}:{arg_tag}")

        ann_lines.append(f"E{e_id}\t{' '.join(event_parts)}")
        e_id += 1

    with open(ann_path, "w", encoding="utf-8") as f:
        f.write("\n".join(ann_lines) + "\n")

    print(f"\n6. BRAT Semantic Role Annotations (saved to {ann_path}):")
    for line in ann_lines:
        print("  ", line)

    return ann_lines
