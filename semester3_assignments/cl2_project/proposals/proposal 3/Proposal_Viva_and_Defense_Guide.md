# CL2 Project Proposal 3 — Viva & Proposal Defense Guide (For Baani & Yashaswi)

This guide prepares you to present and defend **Proposal 3** (*Linguistically Guided Extractive Medical Summarization: From RST, Syntactic Parsing, and Semantic Representations to Feature-Driven Logistic Regression*) to **Prof. Parameswari Krishnamurthy**, **Prof. Rajakrishnan Rajkumar**, and your TAs.

---

## 1. 30-Second Elevator Pitch (What to Say First)

> *"Based on the feedback on our initial medical summarization proposal, we redesigned our project into a **4-stage non-neural linguistic summarization pipeline** on the **BioLaySumm2025 (PLOS and eLife)** datasets.*
>
> *First, in **Stage 1**, we build a **Rule-Based Linguistic Extractive Summarizer** that goes beyond `TF-IDF` and `TextRank` by incorporating three core Computational Linguistics modules: (1) **Rhetorical Structure Theory (RST)** to weight Nucleus conclusion/contrast clauses over Satellite background clauses, (2) a **Syntactic CFG Parser and Anaphora Resolver** to verify main-clause `Subject-Verb-Object` completeness and resolve dangling pronouns, and (3) a **Semantic Representation module** that extracts `<Intervention, Clinical-Predicate, Symptom/Disease>` triples, negation scope, and numeric clinical evidence.*
>
> *Second, in **Stages 2 and 3**, we convert all 15 linguistic rules into a numerical feature vector for each sentence and train a supervised **Logistic Regression** (and **Naive Bayes**) sentence classifier using Oracle ROUGE labels. Third, in **Stage 4**, we inspect the learned weights and **fine-tune the model using the best-performing linguistic features**. Finally, instead of human evaluation, we evaluate automatically using **ROUGE-1/2/L**, our **Python Factual Keyword & Numeric Regex Checker**, and an extrinsic **Symptoms-to-Disease Classifier** to measure how well the summaries preserve clinical meaning."*

---

## 2. Likely Proposal Viva Questions & Model Answers

### Q1: How do you train a Logistic Regression model for extractive summarization when `BioLaySumm2025` only gives a reference summary paragraph, not 0/1 labels for each sentence?
**Answer:**  
We use the standard **Oracle Extractive Labeling** technique from summarization literature (Kupiec et al., 1995; Nallapati et al., 2017):
- For each article in the training set, we compute the `ROUGE-1 + ROUGE-2` F1 overlap between each source sentence $s_i$ and the gold reference summary.
- The top-$K$ sentences that greedily maximize the summary's ROUGE overlap with the gold summary are assigned label $y_i = 1$ (*summary-worthy*), and all remaining sentences receive $y_i = 0$.
- Our **Logistic Regression** classifier is then trained via gradient descent with $L_2$ regularization to predict $P(y_i = 1 \mid \mathbf{x}_i) = \sigma(\mathbf{w}^\top \mathbf{x}_i + b)$ from our 15 linguistic features $\mathbf{x}_i$.

---

### Q2: How do you convert your "Rule-Based Summarizer" into "Features for Logistic Regression"?
**Answer:**  
In **Stage 1 (Rule-Based Summarization)**, each linguistic rule produces a heuristic score or binary trigger (for example, +1.5 if a sentence is an RST *Conclusion/Result* Nucleus, or +1.0 for each `<Treatment, Verb, Disease>` semantic triple).
- In **Stage 2 (Rules-to-Features)**, instead of combining those rules with hand-picked weights, we treat each rule's output as an explicit feature dimension $f_k(s_i)$ in a 15-dimensional feature vector $\mathbf{x}_i \in \mathbb{R}^{15}$ (normalized to $[0, 1]$ or $z$-scores):
  - **Statistical/Graph (`f1`–`f4`):** `TF-IDF` salience, `TextRank` centrality, section/sentence position, length filter.
  - **RST Discourse (`f5`–`f8`):** RST Nucleus score, Satellite concession penalty, *Result/Conclusion* connective cue, *Contrast* connective cue.
  - **Syntactic Parser & Anaphora (`f9`–`f11`):** Main-clause `SVO` completeness from the CFG parser, subordination/parenthetical ratio, and dangling pronoun penalty from Anaphora Resolution.
  - **Semantic Representation (`f12`–`f15`):** `<Subject, Verb, Object>` semantic triple density, Symptom/Disease/Drug concept count, numeric/dosage regex match, and factual vs. speculative modality.
- Logistic Regression then **learns the optimal weight $w_k$ for each linguistic rule directly from data**!

---

