# Assignment 3 Part 2: HMM and CRF Sequence Modeling

This directory contains the implementation, evaluation, and report for Assignment 3 Part 2, focusing on Part-of-Speech (POS) tagging, Chunking, and Named Entity Recognition (NER) using Hidden Markov Models (HMM) and Conditional Random Fields (CRF).

## Project Structure

- **`hmm_tagger.py`**: Implementation of the HMM tagger.
- **`crf_tagger.py`**: Implementation of the CRF tagger using `sklearn-crfsuite`.
- **`evaluation.py`**: The main execution script that loads data, trains models, and evaluates them.
- **`final_report.md` / `final_report.pdf`**: The final report containing results and error analysis.
- **`generate_pdf.py`**: Script to convert `final_report.md` to `final_report.pdf`.
- **`submission.zip`**: The final submission package containing required files.

---

## Implementation Details

### 1. HMM Tagger (`hmm_tagger.py`)
- **Model**: A Bigram Hidden Markov Model estimating $P(T|W) = \prod P(w_i|t_i)P(t_i|t_{i-1})$.
- **Training**: Computes transition probabilities between tags and emission probabilities of words given tags.
- **Smoothing**: Uses Laplace smoothing ($\alpha=1.0$) to handle unseen transitions and emissions, preventing zero probabilities.
- **Decoding**: Implements the **Viterbi algorithm** to find the most likely sequence of tags for a given sequence of words.

### 2. CRF Tagger (`crf_tagger.py`)
- **Model**: Uses `sklearn-crfsuite.CRF`.
- **Feature Extraction**: Extracts rich features for each word in a sentence, including:
  - The word itself and its lowercase version.
  - Prefixes and suffixes of length 1, 2, and 3.
  - Shape features: `is_capitalized`, `is_title`, `is_digit`.
  - Context features: The same features for the previous and next words (window of +/- 1).

### 3. Evaluation Pipeline (`evaluation.py`)
- **Data Loading**:
  - Loads English POS data from CoNLL-U format (`UD_English-EWT`).
  - Loads Hindi POS and Chunk data from SSF-like text format (LTRC).
  - Loads English NER data from LLM-generated CoNLL file (`llm_dataset.conll`).
  - Loads the manual evaluation data from `manual_dataset.conll` and splits it into English and Hindi sections.
- **Tag Mapping**: Crucial for Hindi data. Mapped fine-grained tags from LTRC training data (like `N_NN`, `V_VGF`) to the coarser tags used in the manual dataset (like `NN`, `B-VP`) to ensure fair evaluation.
- **Execution**: Trains models on the full training sets and evaluates on the manual dataset, printing Accuracy for POS and F1 scores for Chunking/NER (using `seqeval`).

---

## How to Run and Test

### Prerequisites
Ensure you have the required Python packages installed:
```bash
pip install sklearn-crfsuite seqeval markdown fpdf2 numpy
```

### Running the Evaluation
To train the models and see the evaluation results along with error samples, run:
```bash
python3 evaluation.py
```
This will output results for:
- English POS (HMM & CRF)
- English NER (CRF trained on LLM data)
- Hindi POS (HMM & CRF)
- Hindi Chunking (HMM & CRF)

### Regenerating the PDF Report
If you modify `final_report.md` and want to regenerate the PDF:
```bash
python3 generate_pdf.py
```

---

## What to Watch Out For (Important Notes)

1.  **Hindi Tag Mismatches**: The training data (LTRC) and the manual evaluation dataset use different tagsets. If you see extremely low accuracy for Hindi initially, make sure the mapping dictionaries in `evaluation.py` (`load_hindi_train_data` function) are correctly mapping training tags to evaluation tags.
2.  **Noisy LLM Data for NER**: The `llm_dataset.conll` was used to train the English NER model. However, this file contains noisy annotations where Chunk tags or POS tags are mixed into the NER column. Consequently, the NER F1 score is very low (~2%), and the model often predicts Chunk tags instead of NER tags. This is documented in the report as a data quality issue.
3.  **PDF Font Limitations**: The PDF generator uses standard `helvetica`. It cannot render Devanagari (Hindi) characters. In the error analysis section of the report, Hindi words are written in transliterated English (e.g., *apne*, *padosi*) to prevent PDF generation crashes.
4.  **File Paths**: The scripts use absolute paths tailored to this workspace. If you move the project to another machine, you will need to update the paths in `evaluation.py` and `generate_pdf.py`.

---

## Potential Viva Questions

Here are some questions an examiner might ask during a viva, along with brief pointers for answers:

1.  **Q: What is the main difference between HMM and CRF?**
    *   **A**: HMM is a **generative** model that models the joint probability $P(W, T)$. It assumes that the current tag depends only on the previous tag (Markov assumption) and the current word depends only on the current tag. CRF is a **discriminative** model that models the conditional probability $P(T|W)$ directly. It allows using overlapping, global features of the input sequence.

2.  **Q: Why did the CRF perform better than HMM in your experiments?**
    *   **A**: CRF can utilize rich feature representations (like word suffixes, capitalization, and surrounding words) without assuming they are independent. HMM is limited to simple transition and emission probabilities, which causes data sparsity issues and inability to use rich context.

3.  **Q: How did you handle unknown words in HMM?**
    *   **A**: We used **Laplace smoothing** ($\alpha=1.0$) during probability estimation. This adds a small count to all possible emissions and transitions, ensuring that unseen words or transitions do not result in zero probability during Viterbi decoding.

4.  **Q: Explain the Viterbi algorithm briefly. Why do we need it?**
    *   **A**: Viterbi is a dynamic programming algorithm used to find the most likely sequence of hidden states (tags) that results in the observed sequence of events (words). We need it because calculating the probability of all possible tag sequences would be exponentially complex ($O(T^N)$). Viterbi reduces this to $O(N \cdot T^2)$.

5.  **Q: Why was the F1 score for English NER so low in your results?**
    *   **A**: We trained the CRF model for NER using LLM-generated data (`llm_dataset.conll`). This data was noisy and contained mixed tags (e.g., Chunk tags like `B-NP` mixed with NER tags like `B-PER` in the same column). The model learned this noise, leading to poor boundary detection and low F1 score when evaluated against clean manual annotations.

6.  **Q: What was the challenge with Hindi data evaluation, and how did you solve it?**
    *   **A**: The challenge was a **tagset mismatch** between the training data (LTRC format with tags like `N_NN`, `V_VGF`) and the manual evaluation dataset (with tags like `NN`, `B-VP`). We solved it by implementing a mapping dictionary in the data loader to align the training tags with the evaluation tags.
