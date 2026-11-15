# Computational Linguistics 2 (CL-2) — Assignment 6
## Word Embeddings (Co-occurrence Matrix & SVD) and Word Sense Disambiguation (WSD)

- **Student Name:** Baani Solanki
- **Roll Number:** `2025114016`

---

## 1. Modular File Structure

- `main.py`: Main controller script that executes Part I (Tasks 2.1–2.4) on `train.csv` and Part II (Problems 1–7) on `wsd-data/wsd_train.txt`.
- `data_loader.py`: Loads sentences from `train.csv` (ignoring class indices) for Part I and loads tab-separated WSD instances from `wsd-data/wsd_train.txt` for Part II.
- `part1_embeddings.py`: Implements Co-occurrence Matrix construction (`part1_task_2_1`), Truncated SVD dimensionality reduction (`part1_task_2_2`), Cosine Similarity evaluation (`part1_task_2_3`), and Context Window Size comparison (`part1_task_2_4`).
- `part2_preprocessing.py`: Implements sentence/word tokenization and POS tagging (`part2_problem_1`), extracts WordNet senses/glosses/examples for content words in the first 10 training sentences (`part2_problem_2`), and computes Precision, Recall, and F1 (`compute_wsd_metrics`).
- `part2_lesk.py`: Implements the Most Frequent Sense baseline (`part2_problem_3`), Simplified Lesk from scratch (`part2_problem_4`), Improved Lesk with all four enhancements (`part2_problem_5`), and manual evaluation of 10 ambiguous words (`part2_problem_6`).
- `part2_naive_bayes.py`: Implements the Extra Credit Multinomial Naive Bayes WSD classifier from scratch (`part2_problem_7_extra_credit`).
- `first_10_sentences_senses.json`: Generated structured JSON of WordNet senses, glosses, and examples for the first 10 training sentences (Part II, Problem 2).
- `output.txt`: Full execution output log from running `main.py`.
- `Report.md`: Complete assignment report answering all theoretical and experimental analysis questions.
- `Understanding_and_Viva_Guide.md`: Study and viva preparation guide with code mappings and 12 model viva Q&As.

---

## 2. How to Run the Code

1. Activate your virtual environment and install dependencies:
   ```bash
   pip install numpy scipy nltk
   python -m nltk.downloader punkt punkt_tab averaged_perceptron_tagger averaged_perceptron_tagger_eng wordnet stopwords
   ```
2. Run the main script:
   ```bash
   python main.py > output.txt
   ```
