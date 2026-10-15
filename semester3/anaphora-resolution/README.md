# Anaphora Resolution Assignment

This repository contains the complete Python implementation and documentation for the **Anaphora Resolution** assignment on the Google GAP Coreference Dataset (based on Jurafsky & Martin, *Speech and Language Processing*, 2nd Edition, Chapter 21).

## Files in This Directory

- `anaphora_resolution.py`: Main Python script implementing **Problems 1 through 8** (using only Python's standard library and `nltk`, including a from-scratch implementation of Logistic Regression `SimpleLogisticRegression` and Rule-Based Hobbs' Algorithm on CFG trees) plus the **Extra Credit** comparison using `scikit-learn`.
- `Understanding_Anaphora_Resolution.md`: Detailed step-by-step study guide explaining the linguistic concepts, mathematical formulation, and implementation details for each problem.
- `Report.pdf` / `Report.md`: Formal assignment report presenting all quantitative results, feature weight rankings, error analyses, and method comparisons.
- `output_log.txt`: Complete execution output of `anaphora_resolution.py` on the GAP dataset.
- `data/`: Directory containing the official GAP dataset splits:
  - `gap-development.tsv` (2,000 segments - Training set)
  - `gap-validation.tsv` (454 segments - Development/Validation set)
  - `gap-test.tsv` (2,000 segments - Test set)

## Requirements

- Python 3.8+
- `nltk` (with `punkt`, `punkt_tab`, `averaged_perceptron_tagger`, and `averaged_perceptron_tagger_eng` resources)
- *(Optional, for Extra Credit only)*: `scikit-learn` (if `scikit-learn` is not installed, Problems 1-8 still run completely and the script gracefully skips the Extra Credit section).

To install NLTK data if not already present:
```bash
python3 -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('averaged_perceptron_tagger'); nltk.download('averaged_perceptron_tagger_eng')"
```

## How to Run the Code

From the `anaphora-resolution` directory, run:

```bash
python3 anaphora_resolution.py
```

The script automatically loads the GAP dataset from `./data/`, executes **Problems 1 to 8** and the **Extra Credit** experiment, and prints all evaluation metrics (Accuracy, Precision, Recall, F1-score, Top-5 Feature Weights, Error Analysis examples, and Method Comparison Tables) to standard output.
