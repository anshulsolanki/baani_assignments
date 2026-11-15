# Disambiguating Meaning Across Sentences: Hybrid Knowledge-Based and Supervised Word Sense Disambiguation Using WordNet Selectional Preferences, Anaphora Resolution, and Discourse Structure

**Yashaswi Priya** (2025114007) & **Baani Solanki** (2025114016)  
*Computational Linguistics 2 — Course Project Proposal (IIIT Hyderabad)*

---

## 1. Goal of the Project & Research Question

Word Sense Disambiguation (WSD)—identifying which sense of a polysemous word is activated in context—is a core problem in computational semantics (Topics **P1, P2, P9, P10**). However, standard non-neural WSD methods suffer from three linguistic bottlenecks when used in isolation:

1. **The Dictionary Sparsity Bottleneck in Classical Lesk:** Simplified Lesk relies on exact surface word overlap between a dictionary gloss and the local sentence. Because glosses are short, exact overlap often fails without **WordNet taxonomic expansion** (hypernyms, hyponyms, meronyms) and **Verb–Argument Selectional Preferences** (e.g., *drink* selects for a `[+LIQUID]` object; *deposit* selects for a `[+FINANCIAL]` object).
2. **Cross-Sentence Pronominal Anaphora Hiding Context Clues:** Standard WSD restricts context to the target sentence. Yet in multi-sentence discourse, the decisive semantic clue frequently modifies an **anaphoric pronoun** (`it, they, its`) in the next sentence (e.g., *"The customer walked toward the **bank** at dusk. **It** had already locked its vault"* vs. *"**It** was muddy and eroding into the river"*). Without **Anaphora Resolution**, sentence-bound WSD completely misses the predicate attached to *"It"*.
3. **Discourse Coherence & Rhetorical Relations (RST):** Naive multi-sentence windows pull in noisy words from unrelated clauses. Under **Rhetorical Structure Theory (RST)**, clauses linked via **Cause/Explanation** (*because, since*), **Elaboration**, or **Contrast** (*although, whereas*) directly constrain the target word's sense, while **Yarowsky's (1995) "One Sense Per Discourse"** principle enforces sense consistency across coreferent mentions.

**Research Question:** *To what extent does integrating (1) Extended WordNet Taxonomic Lesk and Verb–Argument Selectional Preferences, (2) Pronominal Anaphora Context Projection, and (3) RST Discourse Clause Weighting & One-Sense-Per-Discourse improve both knowledge-based WSD and supervised statistical WSD (Naive Bayes vs. Logistic Regression) across multi-sentence texts?*

---

## 2. Scope of the Project & Methodology (Strictly Non-Neural)

- **In-Scope:** We implement a modular, 100% non-neural WSD pipeline from scratch in Python and evaluate six progressive configurations (`B0`, `K1`–`K3`, `S1`–`S3`) in a controlled ablation study:
  1. **Knowledge-Based Lexical & Compositional Semantics (`K1` & `K2` — Yashaswi):** Implement **Simplified Lesk (`K1`)** and **Extended Taxonomic Lesk (`K2`)** by expanding candidate WordNet synsets with 1-hop hypernym, hyponym, meronym, and troponym glosses weighted by **Inverse Gloss Frequency (IGF)** and $n^2$ phrasal overlap, combined with **Wu–Palmer / Information Content Verb–Argument Selectional Preference** scores.
  2. **Anaphora Context Projection & RST Discourse Weighting (`K3` — Baani):** Apply **Binding Theory** intra-sentential filters and **Hobbs'/feature-based anaphora resolution** over a 2-sentence window to resolve pronouns (`it, they, its, them`). When a pronoun resolves to the target ambiguous NP, project its governing verb and modifiers into the target word's context. Segment clauses into **Elementary Discourse Units (EDUs)** via explicit connectives to weight *Cause*, *Elaboration*, and *Contrast* clauses and enforce **One-Sense-Per-Discourse**.
  3. **Supervised Statistical WSD Classifiers (`S1`–`S3`):** Implement multiclass **Multinomial Naive Bayes** (add-$k$ smoothing, Yashaswi) and **L2-Regularized Multinomial Logistic Regression / MaxEnt** (Baani) combining collocational n-grams ($w_{-2..+2}$, POS $t_{-2..+2}$), syntactic relations, knowledge scores (`K2`), and discourse-anaphoric features (`K3`).
