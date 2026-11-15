# Why This Proposal Is Strong & Will Not Be Rejected

**Project Title:** *Beyond Bag-of-Words: Discourse- and Anaphora-Aware Sentiment Classification Using Rhetorical Structure Theory (RST) and Compositional Semantics*  
**Team:** Yashaswi Priya (`2025114007`) & Baani Solanki (`2025114016`)

---

## 1. It Directly Builds on Approved Topics in `project-titles.pdf` — Elevated for a 2-Person Team

On pages 2–4 of the instructors' handout (`project-titles.pdf`), Prof. Parameswari Krishnamurthy and Prof. Rajakrishnan Rajkumar explicitly listed the exact types of projects they want to see in Computational Linguistics 2:
- **P13:** *"Sentiment Analysis on Social Media Texts with Semantic Interpretation: Analyze sentiment while considering the semantic nuances and meanings behind expressions."*
- **P20:** *"Text Classification: Logistic Regression vs Naive Bayes... incorporating linguistically motivated features... Report precision, recall and accuracy figures along with a confusion matrix. Do a detailed linguistic analysis comparing the output of the logistic regression classifier with the naive bayes classifier."*
- **P21:** *"Sentiment Analysis with Naive Bayes and Lexicons... Incorporate features based on a standard polarity lexicon of your choice: ... 3. Opinion lexicon of Hu and Liu (2004), 4. MPQA Subjectivity Lexicon (Wilson et al., 2005)."*
- **P22:** *"Anaphora Resolution: Classifier vs Rule-Based."*

### Why This Matters:
- If a 2-student team only submitted basic **P20** or **P21** (running Naive Bayes with a lexicon), the instructors/TAs could say it is too simple for two people because it is just a minor extension of a single homework.
- By combining **P20 + P21** (Sentiment Analysis with Hu–Liu & MPQA Lexicons comparing Naive Bayes vs. Logistic Regression) with **Rhetorical Structure Theory (RST)** and **Anaphora Resolution (P22)**, the proposal sits in the exact sweet spot: **100% aligned with the instructors' own approved project list**, while being **substantive and original enough for a 2-person team**.

---

## 2. It Follows Prof. Jason Eisner's "Small-to-Medium Bone" Formula in `project-guidelines.pdf`

In `project-guidelines.pdf` (pages 2–3), the instructors included Prof. Jason Eisner's guide on what makes an ideal class research project:
1. *"A significant small bone to look for is a tweak that improves a well-known technique. (In many subfields, you will be expected to demonstrate objectively that your method is an improvement.)"*
2. *"Along the same lines, you might make a controlled comparison of two or more algorithms, evaluating them by some objective measure of efficiency or accuracy."*

Our proposal is designed around a **5-stage controlled ablation study (`M0` $\to$ `M1` $\to$ `M2` $\to$ `M3` $\to$ `M4`)** comparing two classical algorithms (**Naive Bayes vs. Logistic Regression**):
- **`M0`:** Surface Bag-of-Words baseline (Unigrams/Bigrams)
- **`M1`:** `M0` + Lexical Semantics (MPQA & Hu–Liu polarity lexicons)
- **`M2`:** `M1` + Compositional Semantics (syntactic negation scope, intensifiers/downtoners, irrealis modals)
- **`M3`:** `M2` + Pronominal Anaphora Resolution (entity salience tracking across sentences)
- **`M4`:** `M3` + RST Discourse Weighting (Nucleus vs. Satellite clauses)

This structure guarantees success: even if one linguistic module gives a +3.5% F1 boost and another gives a +0.8% F1 boost (or only helps on contrastive sentences), **every stage produces a clean, objective quantitative comparison and deep linguistic error analysis**.

---

## 3. Point-by-Point Comparison: Why Proposal 1 Was Rejected vs. How This Proposal Fixes It

