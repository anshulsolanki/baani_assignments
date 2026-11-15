# Step 5: Hard Contrastive-Discourse & Anaphoric Subset Evaluation and Ablation Studies
# Evaluates M0-M4 on reviews with high discourse contrast/concession and pronoun density

import csv
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from logistic_regression_model import LogisticRegressionModel
from naive_bayes_model import NaiveBayesModel

# Connectives that create rhetorical contrast or concession where surface BoW often fails
CONTRAST_CONCESSION_CUES = {
    "although", "though", "despite", "while", "whereas", "albeit",
    "but", "however", "yet", "nevertheless", "nonetheless", "instead", "still"
}

PRONOUN_CUES = {
    "he", "him", "his", "she", "her", "it", "its", "they", "them", "their"
}


# Score each test review by its rhetorical contrast asymmetry (gap between RST Nucleus
# polarity and raw surface polarity) plus density of contrastive connectives and pronouns
def select_hard_subset_indices(test_reviews, test_m4_X, top_n=60):
    scored_indices = []

    for idx, review in enumerate(test_reviews):
        words = [w.strip(".,!?;:\"'()").lower() for w in review.split()]
        total = max(1, len(words))

        disc_count = sum(1 for w in words if w in CONTRAST_CONCESSION_CUES)
        pron_count = sum(1 for w in words if w in PRONOUN_CUES)

        m4_row = test_m4_X[idx]
        # Asymmetry between surface lexicon polarity and discourse/entity-weighted polarity
        lex_pol = m4_row.get("lex_polarity_density", 0.0) * 25.0
        rst_pol = m4_row.get("rst_weighted_polarity_density", 0.0)
        asymmetry = abs(rst_pol - lex_pol)

        # Competing satellite vs nucleus sentiment
        sat_mass = m4_row.get("rst_satellite_pos_density", 0.0) + m4_row.get("rst_satellite_neg_density", 0.0)

        hardness = asymmetry * 3.0 + sat_mass * 2.0 + (disc_count / total) * 50.0 + (pron_count / total) * 25.0
        scored_indices.append((hardness, idx))

    scored_indices.sort(reverse=True)
    selected = [idx for _, idx in scored_indices[:top_n]]
    selected.sort()
    return selected


# Evaluate M0 through M4 on the Hard Contrastive-Discourse & Anaphoric Subset
def run_hard_subset_evaluation(splits, trained_models, out_csv="hard_subset_results.csv"):
    test_reviews = splits["test"]["reviews"]
    y_test = splits["test"]["y"]
    test_m4_X = splits["test"]["X"]["M4"]

    hard_idx = select_hard_subset_indices(test_reviews, test_m4_X, top_n=60)
    y_hard = [y_test[i] for i in hard_idx]

    rows = []
    for clf_prefix, clf_name in [("LR", "Logistic Regression"), ("NB", "Naive Bayes")]:
        for model_name in ["M0", "M1", "M2", "M3", "M4"]:
            model = trained_models[f"{clf_prefix}_{model_name}"]
            X_hard = [splits["test"]["X"][model_name][i] for i in hard_idx]
            preds = model.predict(X_hard)

            rows.append({
                "Classifier": clf_name,
                "Model": model_name,
                "Subset Size": len(hard_idx),
                "Hard Subset Accuracy": round(accuracy_score(y_hard, preds), 4),
                "Hard Subset Precision": round(precision_score(y_hard, preds, zero_division=0), 4),
                "Hard Subset Recall": round(recall_score(y_hard, preds, zero_division=0), 4),
                "Hard Subset F1": round(f1_score(y_hard, preds, zero_division=0), 4)
            })

    # Also evaluate SO-CAL M2 vs SO-CAL M4 on the hard subset
    for label_name, key in [
        ("SO-CAL (M2 Baseline)", "socal_m2"),
        ("SO-CAL (M4 Anaphora+RST)", "socal_m4")
    ]:
        scores_hard = [splits["test"][key][i] for i in hard_idx]
        preds = [1 if s > -0.05 else 0 for s in scores_hard]
        rows.append({
            "Classifier": label_name,
            "Model": "M2" if "M2" in label_name else "M4",
            "Subset Size": len(hard_idx),
            "Hard Subset Accuracy": round(accuracy_score(y_hard, preds), 4),
            "Hard Subset Precision": round(precision_score(y_hard, preds, zero_division=0), 4),
            "Hard Subset Recall": round(recall_score(y_hard, preds, zero_division=0), 4),
            "Hard Subset F1": round(f1_score(y_hard, preds, zero_division=0), 4)
        })

    fieldnames = [
        "Classifier", "Model", "Subset Size",
        "Hard Subset Accuracy", "Hard Subset Precision", "Hard Subset Recall", "Hard Subset F1"
    ]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    return rows, hard_idx


# Helper to filter feature keys for component-drop ablation experiments
def filter_feature_dict(X_list, drop_prefixes):
    filtered = []
    for row in X_list:
        new_row = {}
        for k, v in row.items():
            if any(k.startswith(pref) for pref in drop_prefixes):
                continue
            new_row[k] = v
        filtered.append(new_row)
    return filtered


# Run Controlled Ablation Study (removing one linguistic module at a time from full M4)
def run_ablation_study(splits, out_csv="ablation_study.csv"):
    y_train = splits["train"]["y"]
    y_val = splits["validation"]["y"]
    y_test = splits["test"]["y"]

    X_train_m4 = splits["train"]["X"]["M4"]
    X_val_m4 = splits["validation"]["X"]["M4"]
    X_test_m4 = splits["test"]["X"]["M4"]

    ablation_configs = [
        ("Full M4 (All Linguistic Modules)", []),
        ("M4 minus RST Features (-rst_*)", ["rst_"]),
        ("M4 minus Anaphora Features (-ana_*)", ["ana_"]),
        ("M4 minus Shifter Features (-shift_*)", ["shift_"]),
        ("M4 minus Prior Lexicon Features (-lex_*)", ["lex_"]),
        ("Dense Linguistic Features Only (No BoW UNI_/BI_)", ["UNI_", "BI_"])
    ]

    rows = []
    for desc, drop_list in ablation_configs:
        tr_X = filter_feature_dict(X_train_m4, drop_list)
        va_X = filter_feature_dict(X_val_m4, drop_list)
        te_X = filter_feature_dict(X_test_m4, drop_list)

        lr = LogisticRegressionModel()
        lr.train(tr_X, y_train)
        val_p = lr.predict(va_X)
        test_p = lr.predict(te_X)

        nb = NaiveBayesModel()
        nb.train(tr_X, y_train)
        nb_test_p = nb.predict(te_X)

        rows.append({
            "Ablation Configuration": desc,
            "LR Val Accuracy": round(accuracy_score(y_val, val_p), 4),
            "LR Test Accuracy": round(accuracy_score(y_test, test_p), 4),
            "LR Test F1": round(f1_score(y_test, test_p), 4),
            "NB Test Accuracy": round(accuracy_score(y_test, nb_test_p), 4),
            "NB Test F1": round(f1_score(y_test, nb_test_p), 4)
        })

    fieldnames = [
        "Ablation Configuration",
        "LR Val Accuracy", "LR Test Accuracy", "LR Test F1",
        "NB Test Accuracy", "NB Test F1"
    ]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    return rows
