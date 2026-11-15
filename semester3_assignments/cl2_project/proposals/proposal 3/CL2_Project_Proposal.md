# Linguistically Guided Extractive Medical Summarization: From RST, Syntactic Parsing, and Semantic Representations to Feature-Driven Logistic Regression

**Yashaswi Priya** (2025114007) & **Baani Solanki** (2025114016)  
*Computational Linguistics 2 — Course Project Proposal (IIIT Hyderabad)*

---

## 1. Goal of the Project & Research Question

Biomedical research articles (*PLOS*, *eLife*) are long and syntactically complex. While surface statistical baselines (`TF-IDF`, `TextRank`) extract sentences with frequent keywords, they ignore **discourse structure**, **syntactic clause nuclearity**, and **clinical meaning**, often selecting background boilerplate over core findings. Conversely, black-box pre-trained LLMs can hallucinate numeric dosages or invert clinical negations. Following the professor's feedback, we propose a **4-stage non-neural linguistic summarization framework**:
$$\text{Rule-Based Linguistic Summarizer} \;\longrightarrow\; \text{Rules-to-Features Mapping} \;\longrightarrow\; \text{Logistic Regression Model} \;\longrightarrow\; \text{Fine-Tuning via Best Linguistic Features}$$

**Research Question:** *How does converting linguistic summarization rules—spanning **Rhetorical Structure Theory (RST)**, **Syntactic Parsing & Anaphora**, and **Semantic Representations** alongside **TF-IDF** and **TextRank**—into features for a supervised **Logistic Regression** (and **Naive Bayes**) model affect factual reliability, clinical information retention (Symptoms-to-Disease classification), and `ROUGE` quality in medical summarization?*

---

## 2. Scope & 4-Stage Methodology (Strictly Non-Neural)

1. **Stage 1 — Rule-Based Linguistic Summarization (`M0` Baselines $\to$ `M1` Linguistic Rules):**
   - **Statistical & Graph Baselines (`M0` — Yashaswi):** Implement sentence-level **TF-IDF** salience and **TextRank** graph centrality.
   - **Rhetorical Structure Theory (`RST` — Baani):** Segment sentences into **Elementary Discourse Units (EDUs)** and classify explicit biomedical connectives into *Conclusion/Result* (*therefore, consequently, findings show*), *Contrast* (*however, in contrast*), *Cause* (*because, due to*), and *Concession* (*although, despite*) to upweight **Nucleus** claims ($w_N > 1$) and downweight **Satellite** background ($w_S < 1$).
   - **Syntactic Parser & Anaphora Resolution (`use a parser` — Baani):** Use NLTK POS tagging and a Context-Free Grammar (`RegexpParser`) chunker to reward complete main-clause `[Subject-NP + Finite-VP + Object-NP]` structures, prune parenthetical citations, and apply **Hobbs'/Binding-Theory Anaphora Resolution** to resolve or penalize dangling initial pronouns (*it, they, this treatment*).
   - **Meaning / Semantic Representation (`M1` — Yashaswi):** Extract structured **Predicate–Argument Semantic Triples** (`<Intervention/Agent, Clinical-Predicate, Symptom/Disease>`), compute **Symptom/Disease/Treatment concept density** (WordNet + medical lexicon), and track **syntactic negation scope** (*not, no evidence of*) and **numeric clinical evidence**.
2. **Stage 2 & 3 — Rules-to-Features Conversion & Supervised Logistic Regression (`M2`):**
   - Convert all 15 statistical, RST, syntactic-parser, and semantic rules into a feature vector $\mathbf{x}_i \in \mathbb{R}^{15}$ per sentence $s_i$, paired with **Oracle ROUGE Extractive Labels** $y_i \in \{0, 1\}$. Train custom **L2-Regularized Logistic Regression** (Baani) and **Naive Bayes** (Kupiec et al., 1995; Yashaswi) sentence classifiers $P(y_i = 1 \mid \mathbf{x}_i) = \sigma(\mathbf{w}^\top \mathbf{x}_i + b)$.
3. **Stage 4 — Feature-Guided Fine-Tuning (`M3`):**
   - Inspect learned Logistic Regression feature weights $|w_j|$, run systematic ablation across the linguistic feature families, and **fine-tune the model using the best-performing linguistic features** with an RST/anaphora coherence post-processor.

---

## 3. Datasets, Tools & 3-Tier Objective Evaluation

- **Datasets:** (1) **BioLaySumm2025-PLOS** & **BioLaySumm2025-eLife** (`https://huggingface.co/datasets/BioLaySumm/BioLaySumm2025-PLOS` & `eLife` — stratified 1,000-article train/dev/test benchmark); (2) **Symptom-to-Disease Clinical Dataset** for medical concept mapping and extrinsic diagnostic evaluation.
- **Tools Used:** Python 3, `nltk` (POS tagger, `RegexpParser` CFG parser, WordNet), `networkx`/`numpy` for `TextRank`, and custom from-scratch **Logistic Regression** & **Naive Bayes** implementations (`scikit-learn`/`matplotlib` for verification and plots).
- **3-Tier Objective Evaluation (No Human Annotation Required):**
  1. **Intrinsic Overlap:** `ROUGE-1`, `ROUGE-2`, and `ROUGE-L`.
  2. **Python Rule-Based Factual Checker:** Medical keyword & semantic-triple coverage, negation polarity preservation, and **regex matching for numeric values** (dosages, percentages, sample sizes, $p$-values).
  3. **Extrinsic Clinical Utility (`Symptoms-to-Disease Classification`):** Evaluate a non-neural **Naive Bayes / Logistic Regression Symptoms-to-Disease Classifier** on the generated summaries to test how well diagnostic symptom–disease links are preserved.

---

## 4. Expected Challenges, Division of Work & Key References

- **Challenges & Mitigations:** (1) *Generating sentence labels from gold summaries:* Use standard **Greedy Oracle ROUGE Labeling** ($y_i \in \{0,1\}$); (2) *Dangling pronouns in extracted sentences:* Substitute antecedent NPs via **Anaphora Resolution**; (3) *Feature collinearity:* Apply $L_2$ regularization and Stage 4 feature selection.
- **Equal 50/50 Division of Work:** **Yashaswi (`2025114007`)** builds `TF-IDF`/`TextRank`, Semantic Representation triples & negation, Naive Bayes, `ROUGE` & Numeric Regex Checker, and the Extrinsic Symptoms-to-Disease Classifier. **Baani (`2025114016`)** builds the RST Discourse Parser, CFG Syntactic Parser & Anaphora module, Rules-to-Features L2 Logistic Regression, and Stage 4 Feature Selection & Fine-Tuning.

1. **Marcu, D. (2000).** *The Theory and Practice of Discourse Parsing and Summarization.* MIT Press.
2. **Kupiec, J., Pedersen, J., & Chen, F. (1995).** A Trainable Document Summarizer. *Proceedings of ACM SIGIR 1995*, 68–73.
3. **Mihalcea, R., & Tarau, P. (2004).** TextRank: Bringing Order into Texts. *Proceedings of EMNLP 2004*, 404–411.
4. **Goldsack, T., et al. (2023/2025).** BioLaySumm: Lay Summarisation of Biomedical Research Articles. *ACL BioNLP Workshop* (`PMC10449915` & `PMC13142433`).