- **Out-of-Scope:** Neural networks, pre-trained embeddings/LLMs, unconstrained all-words WSD, and human evaluation.

---

## 3. Datasets, Tools & Objective Evaluation Metrics

- **Datasets & Lexical Resources:** (1) **Senseval-2 English Lexical Sample (`nltk.corpus.senseval`)** — 4,328 gold-labeled multi-sentence instances across `interest.pos` (N), `line.pos` (N), `serve.pos` (V), and `hard.pos` (Adj) (80/10/10 split); (2) **SemCor Multi-Sentence Discourse Benchmark (`nltk.corpus.semcor`)** — ~1,500 gold WordNet-annotated instances across 15 polysemous words plus a **Hard Anaphoric & Discourse Subset**; (3) **WordNet 3.0 & WordNet IC (`nltk.corpus.wordnet`)**.
- **Tools Used:** Python 3 standard library, `nltk` (POS tagger, `RegexpParser` CFG chunker, WordNet interface), custom Naive Bayes and Logistic Regression implementations, and `scikit-learn`/`matplotlib` for verification and confusion matrix plots.
- **Evaluation Metrics:** Fine-grained Sense Accuracy, Macro-Precision, Macro-Recall, Macro-F1 (to account for Zipfian sense skew), Per-Word Confusion Matrices, and Ablation Analysis (`B0`, `K1`–`K3`, `S1`–`S3`).

---

## 4. Expected Challenges & Mitigation Plan

- **Zipfian sense skew (Most Frequent Sense dominance):** Evaluate with both **Macro-F1** and **Micro-F1**, tune smoothing/class weights, and integrate knowledge-based `K2/K3` scores that are independent of training sense frequency.
- **Gloss noise in Extended Lesk:** Restrict WordNet graph expansion to 1-hop taxonomic neighbors and weight overlaps by **Inverse Gloss Frequency (IGF)** and $n^2$ phrasal match length.
- **Cascading anaphora errors:** Enforce strict number/animacy agreement (`it/its` $\to$ singular inanimate NP) and only project anaphoric predicates when resolution confidence $\tau \ge 0.60$.

---

## 5. Exact Deliverables & Key Research Paper References

**Deliverables:** (1) GitHub repository with modular Python code (`wsd_corpus_loader.py`, `knowledge_wsd.py`, `anaphora_wsd_context.py`, `discourse_rst_wsd.py`, `naive_bayes_wsd.py`, `logistic_regression_wsd.py`, `run_ablation.py`) and `README.md` with balanced 50/50 commits; (2) Final PDF Report (`Report.pdf`) with ablation tables, Zipfian plots, confusion matrices, and linguistic error analysis.

1. **Banerjee, S., & Pedersen, T. (2002).** An Adapted Lesk Algorithm for Word Sense Disambiguation Using WordNet. *Proceedings of CICLing 2002*, 136–145.
2. **Yarowsky, D. (1995).** Unsupervised Word Sense Disambiguation Rivaling Supervised Methods. *Proceedings of ACL 1995*, 189–196.
3. **Resnik, P. (1997).** Selectional Preference and Sense Disambiguation. *Proceedings of ACL SIGLEX Workshop*, 52–57.
4. **Lee, Y. K., & Ng, H. T. (2002).** An Empirical Evaluation of Knowledge Sources and Learning Algorithms for Word Sense Disambiguation. *Proceedings of EMNLP 2002*, 41–48.
5. **Mann, W. C., & Thompson, S. A. (1988).** Rhetorical Structure Theory: Toward a Functional Theory of Text Organization. *Text*, 8(3), 243–281.
