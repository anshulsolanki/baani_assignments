# Computational Linguistics 2 — Course Project Proposal

**Project Title:**  
**Beyond Bag-of-Words: Discourse- and Anaphora-Aware Sentiment Classification Using Rhetorical Structure Theory (RST) and Compositional Semantics**

**Team Members:**
- **Yashaswi Priya** (Roll No: `2025114007`)
- **Baani Solanki** (Roll No: `2025114016`)

**Course:** Computational Linguistics 2 (Monsoon / Semester 3)  
**Instructors:** Prof. Parameswari Krishnamurthy & Prof. Rajakrishnan Rajkumar

---

## 1. Goal of the Project & Research Questions

### 1.1 Primary Goal
Standard statistical and lexicon-based sentiment classifiers rely on surface **Bag-of-Words (BoW)** representations, treating every clause and entity mention in a document as equally important and independent. Consequently, they fail on multi-sentence texts that exhibit:
1. **Rhetorical Discourse Asymmetry**: In contrastive or concessive sentences (e.g., *"Although the cinematography was breathtaking, the plot was predictable and tedious"*), the author's true stance lies in the **Nucleus** (*"the plot was predictable and tedious"*) rather than the **Satellite** (*"Although the cinematography was breathtaking"*).
2. **Pronominal Anaphora Across Sentences**: Opinions are frequently expressed about pronouns rather than explicit noun phrases (e.g., *"The director adapted a classic novel. While it was a masterpiece, his screenplay was shallow and disjointed"*). Without **anaphora resolution**, sentiment words attach to the wrong entity or lose their discourse anchor.
3. **Compositional Semantic Shifters**: Clause-level **negation scope** (*"never quite succeeds"*), **intensifiers/downtoners** (*"utterly"*, *"slightly"*), and **irrealis/presuppositional modals** (*"could have been great if..."*) systematically invert or scale lexical polarity.

The goal of this project is to **design, implement, and evaluate a non-neural, linguistically grounded sentiment classification system** that integrates **Rhetorical Structure Theory (RST)**, **Computational Anaphora Resolution**, and **Compositional Lexical Semantics** into classical statistical classifiers (**Naive Bayes** and **Logistic Regression**).

