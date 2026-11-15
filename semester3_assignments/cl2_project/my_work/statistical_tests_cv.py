# Step 6: Statistical Significance Tests, 5-Fold Cross-Validation, and Custom Classifier Verification
# Implements McNemar's test, Paired Bootstrap test, 5-Fold Stratified CV, and from-scratch verification

import csv
import math
import random
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from logistic_regression_model import LogisticRegressionModel
from naive_bayes_model import NaiveBayesModel
from custom_classifiers import CustomNaiveBayes, CustomLogisticRegression


# McNemar's test (with continuity correction) comparing two classifiers on the same test set
def mcnemar_test(y_true, pred_a, pred_b):
    # b = A right & B wrong; c = A wrong & B right
    b = 0
    c = 0
    for yt, pa, pb in zip(y_true, pred_a, pred_b):
        a_ok = (pa == yt)
        b_ok = (pb == yt)
        if a_ok and not b_ok:
            b += 1
        elif not a_ok and b_ok:
            c += 1

    if (b + c) == 0:
        return 0.0, 1.0, b, c

    chi2 = ((abs(b - c) - 1.0) ** 2) / float(b + c)
    # Two-sided p-value from chi-square with 1 degree of freedom: p = erfc(sqrt(chi2 / 2))
    p_val = math.erfc(math.sqrt(chi2 / 2.0))
    return chi2, p_val, b, c


# Paired bootstrap resampling test (1,000 resamples) for accuracy difference (B - A)
def paired_bootstrap_test(y_true, pred_a, pred_b, n_boot=1000, seed=42):
    rng = random.Random(seed)
    n = len(y_true)
    wins = 0

    obs_diff = accuracy_score(y_true, pred_b) - accuracy_score(y_true, pred_a)

    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        acc_a = sum(1 for i in idx if pred_a[i] == y_true[i]) / float(n)
        acc_b = sum(1 for i in idx if pred_b[i] == y_true[i]) / float(n)
        if acc_b > acc_a:
            wins += 1

    # One-sided p-value that B is not better than A
    p_boot = 1.0 - (wins / float(n_boot))
    return obs_diff, p_boot


# Run statistical significance tests across key model pairs on full test and hard subset
def run_significance_tests(predictions_store, hard_idx, out_csv="significance_tests.csv"):
    y_test = predictions_store["y_test"]
    y_hard = [y_test[i] for i in hard_idx]

    pairs = [
        ("Logistic Regression: M0 vs M4 (Full Test)", y_test, predictions_store["LR_M0"], predictions_store["LR_M4"]),
        ("Logistic Regression: M2 vs M4 (Full Test)", y_test, predictions_store["LR_M2"], predictions_store["LR_M4"]),
        ("Naive Bayes: M0 vs M4 (Full Test)", y_test, predictions_store["NB_M0"], predictions_store["NB_M4"]),
        ("Naive Bayes: M1 vs M2 (Full Test)", y_test, predictions_store["NB_M1"], predictions_store["NB_M2"]),
        ("SO-CAL: M2 vs M4 Discourse (Full Test)", y_test, predictions_store["SO-CAL (M2 Baseline)"], predictions_store["SO-CAL (M4 Anaphora+RST)"]),
        (
            "Logistic Regression: M0 vs M4 (Hard Subset)",
            y_hard,
            [predictions_store["LR_M0"][i] for i in hard_idx],
            [predictions_store["LR_M4"][i] for i in hard_idx]
        ),
        (
            "Naive Bayes: M0 vs M4 (Hard Subset)",
            y_hard,
            [predictions_store["NB_M0"][i] for i in hard_idx],
            [predictions_store["NB_M4"][i] for i in hard_idx]
        )
    ]

    rows = []
    for name, yt, pa, pb in pairs:
        chi2, p_mc, b, c = mcnemar_test(yt, pa, pb)
        diff, p_boot = paired_bootstrap_test(yt, pa, pb)
        rows.append({
            "Comparison": name,
            "BaselineRight_NewWrong (b)": b,
            "BaselineWrong_NewRight (c)": c,
            "Accuracy Gain": round(diff, 4),
            "McNemar Chi2": round(chi2, 4),
            "McNemar p-value": round(p_mc, 4),
            "Bootstrap p-value": round(p_boot, 4)
        })

    fieldnames = [
        "Comparison", "BaselineRight_NewWrong (b)", "BaselineWrong_NewRight (c)",
        "Accuracy Gain", "McNemar Chi2", "McNemar p-value", "Bootstrap p-value"
    ]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    return rows


