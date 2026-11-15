# Step 7: Feature Weight Inspection and Qualitative Linguistic Error Analysis
# Extracts learned Logistic Regression weights for M4 and identifies qualitative test cases

import csv


# Extract learned weights from Logistic Regression M4 (linguistic features + top lexical features)
def inspect_m4_feature_weights(trained_models, out_csv="feature_weights_M4.csv"):
    lr_m4 = trained_models["LR_M4"].model
    vec = lr_m4.named_steps["vectorizer"]
    clf = lr_m4.named_steps["classifier"]

    feature_names = vec.get_feature_names_out()
    coefs = clf.coef_[0]

    linguistic_rows = []
    lexical_pairs = []

    for fname, weight in zip(feature_names, coefs):
        if fname.startswith(("lex_", "shift_", "ana_", "rst_")):
            linguistic_rows.append({
                "Category": "Linguistic Feature",
                "Feature": fname,
                "Weight": round(float(weight), 4)
            })
        else:
            lexical_pairs.append((float(weight), fname))

    linguistic_rows.sort(key=lambda r: abs(r["Weight"]), reverse=True)
    lexical_pairs.sort(reverse=True)

    top_pos = [
        {"Category": "Top Positive Lexical", "Feature": fn, "Weight": round(w, 4)}
        for w, fn in lexical_pairs[:15]
    ]
    top_neg = [
        {"Category": "Top Negative Lexical", "Feature": fn, "Weight": round(w, 4)}
        for w, fn in lexical_pairs[-15:]
    ]

    all_rows = linguistic_rows + top_pos + top_neg

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Category", "Feature", "Weight"])
        writer.writeheader()
        for r in all_rows:
            writer.writerow(r)

    return linguistic_rows, top_pos, top_neg


# Find concrete test examples where M4 (or NB_M4 / SO-CAL M4) fixed errors made by M0/M2,
# plus remaining hard errors on the test set
def run_error_analysis(splits, predictions_store, trained_models, out_md="error_analysis_report.md"):
    ling_w, top_pos, top_neg = inspect_m4_feature_weights(trained_models)

    test_reviews = splits["test"]["reviews"]
    y_test = predictions_store["y_test"]

    lr_m0 = predictions_store["LR_M0"]
    lr_m4 = predictions_store["LR_M4"]
    nb_m0 = predictions_store["NB_M0"]
    nb_m4 = predictions_store["NB_M4"]
    socal_m2 = predictions_store["SO-CAL (M2 Baseline)"]
    socal_m4 = predictions_store["SO-CAL (M4 Anaphora+RST)"]

    fixed_by_m4 = []
    remaining_fp = []
    remaining_fn = []

    for idx, (rev, actual) in enumerate(zip(test_reviews, y_test)):
        # Reviews where surface baseline (M0 or M2) was wrong and M4 discourse/anaphora was right
        if (lr_m0[idx] != actual and lr_m4[idx] == actual) or (
            nb_m0[idx] != actual and nb_m4[idx] == actual
        ) or (
            socal_m2[idx] != actual and socal_m4[idx] == actual
        ):
            fixed_by_m4.append((idx, actual, rev))

        # Remaining false positives and false negatives in LR_M4
        if actual == 0 and lr_m4[idx] == 1:
            remaining_fp.append((idx, rev))
        elif actual == 1 and lr_m4[idx] == 0:
            remaining_fn.append((idx, rev))

    lines = [
        "# Phase 4: Qualitative Error Analysis & Learned Feature Weight Inspection\n",
        "## 1. Learned Linguistic Feature Weights (Logistic Regression M4)\n",
        "| Feature Name | Learned Weight | Linguistic Interpretation |",
        "| :--- | :---: | :--- |"
    ]

    for row in ling_w:
        fname = row["Feature"]
        w = row["Weight"]
        direction = "Pushes toward Positive (+1)" if w >= 0 else "Pushes toward Negative (0)"
        lines.append(f"| `{fname}` | `{w:+.4f}` | {direction} |")

    lines.append("\n## 2. Examples Corrected by Anaphora (M3) & RST Discourse Weighting (M4)\n")
    lines.append(
        f"Total test reviews where M4 corrected an error made by M0/M2 baseline: **{len(fixed_by_m4)}**\n"
    )

    for idx, actual, rev in fixed_by_m4[:5]:
        gold_str = "Positive (1)" if actual == 1 else "Negative (0)"
        snippet = " ".join(rev.split()[:90]) + " ..."
        lines.append(f"- **Test Review #{idx}** (Gold Label: **{gold_str}**):")
        lines.append(
            f"  - `LR_M0`: {lr_m0[idx]}, `LR_M4`: {lr_m4[idx]} | "
            f"`NB_M0`: {nb_m0[idx]}, `NB_M4`: {nb_m4[idx]} | "
            f"`SO-CAL M2`: {socal_m2[idx]}, `SO-CAL M4`: {socal_m4[idx]}"
        )
        lines.append(f"  - *Excerpt:* \"{snippet}\"\n")

    lines.append("## 3. Remaining Error Cases in M4 (False Positives & False Negatives)\n")
    lines.append(
        f"- **Remaining False Positives (Actual Negative predicted as Positive):** {len(remaining_fp)}"
    )
    for idx, rev in remaining_fp[:3]:
        snippet = " ".join(rev.split()[:75]) + " ..."
        lines.append(f"  - *Test Review #{idx}:* \"{snippet}\"")

    lines.append(
        f"\n- **Remaining False Negatives (Actual Positive predicted as Negative):** {len(remaining_fn)}"
    )
    for idx, rev in remaining_fn[:3]:
        snippet = " ".join(rev.split()[:75]) + " ..."
        lines.append(f"  - *Test Review #{idx}:* \"{snippet}\"")

    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return ling_w, len(fixed_by_m4), len(remaining_fp), len(remaining_fn)