### 1.2 Research Questions
1. **RQ1 (Compositional Semantics):** How much does incorporating syntactic negation scope, intensifier/downtoner scaling, and irrealis modal shifting over standard polarity lexicons (MPQA and Hu–Liu) improve classification F1 over a surface Bag-of-Words baseline?
2. **RQ2 (Discourse Structure — RST):** Does segmenting reviews into **Elementary Discourse Units (EDUs)** and differentially weighting **Nucleus** versus **Satellite** clauses (using discourse connectives for *Contrast*, *Concession*, *Cause*, and *Condition*) significantly reduce false predictions on rhetorically complex reviews?
3. **RQ3 (Anaphora & Entity Tracking):** Does resolving third-person pronouns (`he, she, it, they`) using syntactic-semantic constraints (Binding Theory filters + Hobbs' / feature-based anaphora resolution) to track sentiment predicates attached to the primary review topic improve document-level and target-level sentiment accuracy?

---

## 2. How This Proposal Addresses Previous Feedback

| Previous Rejection Reason | How Our New Project Resolves It |
| :--- | :--- |
| **1. Evaluated pre-existing models without original input** | We build our own **rule-based RST discourse segmenter**, **compositional semantic shifter**, **anaphora-linked entity tracker**, and **custom feature-engineered Naive Bayes & Logistic Regression classifiers** from the ground up. |
| **2. Did not utilize linguistic knowledge** | Directly applies **CL2 core theory**: **Rhetorical Structure Theory (RST)** (Nucleus/Satellite asymmetry), **Binding Theory & Anaphora Resolution** (entity-level opinion tracking), and **Compositional Semantics** (polarity lexicons, scope of negation, modality). |
| **3. Relied on Neural Networks / LLMs** | **Strictly zero neural networks or pre-trained LLMs.** Uses only classical statistical models (Naive Bayes, Logistic Regression), CFG/POS parsing, and linguistic rules. |
| **4. Human evaluation was impractical / building a summarizer from scratch was too hard** | Evaluated **100% automatically and objectively** on gold-labeled benchmark corpora using **Precision, Recall, Macro-F1, Accuracy, Confusion Matrices**, and **Ablation Studies**—no human annotation required. |

---

## 3. Scope of the Project

To ensure the project is both **linguistically rich** and **realistically achievable within the semester timeline**, we clearly define the boundaries of our scope:

### 3.1 In-Scope
1. **Clause-Level RST Discourse Parsing (Rule- & Connective-Based):**
   - Segmenting sentences into **Elementary Discourse Units (EDUs)** using punctuation, coordinating/subordinating conjunctions, and NLTK CFG phrase-structure trees (`S`, `SBAR`, `VP`).
   - Identifying four high-impact rhetorical relations via explicit discourse markers:
     - **Concession** (*although, even though, despite, whereas, while*)
     - **Contrast / Antithesis** (*however, but, nevertheless, yet, on the other hand*)
     - **Cause / Result** (*because, therefore, consequently, thus, so that*)
     - **Condition / Irrealis** (*if, unless, provided that, had it been*)
   - Assigning **Nucleus** ($w_N > 1.0$) vs. **Satellite** ($w_S < 1.0$) weights to EDUs based on Mann & Thompson's (1988) canonical nuclearity patterns.
2. **Compositional Lexical Semantics:**
   - Integrating **Hu & Liu's (2004) Opinion Lexicon** and the **MPQA Subjectivity Lexicon (Wilson et al., 2005)** (referencing Topic P21 from the course project list).
   - Implementing syntactic **Negation Scope** (inverting/shifting polarity from a negation cue up to the next clause boundary), **Valence Intensifiers/Downtoners** (multiplicative modifiers), and **Irrealis/Modal Dampening** (neutralizing polarity under counterfactual modals like *would, could, should, might*).
3. **Pronominal Anaphora Resolution for Topical Salience:**
   - Adapting our CL2 Assignment 4 **Anaphora Resolution** pipeline (Binding Theory intra-sentential filters + Hobbs'/feature-based antecedent linking) to resolve pronominal subjects (`it, he, she, they`).
   - Weighting sentiment-bearing predicates higher when their syntactic subject (or resolved antecedent) refers to a **high-frequency topical entity** (discourse center) rather than a peripheral entity.
4. **Classical Statistical Classification & Ablation Study:**
   - Training and comparing **Multinomial/Bernoulli Naive Bayes** and **L2-Regularized Logistic Regression** across 5 cumulative feature sets (Ablation Study) plus a pure rule-based **Semantic-Discourse Aggregation (SO-CAL style)** scorer.

### 3.2 Out-of-Scope
- Full-tree end-to-end neural RST parsing or implicit (connective-less) discourse relation induction.
- Open-domain multi-document coreference resolution beyond third-person pronominal anaphora (`PRP`, `PRP$`) and head-word noun phrase matching.
- Any deep learning, word embeddings (`Word2Vec`/`BERT`), or LLM APIs.

---

## 4. Datasets & Evaluation Metrics

### 4.1 Datasets
1. **Primary Dataset — Cornell Movie Review Polarity Dataset v2.0 (Pang & Lee, 2004):**
   - **Size:** 2,000 full-length movie reviews (1,000 Positive, 1,000 Negative), readily accessible via `nltk.corpus.movie_reviews`.
   - **Why it is ideal for CL2:** Movie reviews are multi-paragraph texts rich in **concessive/contrastive discourse structures** (*"While the acting is strong, the film fails..."*) and **cross-sentence pronominal chains** (*he, she, it, they* referring to actors, directors, characters, and the film itself).
2. **Focused Challenge Subset — "Discourse-Contrastive & Anaphoric" Evaluation Split:**
   - From the test split, we automatically extract a **Hard Linguistic Subset** consisting of reviews with high density of contrastive/concessive connectives (*although, however, but, despite*) and third-person pronouns, allowing us to measure exactly where linguistic knowledge outperforms surface Bag-of-Words.
3. **Lexical Resources:**
   - **Hu & Liu (2004) Opinion Lexicon** (~6,800 positive/negative words).
   - **MPQA Subjectivity Lexicon (Wilson et al., 2005)** (~8,200 words annotated with prior polarity and strong/weak subjectivity).

### 4.2 Objective Evaluation Metrics
- **Accuracy, Precision, Recall, and Macro-F1** (evaluated both on the full test set and the Hard Contrastive-Discourse subset).
- **Confusion Matrices** for each model variant.
- **Controlled Ablation Study** across five progressive configurations:
  1. `M0`: Unigram/Bigram Bag-of-Words Baseline (Naive Bayes & Logistic Regression)
  2. `M1`: `M0` + Polarity Lexicon Features (MPQA + Hu–Liu counts & prior polarity)
  3. `M2`: `M1` + Compositional Semantics (Syntactic Negation Scope + Intensifiers + Irrealis Modals)
  4. `M3`: `M2` + Pronominal Anaphora Resolution & Topical Entity Salience Weighting
  5. `M4`: `M3` + RST Elementary Discourse Unit (Nucleus vs. Satellite) Weighting
- **Qualitative Linguistic Error Analysis:** Detailed inspection of learned Logistic Regression weights and false-positive/false-negative cases.

---

## 5. Tools & Technologies Used

- **Programming Language:** Python 3 (Standard Library: `math`, `re`, `collections`, `csv`, `json`).
- **Linguistic Processing:** `nltk` (Penn Treebank POS tagger, `RegexpParser` CFG chunker/clause segmenter, `WordNetLemmatizer`, `movie_reviews` corpus).
- **Lexicons:** MPQA Subjectivity Lexicon and Hu & Liu Opinion Lexicon.
- **Statistical Classifiers:** Custom Python implementations of **Naive Bayes** (with Laplace/add-$k$ smoothing) and **Logistic Regression** (with L2 regularization), cross-checked with `scikit-learn` for verification and confusion matrix plotting (`matplotlib`).
- **Version Control:** Git & GitHub (following the course commit policy of regular, meaningful commits across multiple days).

---

## 6. Step-by-Step Implementation Plan

```
Raw Review Text
      │
      ▼
[Step 1: Linguistic Preprocessing]
  Sentence Splitting → Tokenization → POS Tagging → CFG NP & Clause Chunking
      │
      ├───────────────────────────────────────────┐
      ▼                                           ▼
[Step 2A: Compositional Semantics (Yashaswi)]   [Step 2B: Discourse & Anaphora (Baani)]
  • MPQA & Hu-Liu Lexicon Lookup                  • EDU Clause Segmentation
  • Syntactic Negation Scope Detection            • Discourse Connective Classification
  • Intensifier / Downtoner Scaling               • RST Nucleus (w_N) vs Satellite (w_S) Tagging
  • Irrealis / Modal Dampening                    • Pronominal Anaphora Resolution & Entity Salience
      │                                           │
      └───────────────────┬───────────────────────┘
                          ▼
        [Step 3: Linguistically Enriched Feature Vector]
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
  [Naive Bayes Classifier]    [Logistic Regression Classifier]
       (Yashaswi)                      (Baani)
            │                           │
            └─────────────┬─────────────┘
                          ▼
  [Step 4: Ablation Study, Confusion Matrices & Linguistic Analysis]
```

1. **Phase 1 — Corpus Preparation & Lexicon Loader:** Load the 2,000 movie reviews (80% train / 10% dev / 10% test stratified split), build the preprocessing pipeline (sentence boundary detection, POS tagging, lemmatization), and parse the Hu–Liu and MPQA lexicons.
2. **Phase 2 — Compositional Semantic Module:** Implement clause-bounded negation scope (`not, never, neither, without, barely`), intensifier/downtoner multipliers (`very: 1.5x`, `extremely: 1.8x`, `slightly: 0.5x`), and irrealis modal detectors (`would, could, should, ought, hoped, expected`).
3. **Phase 3 — RST Discourse Segmenter & Anaphora Salience Module:**
   - Segment sentences into Elementary Discourse Units (EDUs) using punctuation and subordinating/coordinating connectives.
   - Apply nuclearity rules: e.g., in `[Although S1 (Satellite)], [S2 (Nucleus)]`, assign Satellite weight $w_S = 0.4$ and Nucleus weight $w_N = 1.5$; in `[S1], [however S2 (Nucleus)]`, upweight $S2$.
   - Run pronominal anaphora resolution across adjacent sentences to link pronouns (`it, he, she, they`) to their antecedent noun phrases and boost sentiment tokens modifying high-salience discourse entities.
4. **Phase 4 — Statistical Modeling & Ablation Experiments:** Train Naive Bayes and Logistic Regression across configurations `M0` through `M4`, tune hyperparameters ($\alpha$ smoothing for NB; learning rate $\eta$, L2 $\lambda$, and Nucleus/Satellite weights $w_N, w_S$ on the dev set), and evaluate on the test set.
5. **Phase 5 — Linguistic Error Analysis & Report Writing:** Analyze top positive/negative feature weights, compare failure modes of Naive Bayes vs. Logistic Regression, and compile the final PDF report.

---

## 7. Expected Challenges & Mitigation Plan

| Expected Challenge | Impact | Concrete Mitigation Strategy |
| :--- | :--- | :--- |
| **1. Full-document RST tree construction is ambiguous without a heavy parser** | High syntactic ambiguity in long sentences could cause noisy discourse trees. | **Mitigation:** Restrict RST analysis to **intra-sentential and adjacent-sentence Elementary Discourse Units (EDUs)** anchored by explicit lexical discourse connectives (~45 unambiguous connectives from the Penn Discourse Treebank taxonomy), where Nucleus/Satellite directionality is deterministic. |
| **2. Discourse Marker Polysemy** (e.g., *"while"* can be temporal *"while walking"* or concessive *"while the acting was good"*) | Misclassifying temporal *"while"* as a concessive satellite could wrongly downweight a clause. | **Mitigation:** Use **POS-tag and clause-structure patterns** (e.g., `while` followed by `VBG` gerund = Temporal; `while` followed by `[NP + finite VP]` with contrasting polarity = Concession). |
| **3. Cascading Errors in Anaphora Resolution** | Incorrect pronoun resolution in long paragraphs could link sentiment to the wrong noun phrase. | **Mitigation:** Apply strict **Binding Theory (Principles A & B)** and gender/number agreement filters first, and limit antecedent search to a 2-sentence window using our validated Assignment 4 pipeline. |
| **4. Feature Sparsity vs. Overfitting** | Combining unigrams with discourse-weighted features can increase dimensionality. | **Mitigation:** Represent linguistic knowledge both as **dense summary features** (e.g., `nucleus_pos_score`, `satellite_neg_score`, `negated_token_count`, `coref_salient_polarity`) and as **discourse-weighted feature counts**, combined with L2 regularization in Logistic Regression and Laplace smoothing in Naive Bayes. |

---

## 8. Rough Timeline & GitHub Commit Schedule

*(Designed to strictly satisfy the course GitHub policy of consistent, multi-day commits well ahead of the deadline.)*

| Milestone / Dates | Tasks & GitHub Commit Checkpoints | Owner(s) |
| :--- | :--- | :--- |
| **Milestone 1** (Oct 23 – Oct 24) | Finalize & submit project proposal; initialize project directory structure and `README.md` in GitHub repo. | Both |
| **Milestone 2** (Oct 25 – Oct 29) | **Commit 1 & 2:** Implement dataset loader (`movie_reviews`), stratified train/dev/test split, POS/CFG preprocessing pipeline, and `M0` Bag-of-Words baselines. | Yashaswi & Baani |
| **Milestone 3** (Oct 30 – Nov 4) | **Commit 3 & 4:** Implement Lexical & Compositional Semantics module (`M1` & `M2`: MPQA/Hu–Liu lexicons, syntactic negation scope, intensifiers, irrealis modals) + Naive Bayes classifier. | Yashaswi |
| **Milestone 4** (Oct 30 – Nov 4) | **Commit 5 & 6:** Implement RST EDU Segmenter, Nucleus/Satellite connective rules, and Anaphora Entity Salience module (`M3` & `M4`) + Logistic Regression classifier. | Baani |
| **Milestone 5** (Nov 5 – Nov 9) | **Commit 7 & 8:** Integrate all modules (`M0`–`M4`), run full ablation experiments, generate confusion matrices, and evaluate on the Contrastive-Discourse challenge subset. | Both |
| **Milestone 6** (Nov 10 – Final Deadline) | **Commit 9 & 10:** Conduct qualitative linguistic error analysis, inspect top learned weights, finalize `README.md`, and compile final PDF report. | Both |

---

## 9. Clear and Equal Division of Work (50% / 50%)

Because each team member's contribution is evaluated separately (and tracked via GitHub commits), the codebase is modularized into two equal, independent linguistic components plus shared evaluation:

### **Yashaswi Priya (`2025114007`) — Lexical & Compositional Semantics + Naive Bayes**
1. **Data & Lexicon Engineering (`lexicon_semantics.py`):**
   - Parsing and normalizing **Hu & Liu (2004)** and **MPQA Subjectivity (2005)** lexicons; mapping POS tags to lemmatized polarity entries.
2. **Compositional Semantic Shifters (`compositional_rules.py`):**
   - Implementing syntactic **Negation Scope** detection (clause-bounded polarity inversion), **Intensifier/Downtoner** valence scaling, and **Irrealis/Modal** presupposition dampening.
3. **Naive Bayes & Rule-Based Aggregation (`naive_bayes_model.py`):**
   - Implementing Multinomial Naive Bayes with add-$k$ smoothing from scratch and the lexicon-based SO-CAL aggregation baseline.
4. **Evaluation & Confusion Matrices (`evaluate_metrics.py`):**
   - Computing Precision, Recall, Macro-F1, Confusion Matrices, and analyzing semantic shifter errors.

### **Baani Solanki (`2025114016`) — RST Discourse Structure, Anaphora Resolution + Logistic Regression**
1. **RST Elementary Discourse Unit (EDU) Parser (`rst_discourse.py`):**
   - Implementing clause boundary segmentation using NLTK POS/CFG patterns and classifying explicit discourse connectives into *Concession*, *Contrast*, *Cause*, and *Condition*.
   - Implementing **Nucleus vs. Satellite** weight assignment ($w_N, w_S$) and handling discourse marker polysemy (e.g., temporal vs. concessive *while/since*).
2. **Anaphora Resolution & Entity Salience (`anaphora_salience.py`):**
   - Adapting Binding Theory constraints and pronominal anaphora resolution (`he, she, it, they`) to identify topical discourse centers and weight sentiment predicates attached to salient entities.
3. **Logistic Regression Classifier (`logistic_regression_model.py`):**
   - Implementing L2-regularized Logistic Regression from scratch using mini-batch gradient descent, hyperparameter tuning on dev set, and feature weight inspection.
4. **Contrastive Subset & Discourse Error Analysis (`discourse_analysis.py`):**
   - Constructing the Contrastive-Discourse test subset and performing qualitative/quantitative comparison between RST-aware and RST-blind models.

---

## 10. Exact Deliverables

1. **GitHub Repository (`semester3/cl2_project/`):**
   - Clean, modular, well-documented Python codebase (`lexicon_semantics.py`, `compositional_rules.py`, `rst_discourse.py`, `anaphora_salience.py`, `naive_bayes_model.py`, `logistic_regression_model.py`, `main_experiments.py`) with balanced, multi-day commit history from both Yashaswi and Baani.
   - Comprehensive `README.md` with exact reproduction commands and dependency instructions.
2. **Experimental Outputs & Visualizations:**
   - Complete ablation table (`M0` through `M4`) reporting Precision, Recall, Macro-F1, and Accuracy on both the full test set and the Contrastive-Discourse subset.
   - Confusion matrix plots and top learned feature weight tables.
3. **Final Project Report (`Report.pdf`):**
   - Structured academic report detailing linguistic motivation, formal algorithmic descriptions of the Compositional Semantics, Anaphora, and RST modules, quantitative ablation results, and qualitative linguistic error analysis.

---

## 11. Key Research Paper References

1. **Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011).** *Lexicon-Based Methods for Sentiment Analysis.* Computational Linguistics, 37(2), 267–307. *(Foundational paper on SO-CAL: compositional semantic shifters, negation, irrealis modals, and intensifiers without neural networks.)*
2. **Mann, W. C., & Thompson, S. A. (1988).** *Rhetorical Structure Theory: Toward a Functional Theory of Text Organization.* Text - Interdisciplinary Journal for the Study of Discourse, 8(3), 243–281. *(Core theoretical framework for Nucleus vs. Satellite discourse asymmetry.)*
3. **Bhatia, P., Ji, Y., & Eisenstein, J. (2015).** *Better Document-Level Sentiment Analysis from RST Discourse Parsing.* Proceedings of EMNLP 2015, 2212–2218. *(Demonstrates how weighting RST Nuclei over Satellites improves document-level sentiment classification in linear classifiers.)*
4. **Pang, B., & Lee, L. (2004).** *A Sentimental Education: Sentiment Analysis Using Subjectivity Summarization Based on Minimum Cuts.* Proceedings of ACL 2004, 271–278. *(Introduces the Cornell Movie Review dataset and discourse-level subjectivity filtering using Naive Bayes and linear classifiers.)*
5. **Jakob, N., & Gurevych, I. (2010).** *Using Anaphora Resolution to Improve Opinion Target Identification in Movie Reviews.* Proceedings of the ACL 2010 Conference Short Papers, 263–268. *(Demonstrates how resolving pronominal anaphora significantly improves linking opinion words to entities in movie reviews.)*