# Run 5-Fold Stratified Cross-Validation across all 2,000 reviews for M0 through M4
def run_cross_validation(splits, k_folds=5, out_csv="cross_validation_results.csv"):
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.naive_bayes import MultinomialNB
    import numpy as np

    all_y = np.array(splits["train"]["y"] + splits["validation"]["y"] + splits["test"]["y"])
    pos_indices = [i for i, y in enumerate(all_y) if y == 1]
    neg_indices = [i for i, y in enumerate(all_y) if y == 0]

    # Build 5 balanced stratified folds (200 pos + 200 neg per fold = 400 per fold)
    folds = [[] for _ in range(k_folds)]
    for idx, p_i in enumerate(pos_indices):
        folds[idx % k_folds].append(p_i)
    for idx, n_i in enumerate(neg_indices):
        folds[idx % k_folds].append(n_i)

    nb_helper = NaiveBayesModel()
    cv_rows = []

    for model_name in ["M0", "M1", "M2", "M3", "M4"]:
        all_X = (
            splits["train"]["X"][model_name]
            + splits["validation"]["X"][model_name]
            + splits["test"]["X"][model_name]
        )

        # Vectorize once per model configuration for fast 5-fold slicing
        vec_lr = DictVectorizer()
        X_mat_lr = vec_lr.fit_transform(all_X)

        vec_nb = DictVectorizer()
        X_mat_nb = vec_nb.fit_transform(nb_helper._prepare_nb_features(all_X))

        lr_accs, lr_f1s = [], []
        nb_accs, nb_f1s = [], []

        for fold_id in range(k_folds):
            te_idx = folds[fold_id]
            test_set = set(te_idx)
            tr_idx = [i for i in range(len(all_y)) if i not in test_set]

            y_tr, y_te = all_y[tr_idx], all_y[te_idx]

            lr = LogisticRegression(max_iter=1000, random_state=42)
            lr.fit(X_mat_lr[tr_idx], y_tr)
            lp = lr.predict(X_mat_lr[te_idx])
            lr_accs.append(accuracy_score(y_te, lp))
            lr_f1s.append(f1_score(y_te, lp))

            nb = MultinomialNB(alpha=1.0)
            nb.fit(X_mat_nb[tr_idx], y_tr)
            np_pred = nb.predict(X_mat_nb[te_idx])
            nb_accs.append(accuracy_score(y_te, np_pred))
            nb_f1s.append(f1_score(y_te, np_pred))

        for clf_label, acc_list, f1_list in [
            ("Logistic Regression", lr_accs, lr_f1s),
            ("Naive Bayes", nb_accs, nb_f1s)
        ]:
            mean_acc = sum(acc_list) / k_folds
            std_acc = math.sqrt(sum((x - mean_acc) ** 2 for x in acc_list) / k_folds)
            mean_f1 = sum(f1_list) / k_folds
            std_f1 = math.sqrt(sum((x - mean_f1) ** 2 for x in f1_list) / k_folds)

            cv_rows.append({
                "Classifier": clf_label,
                "Model": model_name,
                "5-Fold Mean Accuracy": round(mean_acc, 4),
                "5-Fold Std Accuracy": round(std_acc, 4),
                "5-Fold Mean F1": round(mean_f1, 4),
                "5-Fold Std F1": round(std_f1, 4)
            })

    fieldnames = [
        "Classifier", "Model",
        "5-Fold Mean Accuracy", "5-Fold Std Accuracy",
        "5-Fold Mean F1", "5-Fold Std F1"
    ]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in cv_rows:
            writer.writerow(r)

    return cv_rows


# Compare our from-scratch CustomNaiveBayes and CustomLogisticRegression against sklearn
def verify_custom_classifiers(splits, out_csv="custom_vs_sklearn.csv"):
    y_train = splits["train"]["y"]
    y_test = splits["test"]["y"]
    rows = []

    for model_name in ["M0", "M2", "M4"]:
        X_train = splits["train"]["X"][model_name]
        X_test = splits["test"]["X"][model_name]

        c_nb = CustomNaiveBayes(alpha=1.0)
        c_nb.train(X_train, y_train)
        c_nb_pred = c_nb.predict(X_test)

        c_lr = CustomLogisticRegression(lr=0.03, l2_reg=0.005, epochs=12)
        c_lr.train(X_train, y_train)
        c_lr_pred = c_lr.predict(X_test)

        for name, preds in [
            ("Custom Naive Bayes (From Scratch)", c_nb_pred),
            ("Custom Logistic Regression (From Scratch)", c_lr_pred)
        ]:
            rows.append({
                "Implementation": name,
                "Model": model_name,
                "Test Accuracy": round(accuracy_score(y_test, preds), 4),
                "Precision": round(precision_score(y_test, preds), 4),
                "Recall": round(recall_score(y_test, preds), 4),
                "F1": round(f1_score(y_test, preds), 4)
            })

    fieldnames = ["Implementation", "Model", "Test Accuracy", "Precision", "Recall", "F1"]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    return rows
