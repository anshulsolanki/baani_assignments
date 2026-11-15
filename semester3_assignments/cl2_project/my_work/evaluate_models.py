# Step 4: Evaluate M0 through M4 across Logistic Regression, Naive Bayes, and SO-CAL
# Extracts features once per review for all 5 models (M0, M1, M2, M3, M4) and saves comparison CSVs

import os
import csv
import pickle
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

from preprocess import preprocess, flatten
from lexicon_semantics import build_lexicon, apply_lexicon, lexicon_features
from compositional_rules import apply_shifters, shifter_features
from anaphora_salience import apply_anaphora, anaphora_features
from rst_discourse import apply_rst, rst_features
from features_2 import bow_features
from logistic_regression_model import LogisticRegressionModel
from naive_bayes_model import NaiveBayesModel
from custom_classifiers import CustomNaiveBayes, CustomLogisticRegression


# Load a dataset split (train.csv, validation.csv, or test.csv) using standard csv module
def load_split_csv(filepath):
    reviews = []
    labels = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            reviews.append(row["review"])
            labels.append(int(row["sentiment"]))
    return reviews, labels


# Extract M0, M1, M2, M3, and M4 feature dicts from a single preprocessed review
# (Preprocessing once per review instead of 5 times makes dataset building 5x faster)
def extract_all_models_single_review(review, lexicon):
    sentences = preprocess(review)

    # M0: Surface Bag-of-Words (unigrams + bigrams)
    m0_feats = bow_features(sentences)

    # M1: M0 + Lexicon features
    apply_lexicon(sentences, lexicon)
    m1_feats = dict(m0_feats)
    m1_feats.update(lexicon_features(sentences))

    # M2: M1 + Compositional Shifters (negation, intensifiers, irrealis)
    apply_shifters(sentences)
    m2_feats = dict(m1_feats)
    m2_feats.update(shifter_features(sentences))

    # Also compute M2 SO-CAL score (before M3/M4 token weights)
    tokens = flatten(sentences)
    m2_pol_scores = [t.shifted_polarity for t in tokens if t.prior_polarity != 0]
    socal_m2_score = sum(m2_pol_scores) / len(m2_pol_scores) if m2_pol_scores else 0.0

    # M3: M2 + Pronominal Anaphora Resolution & Entity Salience
    apply_anaphora(sentences)
    m3_feats = dict(m2_feats)
    m3_feats.update(anaphora_features(sentences))

    # M4: M3 + RST EDU Segmentation & Nucleus/Satellite Weighting
    apply_rst(sentences)
    m4_feats = dict(m3_feats)
    m4_feats.update(rst_features(sentences))

    # Also compute M4 Discourse-Aware SO-CAL score (weighted by Anaphora + RST)
    m4_pol_scores = [t.shifted_polarity * t.weight for t in tokens if t.prior_polarity != 0]
    socal_m4_score = sum(m4_pol_scores) / len(m4_pol_scores) if m4_pol_scores else 0.0

    return {
        "M0": m0_feats,
        "M1": m1_feats,
        "M2": m2_feats,
        "M3": m3_feats,
        "M4": m4_feats,
        "socal_m2": socal_m2_score,
        "socal_m4": socal_m4_score
    }


# Build or load cached feature datasets for train, validation, and test splits
def build_or_load_datasets(data_dir="processed_data", cache_file="saved_models/all_features_cache.pkl"):
    if os.path.exists(cache_file):
        print(f"[Info] Loading cached M0-M4 features from {cache_file}...")
        with open(cache_file, "rb") as f:
            return pickle.load(f)

    lexicon = build_lexicon()
    splits = {}

    for split_name in ["train", "validation", "test"]:
        csv_path = os.path.join(data_dir, f"{split_name}.csv")
        reviews, labels = load_split_csv(csv_path)
        print(f"Extracting M0-M4 features for {split_name} ({len(reviews)} reviews)...")

        model_X = {"M0": [], "M1": [], "M2": [], "M3": [], "M4": []}
        socal_m2_scores = []
        socal_m4_scores = []

        for idx, rev in enumerate(reviews):
            if (idx + 1) % 200 == 0 or (idx + 1) == len(reviews):
                print(f"  Processed {idx + 1}/{len(reviews)} reviews in {split_name}")

            extracted = extract_all_models_single_review(rev, lexicon)
            for m in ["M0", "M1", "M2", "M3", "M4"]:
                model_X[m].append(extracted[m])
            socal_m2_scores.append(extracted["socal_m2"])
            socal_m4_scores.append(extracted["socal_m4"])

        splits[split_name] = {
            "reviews": reviews,
            "y": labels,
            "X": model_X,
            "socal_m2": socal_m2_scores,
            "socal_m4": socal_m4_scores
        }

    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    with open(cache_file, "wb") as f:
        pickle.dump(splits, f)
    print(f"[Info] Saved extracted M0-M4 features to {cache_file}")
    return splits


