# Beyond Bag-of-Words: Discourse- and Anaphora-Aware Sentiment Classification Using Rhetorical Structure Theory (RST) and Compositional Semantics

**Yashaswi Priya** (2025114007) & **Baani Solanki** (2025114016)  
*Computational Linguistics 2 — Course Project Proposal (IIIT Hyderabad)*

---

## 1. Goal of the Project & Research Question

Standard Bag-of-Words (BoW) and surface lexicon sentiment classifiers treat every clause and entity mention in a document as equally salient and independent. Consequently, they systematically fail on multi-sentence texts that exhibit:

1. **Rhetorical Discourse Asymmetry (RST):** In concessive or contrastive sentences (e.g., *"Although the cinematography was breathtaking [Satellite], the plot was predictable and tedious [Nucleus]"*), the author's true stance resides in the **Nucleus** clause rather than the conceded **Satellite** clause.
2. **Cross-Sentence Pronominal Anaphora:** Sentiment predicates frequently modify third-person pronouns (*he, she, it, they*) rather than explicit noun phrases (e.g., *"The director adapted a classic novel. While it was a masterpiece, his screenplay was shallow"*). Without anaphora resolution, opinion words lose their target entity anchor.
3. **Compositional Semantic Shifters:** Syntactic **negation scope** (*not, never, barely*), **intensifiers/downtoners** (*utterly, slightly*), and **irrealis modals** (*would, could, should*) invert or scale lexical polarity within clause boundaries.

**Research Question:** *To what extent does integrating (1) Compositional Lexical Semantics, (2) Pronominal Anaphora Resolution for topical entity salience, and (3) Rhetorical Structure Theory (RST) Nucleus–Satellite discourse weighting improve non-neural sentiment classification (Naive Bayes and Logistic Regression) over surface Bag-of-Words baselines?*

---

## 2. Scope of the Project & Methodology (Strictly Non-Neural)

- **In-Scope:** We design and implement a modular linguistic pipeline from scratch in Python and evaluate five progressive configurations (`M0` $\to$ `M4`) in a controlled ablation study:
  1. **Compositional Lexical Semantics (`M1` & `M2`):** Map POS-tagged lemmas to prior polarity scores using the **MPQA Subjectivity Lexicon** and **Hu & Liu Opinion Lexicon**. Implement syntactic clause-bounded **Negation Scope**, multiplicative **Intensifiers/Downtoners**, and **Irrealis Modal Dampening** (following Taboada et al.'s SO-CAL framework).
  2. **Pronominal Anaphora & Topical Salience (`M3`):** Apply **Binding Theory** intra-sentential constraints and **Hobbs'/feature-based anaphora resolution** across a 2-sentence window to resolve pronouns (*he, she, it, they*) to antecedent NPs, weighting sentiment predicates attached to high-frequency topical entities (discourse centers).
  3. **Rule-Based RST Discourse Segmentation & Weighting (`M4`):** Segment sentences into **Elementary Discourse Units (EDUs)** using NLTK CFG clause boundaries (`S`, `SBAR`) and classify ~45 explicit discourse connectives into *Concession* (*although, despite, while*), *Contrast* (*however, but, yet*), *Cause* (*because, therefore*), and *Condition* (*if, unless*) to upweight **Nucleus** EDUs ($w_N > 1$) and downweight **Satellite** EDUs ($w_S < 1$).
  4. **Statistical Classification:** Compare custom **Multinomial Naive Bayes** (add-$k$ smoothing) and **L2-Regularized Logistic Regression** classifiers alongside a pure rule-based SO-CAL aggregation scorer.
- **Out-of-Scope:** Neural networks, pre-trained embeddings/LLMs, implicit (connective-less) discourse parsing, and human evaluation.

---

## 3. Datasets, Tools & Objective Evaluation Metrics

- **Datasets & Lexicons:** (1) **Cornell Movie Review Polarity Dataset v2.0 (Pang & Lee, 2004)** — 2,000 full-length reviews (1,000 Positive, 1,000 Negative; 80/10/10 stratified split via `nltk.corpus.movie_reviews`), plus a **Hard Contrastive-Discourse & Anaphoric Subset**; (2) **MPQA Subjectivity Lexicon** (~8,200 words) & **Hu–Liu Opinion Lexicon** (~6,800 words).
- **Tools Used:** Python 3 standard library, `nltk` (POS tagger, `RegexpParser` CFG chunker, WordNet lemmatizer), custom Naive Bayes and Logistic Regression implementations, and `scikit-learn`/`matplotlib` for verification and confusion matrix plots.
- **Evaluation Metrics:** Precision, Recall, Macro-F1, Accuracy, Confusion Matrices, and Ablation Analysis across `M0`–`M4`, paired with qualitative linguistic inspection of learned Logistic Regression weights.

---

## 4. Expected Challenges & Mitigation Plan

- **Full RST tree ambiguity:** Restrict RST analysis to intra-sentential and adjacent-sentence EDUs anchored by explicit lexical connectives where Nucleus/Satellite directionality is deterministic.
- **Discourse marker polysemy** (e.g., temporal vs. concessive *"while"*): Disambiguate via POS/CFG subcategorization rules (e.g., `while + VBG` = Temporal vs. `while + finite S` with contrasting polarity = Concession).
- **Cascading anaphora errors:** Enforce gender/number agreement and Binding Theory Principles A & B within a 2-sentence window.

---

## 5. Exact Deliverables & Key Research Paper References

**Deliverables:** (1) GitHub repository with modular Python code (`lexicon_semantics.py`, `compositional_rules.py`, `rst_discourse.py`, `anaphora_salience.py`, `naive_bayes_model.py`, `logistic_regression_model.py`, `run_ablation.py`) and `README.md`; (2) Final PDF Report (`Report.pdf`) with ablation tables, confusion matrices, and linguistic error analysis.

1. **Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011).** Lexicon-Based Methods for Sentiment Analysis. *Computational Linguistics*, 37(2), 267–307.
2. **Bhatia, P., Ji, Y., & Eisenstein, J. (2015).** Better Document-Level Sentiment Analysis from RST Discourse Parsing. *Proceedings of EMNLP 2015*, 2212–2218.
3. **Mann, W. C., & Thompson, S. A. (1988).** Rhetorical Structure Theory: Toward a Functional Theory of Text Organization. *Text*, 8(3), 243–281.
4. **Jakob, N., & Gurevych, I. (2010).** Using Anaphora Resolution to Improve Opinion Target Identification in Movie Reviews. *Proceedings of ACL 2010 Short Papers*, 263–268.
5. **Pang, B., & Lee, L. (2004).** A Sentimental Education: Sentiment Analysis Using Subjectivity Summarization Based on Minimum Cuts. *Proceedings of ACL 2004*, 271–278.
