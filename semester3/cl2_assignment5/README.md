# Computational Linguistics 2 — Assignment 5
## Discourse-Based Text Summarization using Rhetorical Structure Theory (RST)

- **Student Name:** Baani Solanki
- **Roll Number:** `2025114016`

---

## 1. Overview & Included Files

This repository implements an end-to-end **Rhetorical Structure Theory (RST) Discourse-Based Text Summarization** pipeline across the 10 benchmark paragraphs in `paragraph.txt` (from Mann & Thompson, 1988).

- `rst_summarization.py`: Main modular Python script with a strict 1-to-1 mapping to the assignment problems:
  - `problem_1(paragraphs)`: Runs the pretrained `isanlp_rst` discourse parser (`hf_model_name='tchewik/isanlp_rst_v3'`, `hf_model_version='rstdt'`) on all 10 paragraphs and prints the complete binary RST discourse trees and relation labels.
  - `problem_2(paragraphs, parsed_trees)`: Extracts structured EDU-level and sentence-level Nucleus/Satellite roles, relation labels, tree depths, Marcu (2000) promotion depths, and path nuclearity ratios.
  - `problem_3(structured_data)`: Applies five transparent RST discourse rules to score sentences and generate 1-to-2 sentence extractive summaries for each paragraph.
  - `problem_4(structured_data, rule_summaries)`: Compares the rule-based RST summaries against a 2-to-3 sentence ChatGPT baseline and computes Sentence Selection Accuracy, Precision, Recall, F1-score, and Content-Word Overlap F1.
  - `problem_5(overall_metrics)`: Summarizes empirical findings, rule patterns that succeeded or struggled, and concrete system improvements.
  - `extra_credit(structured_data)`: Trains a from-scratch L2-regularized Logistic Regression model (`SimpleLogisticRegression`) to learn weights for Nucleus and Satellite relations and evaluates generalization via Leave-One-Paragraph-Out Cross-Validation (LOPO-CV).
- `paragraph.txt`: The 10 English paragraphs provided for the assignment.
- `rst_trees_cache.json`: Serialized output of the pretrained `isanlp_rst` (`rstdt`) parser across all 10 paragraphs so the script can also run instantly without re-downloading the Hugging Face weights on every run.
- `summarization_results.json` & `output_log.txt`: Generated quantitative results and full console output log.
- `Report.pdf` & `Report.md`: Detailed assignment report containing all parsed RST trees, structured tables, generated summaries, evaluation metrics, discussion, and Extra Credit analysis.

---

## 2. Environment Setup & Installation (macOS / Linux)

### Step 1: Create and Activate a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies
> **Note on `isanlp_rst` on macOS (Apple Silicon / Python 3.11+):**
> The `isanlp_rst` package metadata lists an unused legacy C++ dependency (`jsonnet`) that fails to compile on modern macOS/Python 3.13. Install `isanlp_rst` with `--no-deps` and install its runtime dependencies directly as shown below:

```bash
pip install --upgrade pip
pip install --no-deps isanlp_rst
pip install git+https://github.com/iinemo/isanlp.git
pip install razdel torch transformers huggingface_hub nltk tqdm numpy sentencepiece protobuf pillow playwright lxml matplotlib fire
```

---

## 3. How to Run the Code

Run the complete pipeline from the terminal:

```bash
python3 rst_summarization.py
```

- **Default Fast Execution (using cached `isanlp_rst` trees):** By default, `parse_paragraphs_with_isanlp()` loads the exact `isanlp_rst` (`rstdt`) parse trees from `rst_trees_cache.json` if present, printing all trees, tables, summaries, evaluation metrics, and Logistic Regression weights in `< 1 second`.
- **Force Live `isanlp_rst` Neural Parsing:** If you delete `rst_trees_cache.json` (or pass `force_run=True` in `parse_paragraphs_with_isanlp()`), the script initializes `Parser(hf_model_name='tchewik/isanlp_rst_v3', hf_model_version='rstdt', cuda_device=-1)` from Hugging Face, parses all 10 paragraphs live, and regenerates `rst_trees_cache.json`.