| Why Proposal 1 (Medical Summarization) Was Rejected | How Our New Proposal Completely Solves It |
| :--- | :--- |
| **1. "Simply evaluated pre-existing models without adding any of our own input"** | Zero pre-trained models are used. Every module—Compositional Negation/Modal Shifter, Pronominal Anaphora Resolver, Connective-based RST Segmenter, Naive Bayes, and Logistic Regression—is **implemented from scratch by Yashaswi and Baani**. |
| **2. "Did not utilize our linguistic knowledge"** | Directly applies **every major linguistic pillar taught in CL2**:<br>• **Semantics:** Polarity lexicons, compositional negation scope, intensifiers, and presuppositional/irrealis modality.<br>• **Discourse:** Rhetorical Structure Theory (Nucleus vs. Satellite asymmetry in *Concession*, *Contrast*, *Cause*, *Condition*).<br>• **Pragmatics/Syntax:** Binding Theory Principles A & B + Anaphora Resolution. |
| **3. "Used Neural Networks / Pre-trained LLMs"** | **Strictly 0% neural networks.** Uses only classical statistical NLP (Naive Bayes & Logistic Regression) and rule-based linguistics (`nltk`). |
| **4. "Human evaluation would be too difficult to execute"** | **Zero human evaluation required.** The Cornell Movie Review dataset (`nltk.corpus.movie_reviews`) already has gold-standard Positive/Negative labels, so Precision, Recall, Macro-F1, Accuracy, and Confusion Matrices are 100% automatic and reproducible. |
| **5. "Building our own summarizer from scratch is too challenging"** | Binary sentiment classification (`Positive` vs. `Negative`) + rule-based clause weighting is **completely achievable in ~400–600 lines of clean Python** (especially since Baani already implemented custom Logistic Regression and Anaphora Resolution in Assignment 4). |

---

## 4. Unmistakable, Equal 50/50 Division of Work for Separate Grading

Because `project-guidelines.pdf` explicitly states:
> *"Group size: 2 members maximum (each member's contribution will be evaluated separately)"*

TAs frequently question proposals where both students seem to be doing the exact same thing or where one student's role is vague. Here, the 50/50 split is built directly into the architecture:
- **Yashaswi Priya (`2025114007`)** owns **Semantics + Generative Classifier**:
  - MPQA & Hu–Liu lexicon integration (`lexicon_semantics.py`)
  - Compositional Semantic Shifters: syntactic negation scope, intensifiers/downtoners, irrealis modals (`compositional_rules.py`)
  - Multinomial Naive Bayes from scratch & SO-CAL rule-based aggregation (`naive_bayes_model.py`)
- **Baani Solanki (`2025114016`)** owns **Discourse/Pragmatics + Discriminative Classifier**:
  - Rule-based RST Elementary Discourse Unit (EDU) segmentation & Nucleus/Satellite connective weighting (`rst_discourse.py`)
  - Pronominal Anaphora Resolution & topical entity salience (`anaphora_salience.py`)
  - L2-Regularized Logistic Regression from scratch & feature weight inspection (`logistic_regression_model.py`)

---

## 5. How We Preempted the Only Tough Question a TA Could Ask

The only realistic concern a TA or professor could raise when seeing "Rhetorical Structure Theory (RST)" in a project title is:
> *"Full-document RST discourse tree parsing is hard without a pre-trained neural parser—how will you do RST using only rules?"*

We explicitly addressed and solved this in **Section 2 (Scope)** and **Section 4 (Expected Challenges & Mitigation)** of the proposal:
1. We explicitly state that **full-document unconstrained RST tree construction is Out-of-Scope**.
2. Instead, we restrict RST analysis to **intra-sentential and adjacent-sentence Elementary Discourse Units (EDUs) anchored by explicit lexical discourse connectives** (~45 connectives such as *although, even though, despite, however, but, because, therefore, if, unless*) using NLTK CFG clause boundaries (`S`, `SBAR`).
3. When an explicit connective is present, **Nucleus vs. Satellite directionality follows deterministic linguistic rules** (e.g., `[Although Satellite], [Nucleus]`; `[Satellite], however [Nucleus]`).
4. We also address **connective polysemy** (e.g., temporal *"while walking"* vs. concessive *"while the acting was good"*) using POS/CFG subcategorization rules (`while + VBG` vs. `while + finite S`).

This shows the instructors that the team understands **both** the formal linguistic theory of RST **and** how to scope it practically so it can be completed cleanly and rigorously before the deadline.
