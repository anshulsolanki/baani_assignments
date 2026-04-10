# Assignment 3 Part 2: HMM and CRF Sequence Modeling

**Student ID**: 2025114016 (Assumed from folder name)

## 1. Introduction
This report presents the implementation and evaluation of Hidden Markov Model (HMM) and Conditional Random Field (CRF) taggers for Part of Speech (POS), Chunk, and Named Entity Recognition (NER) tagging tasks in English and Hindi. The models were trained on standard gold datasets (and LLM-generated data for NER) and evaluated against a manually annotated dataset.

## 2. Data Description
- **English**: Gold data from `UD_English-EWT` for POS tagging. `llm_dataset.conll` used for English NER training.
- **Hindi**: Gold data from LTRC Shallow Parsing repository (`hindi-train.txt`) for POS and Chunk tagging.
- **Evaluation**: `manual_dataset.conll` containing manually annotated sentences for both languages.

## 3. Methodology

### 3.1 HMM Tagger
- Implemented with Laplace smoothing ($\alpha=1.0$) to handle zero probabilities.
- Viterbi algorithm used for decoding.

### 3.2 CRF Tagger
- Implemented using `sklearn-crfsuite`.
- **Features**: Word identity, lowercase word, prefixes/suffixes, shape features, and context features (+/- 1 word).

### 3.3 Tag Mapping
To handle discrepancies between training data and manual dataset for Hindi:
- **POS**: `N_NN` -> `NN`, `V_VM` -> `VM`, etc.
- **Chunk**: `B-VGF` -> `B-VP`, etc.

## 4. Results

### 4.1 POS Tagging Accuracy
| Model | English | Hindi |
| :--- | :--- | :--- |
| **HMM** | 0.8047 | 0.7181 |
| **CRF** | 0.9186 | 0.7886 |

### 4.2 Chunking F1 Score (Hindi)
| Model | F1 Score |
| :--- | :--- |
| **HMM** | 0.2814 |
| **CRF** | 0.4026 |

### 4.3 NER F1 Score (English)
| Model | F1 Score |
| :--- | :--- |
| **CRF (Trained on LLM data)** | 0.0190 |

*Note: The low NER score is due to mixed and noisy labels in the LLM-generated training data.*

## 5. Error Analysis

### 5.1 English CRF POS Errors
- Quotes (``) misclassified as `NOUN` or `PROPN` instead of `PUNCT`.
- "Committee" misclassified as `NOUN` instead of `PROPN`.

### 5.2 Hindi CRF POS Errors
- **apne**: Predicted as `PR_PRF` (Reflexive) instead of `PRP` (Personal). This is a tagset granularity difference.
- **padosi**: Predicted as `NNP` instead of `JJ`. Used as an adjective in context but seen as noun in training.

### 5.3 Hindi CRF Chunking Errors
- **padosi**: Predicted as `B-NP` instead of `I-NP`. Boundary detection error.
- **se**: Predicted as `I-NP` instead of `B-PP`. Postposition attached to noun phrase instead of starting a prepositional phrase.

### 5.4 English CRF NER Errors
- `The` predicted as `B-NP` (Chunk tag) instead of `O`.
- `December` predicted as `O` instead of `B-DATE`.
- The model confused Chunk tags with NER tags due to mixed labels in training data.

## 5.5 Comparison with LLM Annotations
- **Data Quality**: The LLM-generated data (`llm_dataset.conll`) used for NER training was found to be noisy, mixing POS/Chunk tags with NER tags in the same column. This led to poor performance of the CRF model trained on it.
- **HMM vs CRF**: CRF consistently outperformed HMM by leveraging rich contextual and morphological features, which HMM cannot easily incorporate due to independence assumptions.
- **LLM Behavior**: LLMs tend to be good at identifying entities but may not follow strict annotation guidelines (like IOB format) consistently unless heavily prompted, resulting in noise compared to gold-standard human annotations.

## 6. Conclusion
CRF models generally outperformed HMMs. Data quality and tagset consistency are critical for performance.
