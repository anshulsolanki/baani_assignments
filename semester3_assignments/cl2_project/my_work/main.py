# Main controller script for CL2 Project (Phases 3 & 4):
# Orchestrates independent module tests, M0-M4 evaluation, hard-subset & ablation studies,
# 5-fold cross-validation, statistical significance tests, and qualitative error analysis.

from lexicon_semantics import build_lexicon
from test_components import run_tests as run_phase2_tests
from test_phase3_modules import (
    test_anaphora_module,
    test_rst_module,
    test_full_feature_pipeline
)
from evaluate_models import build_or_load_datasets, evaluate_all_models
from hard_subset_ablation import run_hard_subset_evaluation, run_ablation_study
from statistical_tests_cv import (
    run_significance_tests,
    run_cross_validation,
    verify_custom_classifiers
)
from error_analysis import run_error_analysis


def main():
    print("=================================================================")
    print(" STEP 1-3: Running Phase 2 & Phase 3 Independent Component Tests")
    print("=================================================================")
    run_phase2_tests()
    lexicon = build_lexicon()
    test_anaphora_module(lexicon)
    test_rst_module(lexicon)
    test_full_feature_pipeline(lexicon)

    print("\n=================================================================")
    print(" STEP 4: Extracting Features & Evaluating M0-M4 Across Models")
    print("=================================================================")
    splits = build_or_load_datasets()
    eval_rows, predictions_store, trained_models = evaluate_all_models(splits)

    for r in eval_rows:
        print(
            f"  {r['Classifier']:26s} | {r['Features']:21s} | "
            f"Val Acc: {r['Validation Accuracy']:.4f} | "
            f"Test Acc: {r['Test Accuracy']:.4f} | F1: {r['F1']:.4f}"
        )

    print("\n=================================================================")
    print(" STEP 5: Hard Contrastive-Discourse Subset & Ablation Studies")
    print("=================================================================")
    hard_rows, hard_idx = run_hard_subset_evaluation(splits, trained_models)
    for r in hard_rows:
        print(
            f"  [Hard Subset] {r['Classifier']:26s} | {r['Model']:4s} | "
            f"Acc: {r['Hard Subset Accuracy']:.4f} | F1: {r['Hard Subset F1']:.4f}"
        )

    ablation_rows = run_ablation_study(splits)
    print("\n  --- Controlled Ablation Study (Removing Modules from M4) ---")
    for r in ablation_rows:
        print(
            f"  {r['Ablation Configuration']:48s} | "
            f"LR Test F1: {r['LR Test F1']:.4f} | NB Test F1: {r['NB Test F1']:.4f}"
        )

    print("\n=================================================================")
    print(" STEP 6: Statistical Significance Tests, 5-Fold CV & Custom Models")
    print("=================================================================")
    sig_rows = run_significance_tests(predictions_store, hard_idx)
    for r in sig_rows:
        print(
            f"  {r['Comparison']:44s} | Gain: {r['Accuracy Gain']:+.4f} | "
            f"Boot p={r['Bootstrap p-value']:.4f}"
        )

    cv_rows = run_cross_validation(splits, k_folds=5)
    print("\n  --- 5-Fold Stratified Cross-Validation (2,000 Reviews) ---")
    for r in cv_rows:
        print(
            f"  {r['Classifier']:20s} | {r['Model']:4s} | "
            f"CV Acc: {r['5-Fold Mean Accuracy']:.4f} (+/- {r['5-Fold Std Accuracy']:.4f}) | "
            f"CV F1: {r['5-Fold Mean F1']:.4f}"
        )

    custom_rows = verify_custom_classifiers(splits)
    print("\n  --- Custom From-Scratch Classifiers Verification ---")
    for r in custom_rows:
        print(
            f"  {r['Implementation']:42s} | {r['Model']:4s} | "
            f"Test Acc: {r['Test Accuracy']:.4f} | F1: {r['F1']:.4f}"
        )

    print("\n=================================================================")
    print(" STEP 7: Feature Weight Inspection & Qualitative Error Analysis")
    print("=================================================================")
    ling_w, n_fixed, n_fp, n_fn = run_error_analysis(splits, predictions_store, trained_models)
    print(f"  Test errors corrected by M4 over M0/M2 baselines: {n_fixed}")
    print(f"  Remaining LR_M4 False Positives: {n_fp} | False Negatives: {n_fn}")
    print("  All CSV tables and error_analysis_report.md saved in my_work/!")


if __name__ == "__main__":
    main()