### Q3: What does "fine-tune the model using the best-performing features" mean in a non-neural Logistic Regression setup?
**Answer:**  
After training our initial Logistic Regression model on all 15 features (`Stage 3`), some features may be noisy, redundant, or collinear. In **Stage 4**:
1. We rank all 15 features by their standardized learned weights $|w_k|$ and run **Group-Wise Ablation** and **Forward/Backward Feature Selection** on the validation set.
2. We select the **best-performing linguistic feature subset** that maximizes validation `ROUGE` and Factual Keyword/Numeric Coverage, re-tune the $L_2$ regularization hyperparameter $\lambda$ and classification threshold, and apply our **Anaphora & RST Coherence Post-Processor** to produce the final fine-tuned model.

---

### Q4: How do you use a Syntactic Parser (`use a parser`) and Meaning/Semantic Representation in your summarizer?
**Answer:**  
1. **Syntactic Parser (`nltk` POS + `RegexpParser` CFG):**
   - Biomedical articles contain many fragmentary table captions, citation lists, and deeply nested relative clauses (`SBAR`). Our CFG parser chunks sentences into `NP`, `VP`, `PP`, and `SBAR` constituents. We verify whether a sentence has a well-formed main-clause `[Subject NP + Finite Clinical Verb + Object NP]` backbone, downweight parenthetical/subordinate noise, and check for unresolved initial pronouns (*"It", "They"*) using our **Hobbs'/Binding-Theory Anaphora Resolver**.
2. **Meaning / Semantic Representation:**
   - Surface Bag-of-Words cannot tell *who did what to whom*. Using the CFG parse tree, we extract **Predicate–Argument Semantic Triples** of the form `<Agent/Intervention, Clinical-Predicate, Target/Symptom/Disease>` (e.g., `<Metformin, reduced, insulin_resistance>`), tagged with **syntactic negation scope** (`AFFIRMED` vs. `NEGATED`) and **modality** (`FACTUAL` vs. `HYPOTHETICAL`). Sentences rich in factual clinical semantic triples receive higher feature scores.

---

### Q5: How does Rhetorical Structure Theory (RST) help summarize medical articles?
**Answer:**  
In Mann & Thompson's (1988) and Marcu's (2000) RST framework, a scientific text is organized into **Nuclei** (the central claims and results) and **Satellites** (background, concessions, and elaborations):
- For example, in *"Although previous small-scale trials were inconclusive [Satellite: Concession], our randomized cohort study demonstrates a 42% reduction in relapse [Nucleus: Contrast/Result]"*, a surface `TF-IDF` model might weight both clauses equally.
- Our RST module segments sentences into **Elementary Discourse Units (EDUs)** and uses explicit discourse connectives (*therefore, consequently, we demonstrate, however, in contrast* vs. *although, despite, whereas*) to upweight **Nucleus** claims and downweight **Satellite** background.

---

### Q6: Where does "Symptoms-to-Disease Classification" fit into the project?
**Answer:**  
It serves two key roles:
1. **Semantic Concept Lexicon:** Using a standard **Symptom-to-Disease dataset**, we build a domain lexicon of verified *Symptom* and *Disease* expressions that feeds into feature `f13` (`symptom_disease_concept_count`) of our Semantic Representation module.
2. **Extrinsic Clinical Utility Evaluation (Replacing Human Evaluation):** To test whether a generated summary actually preserves diagnostic medical meaning, we train a non-neural **Naive Bayes & Logistic Regression Symptoms-to-Disease Classifier** and evaluate its accuracy when given **only the generated summaries**. If summaries from our Fine-Tuned Linguistic Logistic Regression model achieve higher disease classification F1 than `TF-IDF` or `TextRank` summaries, that objectively proves our linguistic features preserve core clinical semantics!

---

### Q7: How is the work divided 50/50 between Yashaswi and Baani?
**Answer:**  
- **Yashaswi Priya (`2025114007`)** owns **Statistical/Graph Baselines, Semantic Representation, Naive Bayes & Evaluation**:
  - `baselines_tfidf_textrank.py`: `BioLaySumm2025` loader, Oracle ROUGE labeler, `TF-IDF` and `TextRank`.
  - `semantic_representation.py`: `<Subject, Verb, Object>` semantic triple extraction, Symptom/Disease concept mapping, negation scope, and modality.
  - `naive_bayes_clinical.py` & `evaluate_summarization.py`: Naive Bayes sentence extractor, `ROUGE-1/2/L`, Python Factual Keyword & Numeric Regex Checker, and the Extrinsic Symptoms-to-Disease Classifier.
- **Baani Solanki (`2025114016`)** owns **RST Discourse, Syntactic Parser & Anaphora, Logistic Regression & Feature Fine-Tuning**:
  - `rst_discourse_summarizer.py`: EDU segmentation and RST Nucleus vs. Satellite connective weighting.
  - `syntactic_parser_anaphora.py`: CFG phrase-structure parsing (`NP/VP/SBAR`), main-clause `SVO` completeness, and Anaphora Resolution for pronoun repair.
  - `logistic_regression_summarizer.py` & `feature_selection_finetune.py`: Rules-to-Features L2 Logistic Regression from scratch and Stage 4 Feature Ablation & Fine-Tuning.