# Evaluate all models (M0-M4) and save results to CSV
def evaluate_all_models(splits, out_csv="all_models_M0_to_M4.csv"):
    y_train = splits["train"]["y"]
    y_val = splits["validation"]["y"]
    y_test = splits["test"]["y"]

    rows = []
    predictions_store = {"y_test": y_test, "y_val": y_val}
    trained_models = {}

    for model_name in ["M0", "M1", "M2", "M3", "M4"]:
        X_train = splits["train"]["X"][model_name]
        X_val = splits["validation"]["X"][model_name]
        X_test = splits["test"]["X"][model_name]

        # 1. Logistic Regression (Normalized)
        lr = LogisticRegressionModel()
        lr.train(X_train, y_train)
        lr_val_pred = lr.predict(X_val)
        lr_test_pred = lr.predict(X_test)
        trained_models[f"LR_{model_name}"] = lr
        predictions_store[f"LR_{model_name}"] = lr_test_pred

        rows.append({
            "Classifier": "Logistic Regression",
            "Features": model_name,
            "Version": "Raw" if model_name == "M0" else "Normalized",
            "Validation Accuracy": round(accuracy_score(y_val, lr_val_pred), 4),
            "Test Accuracy": round(accuracy_score(y_test, lr_test_pred), 4),
            "Precision": round(precision_score(y_test, lr_test_pred), 4),
            "Recall": round(recall_score(y_test, lr_test_pred), 4),
            "F1": round(f1_score(y_test, lr_test_pred), 4)
        })

        # 2. Multinomial Naive Bayes
        nb = NaiveBayesModel()
        nb.train(X_train, y_train)
        nb_val_pred = nb.predict(X_val)
        nb_test_pred = nb.predict(X_test)
        trained_models[f"NB_{model_name}"] = nb
        predictions_store[f"NB_{model_name}"] = nb_test_pred

        rows.append({
            "Classifier": "Naive Bayes",
            "Features": model_name,
            "Version": "Raw" if model_name == "M0" else "Normalized",
            "Validation Accuracy": round(accuracy_score(y_val, nb_val_pred), 4),
            "Test Accuracy": round(accuracy_score(y_test, nb_test_pred), 4),
            "Precision": round(precision_score(y_test, nb_test_pred), 4),
            "Recall": round(recall_score(y_test, nb_test_pred), 4),
            "F1": round(f1_score(y_test, nb_test_pred), 4)
        })

    # 3. Evaluate SO-CAL Baseline (M2) and SO-CAL Discourse-Weighted (M4)
    for tag, key, label_str in [
        ("SO-CAL (M2 Baseline)", "socal_m2", "M2 Lexicon+Shifters"),
        ("SO-CAL (M4 Anaphora+RST)", "socal_m4", "M4 Discourse-Weighted")
    ]:
        val_s = splits["validation"][key]
        test_s = splits["test"][key]

        # Tune threshold on validation set just like Phase 2 notebook
        best_th = 0.0
        best_val_f1 = -1.0
        for step in range(-20, 21):
            th = step * 0.01
            v_pred = [1 if s > th else 0 for s in val_s]
            vf1 = f1_score(y_val, v_pred, zero_division=0)
            if vf1 > best_val_f1:
                best_val_f1 = vf1
                best_th = th

        val_pred = [1 if s > best_th else 0 for s in val_s]
        test_pred = [1 if s > best_th else 0 for s in test_s]
        predictions_store[tag] = test_pred

        rows.append({
            "Classifier": tag,
            "Features": label_str,
            "Version": f"Threshold = {round(best_th, 2)}",
            "Validation Accuracy": round(accuracy_score(y_val, val_pred), 4),
            "Test Accuracy": round(accuracy_score(y_test, test_pred), 4),
            "Precision": round(precision_score(y_test, test_pred, zero_division=0), 4),
            "Recall": round(recall_score(y_test, test_pred, zero_division=0), 4),
            "F1": round(f1_score(y_test, test_pred, zero_division=0), 4)
        })

    # Save table to CSV
    fieldnames = [
        "Classifier", "Features", "Version",
        "Validation Accuracy", "Test Accuracy", "Precision", "Recall", "F1"
    ]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    # Save confusion matrices for all models
    cm_rows = []
    for key, preds in predictions_store.items():
        if key in {"y_test", "y_val"}:
            continue
        cm = confusion_matrix(y_test, preds)
        tn, fp, fn, tp = cm.ravel()
        cm_rows.append({
            "Model": key,
            "TN": int(tn), "FP": int(fp),
            "FN": int(fn), "TP": int(tp)
        })

    with open("confusion_matrices.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Model", "TN", "FP", "FN", "TP"])
        writer.writeheader()
        for r in cm_rows:
            writer.writerow(r)

    return rows, predictions_store, trained_models


if __name__ == "__main__":
    splits = build_or_load_datasets()
    rows, _, _ = evaluate_all_models(splits)
    print("\n=== M0 to M4 Evaluation Summary ===")
    for r in rows:
        print(
            f"{r['Classifier']:26s} | {r['Features']:21s} | "
            f"Val Acc: {r['Validation Accuracy']:.4f} | "
            f"Test Acc: {r['Test Accuracy']:.4f} | F1: {r['F1']:.4f}"
        )
