# Computational Linguistics 2 — Course Project Proposal (Proposal 2)

**Project Title:**  
**Disambiguating Meaning Across Sentences: A Hybrid Knowledge-Based and Supervised Word Sense Disambiguation System Using WordNet Selectional Preferences, Anaphora Resolution, and Discourse Structure**

**Team Members:**
- **Yashaswi Priya** (Roll No: `2025114007`)
- **Baani Solanki** (Roll No: `2025114016`)

**Course:** Computational Linguistics 2 (Monsoon / Semester 3)  
**Instructors:** Prof. Parameswari Krishnamurthy & Prof. Rajakrishnan Rajkumar

---

## 1. Goal of the Project & Research Questions

### 1.1 Primary Goal
**Word Sense Disambiguation (WSD)**—computationally determining which sense (meaning) of a polysemous word is activated in a given context—is a foundational problem in computational semantics (Topics **P1, P2, P9, and P10** in the course project handout). However, classical WSD systems suffer from three fundamental linguistic limitations when applied separately:

1. **The Dictionary Sparsity Bottleneck in Knowledge-Based WSD (Lesk):**  
   The classical **Lesk algorithm** (Lesk, 1986) disambiguates a target word by counting exact word overlaps between its dictionary definition (gloss) and the local context. Because dictionary glosses are brief and use formal phrasing, exact surface overlap frequently fails even when the context is semantically related (e.g., *"deposit money"* vs. *"financial institution"* for `bank.n.02`), and ignores **compositional verb–argument selectional restrictions** (e.g., the verb *drink* selects for a `[+LIQUID]` direct object, while *cash* selects for a `[+FINANCIAL_DOCUMENT]` object).
2. **Cross-Sentence Pronominal Anaphora Hiding Disambiguating Clues:**  
   Standard WSD systems restrict their context window to the current sentence or a narrow $\pm k$-word window. In real multi-sentence discourse, the decisive semantic predicate often appears in an adjacent sentence attached to an **anaphoric pronoun** (`it, they, its, them`):
   - *Example A:* *"The hiker walked toward the **bank** at dusk. **It** was steep, muddy, and eroding into the river."* (`bank` = sloping land)
   - *Example B:* *"The customer walked toward the **bank** at dusk. **It** had already locked its vault for the holiday."* (`bank` = financial institution)  
   In Sentence 1 (*"walked toward the bank at dusk"*), the local context is completely ambiguous. Only by resolving the pronoun **"It"** in Sentence 2 to **"bank"** via **Anaphora Resolution** can a system attach the disambiguating predicates (*"eroding into the river"* vs. *"locked its vault"*) to the target word.
3. **Discourse Coherence & Rhetorical Asymmetry (RST):**  
   Naive multi-sentence context expansion pulls in noisy, unrelated words from background clauses. Under **Rhetorical Structure Theory (RST)**, clauses linked to the target word's clause via **Elaboration**, **Cause/Explanation** (*because, since, therefore*), or **Contrast** (*although, whereas, however*) directly constrain the target word's sense, while **Yarowsky's (1995) "One Sense Per Discourse" principle** establishes that multiple mentions of an ambiguous word within a coherent discourse segment share the same sense.

The goal of this project is to **design, implement from scratch, and systematically compare a non-neural hybrid WSD framework** that bridges **Knowledge-Based Lexical Semantics** (Simplified Lesk, Extended Taxonomic Lesk, and WordNet Verb–Argument Selectional Preferences), **Discourse & Anaphora Resolution** (Pronominal Context Projection, RST Clause Weighting, and One-Sense-Per-Discourse), and **Supervised Statistical Classifiers** (**Naive Bayes** and **L2-Regularized Multinomial Logistic Regression**).

### 1.2 Research Questions
1. **RQ1 (Knowledge-Based Lexical & Compositional Semantics — P1, P9, P10):** How much does expanding Simplified Lesk with **WordNet taxonomic relations** (hypernyms, hyponyms, meronyms, troponyms weighted by Inverse Gloss Frequency) and **Verb–Argument Selectional Preference similarity** (Wu–Palmer and Information Content similarity) improve unsupervised WSD accuracy over baseline Lesk and the Zipfian Most Frequent Sense (MFS)?
2. **RQ2 (Anaphora Resolution & Discourse Structure in WSD):** Does projecting predicates attached to **coreferent pronouns** (resolved via Binding Theory filters and Hobbs'/feature-based anaphora resolution) and weighting **RST-linked clauses** (*Elaboration*, *Cause*, *Contrast*) + **One-Sense-Per-Discourse constraints** significantly improve disambiguation on multi-sentence contexts (`SemCor` and `Senseval-2`)?
3. **RQ3 (Generative vs. Discriminative Supervised WSD — P2):** When combining collocational n-grams, syntactic relations, knowledge-based Lesk/WordNet scores, and discourse-anaphoric features into a unified feature representation, how does a discriminative **Multinomial Logistic Regression (MaxEnt)** classifier compare against a generative **Multinomial Naive Bayes** classifier (with smoothing)?

---

## 2. How This Proposal Addresses Previous Feedback

| Previous Rejection Reason (Medical Summarization) | How Our New Project Completely Resolves It |
| :--- | :--- |
| **1. Evaluated pre-existing models without original input** | Zero pre-trained models or black-box APIs are used. We implement **Simplified Lesk**, **Extended Taxonomic Lesk**, **Selectional Preference Scorer**, **Anaphora Context Projector**, **RST Clause Weighter**, **Naive Bayes**, and **Multinomial Logistic Regression** from scratch in Python. |
| **2. Did not utilize linguistic knowledge** | Directly integrates **every core module of CL2**: **Lexical Semantics** (WordNet synsets, hypernym/meronym hierarchies, selectional restrictions), **Discourse & Pragmatics** (Binding Theory, Anaphora Resolution, RST discourse relations, One-Sense-Per-Discourse), and **Statistical NLP** (Zipfian sense priors, N-gram collocations, smoothing, Naive Bayes, Logistic Regression). |
| **3. Relied on Neural Networks / Pre-trained LLMs** | **Strictly 0% neural networks, word embeddings, or LLMs.** Uses only symbolic lexical resources (WordNet), CFG/POS parsing, and classical statistical classifiers. |
| **4. Human evaluation was impractical / building a summarizer from scratch was too hard** | Evaluated **100% automatically and objectively** against gold-standard human-annotated WordNet sense labels in **Senseval-2** (`nltk.corpus.senseval`) and **SemCor** (`nltk.corpus.semcor`) using **Accuracy, Macro/Micro Precision, Recall, F1, Confusion Matrices**, and a controlled **Ablation Study**. |

---

## 3. Scope of the Project

To ensure the project is both **linguistically rigorous** and **completely achievable within the semester timeline**, we clearly define our boundaries:

### 3.1 In-Scope
1. **Zipfian Sense Distribution Analysis & Baselines:**
   - Quantifying how word sense frequencies follow **Zipf's Law** across polysemous nouns, verbs, and adjectives in `SemCor` and `Senseval-2`, and implementing Random Sense and **Most Frequent Sense (MFS)** baselines.
2. **Knowledge-Based Lexical & Compositional Semantics (`P1 + P9 + P10`):**
   - **Simplified Lesk:** Lemmatized, stopword-filtered overlap between target synset gloss/examples and local sentence context.
   - **Extended Taxonomic Lesk (Banerjee & Pedersen, 2002):** Expanding each candidate synset's signature with the glosses of its WordNet **hypernyms, hyponyms, meronyms, holonyms, and troponyms**, weighted by **Inverse Gloss Frequency (IGF)** so rare, domain-specific gloss words carry higher weight than generic definitions.
   - **Verb–Argument Selectional Preference Module:** Extracting syntactic `[Verb, Direct-Object]` and `[Subject, Verb]` pairs using NLTK CFG chunking and scoring candidate senses via **Wu–Palmer (`wup_similarity`)** and **Resnik/Lin Information Content similarity** in WordNet.
3. **Discourse & Anaphora Context Enrichment:**
   - **Anaphora-Driven Context Projection:** Resolving third-person pronouns (`it, they, its, them, he, she`) in adjacent sentences ($s_{t}, s_{t+1}$) using **Binding Theory Principles A & B** and **Hobbs' CFG tree search / feature-based anaphora resolution**. Whenever a pronoun resolves to the target ambiguous NP, the pronoun's governing verb and modifying adjectives are injected into the target word's disambiguation context.
   - **RST Discourse Clause Weighting & One-Sense-Per-Discourse:** Segmenting multi-clause contexts into **Elementary Discourse Units (EDUs)** via explicit discourse connectives (*because, since, therefore, although, however, for instance*) to upweight **Nucleus** and **Causal/Elaboration Satellite** tokens while enforcing **Yarowsky's (1995) One-Sense-Per-Discourse** constraint across repeated mentions in a passage.
4. **Supervised Statistical WSD Classifiers (`P2`):**
   - Implementing **Multinomial Naive Bayes** (with Laplace / add-$k$ smoothing) and **Multinomial L2-Regularized Logistic Regression (MaxEnt)** from scratch over linguistic feature vectors (collocational n-grams $w_{-2..+2}$, POS tags $t_{-2..+2}$, syntactic head/governor, Extended Lesk scores, and discourse-anaphoric context features).

### 3.2 Out-of-Scope
- Neural networks, static/contextual word embeddings (`Word2Vec`, `GloVe`, `BERT`), or LLMs.
- Unconstrained all-words WSD over millions of tokens (we focus on the standard **Senseval-2 English Lexical Sample** benchmark + a curated **multi-sentence SemCor discourse benchmark** of 15 highly polysemous nouns and verbs).
- Full end-to-end discourse tree parsing without lexical connectives or human evaluation.

---

## 4. Datasets & Objective Evaluation Metrics

### 4.1 Datasets & Lexical Resources (Built into NLTK)
1. **Senseval-2 English Lexical Sample Corpus (`nltk.corpus.senseval`):**
   - **Size:** **4,328 gold-annotated multi-sentence instances** across four canonical highly polysemous words covering Noun, Verb, and Adjective parts of speech:
     - **`interest.pos`** (Noun — 2,368 instances across 6 senses: *readiness to give attention*, *advantage/benefit*, *financial fixed charge*, *financial share/stake*, *pastime*, etc.)
     - **`line.pos`** (Noun — 4,146 total/subset instances across 6 senses: *product line*, *telephone connection*, *written text/verse*, *queue of people*, *cord/rope*, *division/boundary*)
     - **`serve.pos`** (Verb — 1,850 instances across 4 senses: *supply with food/goods*, *hold an office/duty*, *function as*, *provide a service*)
     - **`hard.pos`** (Adjective — 4,333 instances across 3 senses: *not easy/difficult*, *dispassionate/severe*, *resisting weight/solid*)
   - **Why it is ideal:** Each instance includes a multi-sentence context paragraph, POS tags, and a gold-standard sense label, enabling rigorous supervised 80/10/10 train/dev/test evaluation for **Naive Bayes vs. Logistic Regression**.
2. **SemCor Discourse WSD Benchmark (`nltk.corpus.semcor`):**
   - **Size:** Multi-sentence paragraphs from the Brown Corpus where **every content word is human-annotated with its exact WordNet 3.0 synset**.
   - We extract a benchmark of ~1,500 multi-sentence occurrences across 15 classic polysemous words (e.g., *bank, plant, bass, crane, palm,organ, cell, issue, state, play, run, break*) plus a **Hard Anaphoric & Discourse Subset** where the target sentence has minimal local cues and the disambiguating predicate resides in an adjacent clause/sentence linked via a pronoun (`it, they`) or discourse connective (*because, although, since*).
3. **Lexical Knowledge Base:**
   - **WordNet 3.0 (`nltk.corpus.wordnet`)** and **WordNet Information Content (`nltk.corpus.wordnet_ic`)** for synset glosses, hypernym/hyponym/meronym graphs, and taxonomic similarity metrics.

### 4.2 Objective Evaluation Metrics
- **Fine-Grained Sense Accuracy, Macro-Averaged Precision, Recall, and Macro-F1** (essential because Zipfian sense distributions are imbalanced, so Macro-F1 penalizes models that simply predict the Most Frequent Sense).
- **Per-Word and Per-POS Confusion Matrices** (visualizing which closely related senses—such as *financial charge* vs. *financial stake* for `interest`—are confused).
- **Controlled 6-Stage Ablation Study (`K1`–`K3` Knowledge-Based & `S1`–`S3` Supervised):**
  - `B0`: Random Sense & Most Frequent Sense (MFS) Zipfian Baseline
  - `K1`: Classical / Simplified Lesk (Local Sentence Gloss Overlap)
  - `K2`: Extended Taxonomic Lesk (Hypernym/Hyponym/Meronym Expansion + IGF Weighting + Selectional Preferences)
  - `K3`: Discourse- & Anaphora-Aware Extended Lesk (`K2` + Pronominal Context Projection + RST Clause Weighting + One-Sense-Per-Discourse)
  - `S1`: Supervised Naive Bayes vs. Logistic Regression (Surface Bag-of-Words & Local Collocation N-grams $w_{-2..+2}$)
  - `S2`: Supervised Naive Bayes vs. Logistic Regression + Syntactic Relations & Knowledge-Based (`K2`) Scores
  - `S3`: **Full Hybrid System** (`S2` + Anaphora-Projected Context Features + RST Discourse Weighting)

---

## 5. Tools & Technologies Used

- **Programming Language:** Python 3 (Standard Library: `math`, `re`, `collections`, `csv`, `json`).
- **Linguistic & Lexical Processing:** `nltk` (`nltk.corpus.wordnet`, `nltk.corpus.wordnet_ic`, `nltk.corpus.senseval`, `nltk.corpus.semcor`, Penn Treebank POS tagger, `RegexpParser` CFG phrase chunker, `WordNetLemmatizer`).
- **Statistical Classifiers:** Custom from-scratch Python implementations of **Multinomial Naive Bayes** (with add-$k$ smoothing) and **Multinomial L2-Regularized Logistic Regression** (Softmax + Stochastic/Mini-Batch Gradient Descent), verified against `scikit-learn` with `matplotlib` for confusion matrices and Zipfian sense distribution plots.
- **Version Control:** Git & GitHub (strictly adhering to the course policy of regular, meaningful multi-day commits).

---

## 6. Step-by-Step Implementation Plan

```
Multi-Sentence Passage + Target Ambiguous Word (w)
                      │
                      ▼
        [Step 1: Linguistic Preprocessing]
   Sentence Splitting → POS Tagging → Lemmatization → CFG NP & VP Chunking
                      │
       ┌──────────────┴────────────────────────────────┐
       ▼                                               ▼
[Step 2A: Lexical & Compositional Semantics]   [Step 2B: Discourse & Anaphora Enrichment]
         (Yashaswi)                                      (Baani)
 • WordNet Synset & Gloss Extraction            • Pronominal Anaphora Resolution (Binding + Hobbs)
 • Extended Taxonomic Graph (Hyper/Meronyms)    • Pronoun Predicate Projection onto Target Word
 • Inverse Gloss Frequency (IGF) Weighting      • EDU Segmentation & RST Connective Weighting
 • Verb-Argument Selectional Similarity         • One-Sense-Per-Discourse Propagation
       │                                               │
       └──────────────┬────────────────────────────────┘
                      ▼
     [Step 3: Unified Hybrid Feature & Score Representation]
                      │
        ┌─────────────┼──────────────────────┐
        ▼             ▼                      ▼
  [Knowledge WSD]  [Multinomial Naive Bayes]  [Multinomial Logistic Regression]
   (K1 -> K3)          (Yashaswi)                    (Baani)
        │             │                      │
        └─────────────┼──────────────────────┘
                      ▼
  [Step 4: Ablation Study (B0-K3, S1-S3), Confusion Matrices & Error Analysis]
```

1. **Phase 1 — Corpus Preprocessing & Zipfian Sense Analysis:** Load `Senseval-2` (`interest, line, hard, serve`) and `SemCor` multi-sentence passages; build stratified 80/10/10 splits; plot sense frequency rank vs. frequency on log-log axes to verify Zipf's Law of Meaning; implement `B0` (Random & MFS baselines).
2. **Phase 2 — Knowledge-Based Lexical & Selectional WSD (`K1` & `K2`):** Implement Simplified Lesk (`K1`), Extended Taxonomic Lesk with hypernym/hyponym/meronym gloss expansion and Inverse Gloss Frequency weighting, and Verb–Argument Selectional Preference scoring (`K2`).
3. **Phase 3 — Anaphora Context Projection & RST Discourse Module (`K3`):**
   - Run CFG NP extraction, Binding Theory filters, and Hobbs' algorithm over a 2-sentence window around the target word to resolve pronouns (`it, they, its, them`). When a pronoun co-refers with the target word, project the pronoun's governing verb and adjectives into the target word's context with weight $\gamma_{\text{anaph}}$.
   - Segment sentences into Elementary Discourse Units (EDUs) using explicit connectives (*because, since, although, whereas, therefore*) to weight rhetorically linked clauses and apply Yarowsky's One-Sense-Per-Discourse constraint.
4. **Phase 4 — Supervised Naive Bayes vs. Logistic Regression (`S1`–`S3`):** Extract collocational n-grams ($w_{-2..+2}$, POS $t_{-2..+2}$), syntactic dependencies, knowledge scores (`K2`), and discourse-anaphoric features (`K3`). Train custom Multinomial Naive Bayes and Multinomial L2 Logistic Regression across `S1`, `S2`, and `S3`.
5. **Phase 5 — Quantitative Ablation & Linguistic Error Analysis:** Evaluate all models on full test sets and the Hard Anaphoric-Discourse subset, generate confusion matrices, inspect top learned feature weights per sense, and compile the final PDF report.

---

## 7. Expected Challenges & Mitigation Plan

| Expected Challenge | Impact | Concrete Mitigation Strategy |
| :--- | :--- | :--- |
| **1. Extreme Zipfian Skew in Word Senses** | The Most Frequent Sense (MFS) often accounts for 50–70% of occurrences, causing unregularized classifiers to ignore rare senses. | **Mitigation:** Report both **Micro-F1 (Accuracy)** and **Macro-F1**, tune add-$k$ smoothing in Naive Bayes and class-balanced/L2 weights in Logistic Regression, and combine supervised priors with knowledge-based Extended Lesk scores (`S2`/`S3`) which do not depend on training sense frequency. |
| **2. Gloss Explosion & Noise in Extended Lesk** | Expanding too many levels of WordNet hypernyms produces generic top-level definitions (*"a physical entity"*) that match everything. | **Mitigation:** Limit taxonomic expansion to **1-hop hypernyms, hyponyms, meronyms, and troponyms**, apply strict POS/stopword filtering, and weight overlapping terms by **Inverse Gloss Frequency ($\text{IGF}(t) = \log \frac{N}{df_{\text{gloss}}(t)}$)** and **Banerjee & Pedersen's $n^2$ phrasal overlap bonus**. |
| **3. Noisy Pronoun Resolution in Multi-Noun Sentences** | If a pronoun (`it`) is linked to the wrong antecedent NP, projecting its verb could introduce misleading context words. | **Mitigation:** Enforce strict **number/animacy agreement** (e.g., neuter `it/its` only links to singular inanimate NPs; `he/she` to animate NPs) and only project anaphoric predicates when our Assignment 4 classifier/Hobbs' confidence exceeds a high threshold ($\tau \ge 0.60$). |
| **4. Sense Granularity in WordNet** | WordNet sometimes splits very fine-grained nuances into separate synsets. | **Mitigation:** Use the standard `Senseval-2` sense groupings alongside `SemCor` WordNet synsets, and analyze fine-grained sense confusions via per-word **Confusion Matrices**. |

---

## 8. Rough Timeline & GitHub Commit Schedule

*(Structured to ensure consistent, multi-day commits from both team members well ahead of the deadline.)*

| Milestone / Dates | Tasks & GitHub Commit Checkpoints | Owner(s) |
| :--- | :--- | :--- |
| **Milestone 1** (Oct 23 – Oct 24) | Finalize & submit project proposal; initialize repository directory structure and `README.md`. | Both |
| **Milestone 2** (Oct 25 – Oct 29) | **Commit 1 & 2:** Implement `Senseval-2` and `SemCor` data loaders, POS/CFG preprocessing pipeline, Zipfian sense distribution analysis, and `B0` (Random & MFS) baselines. | Yashaswi & Baani |
| **Milestone 3** (Oct 30 – Nov 4) | **Commit 3 & 4:** Implement Simplified Lesk (`K1`), Extended Taxonomic Lesk with IGF weighting, Verb–Argument Selectional Preferences (`K2`), and custom Multinomial Naive Bayes WSD classifier. | Yashaswi |
| **Milestone 4** (Oct 30 – Nov 4) | **Commit 5 & 6:** Implement Anaphora Context Projection module, RST EDU Connective Weighting, One-Sense-Per-Discourse (`K3`), and custom Multinomial L2 Logistic Regression WSD classifier. | Baani |
| **Milestone 5** (Nov 5 – Nov 9) | **Commit 7 & 8:** Integrate hybrid feature pipeline (`S1`–`S3`), run full 6-stage ablation study on `Senseval-2` and `SemCor` (including the Hard Anaphoric Subset), and generate confusion matrices. | Both |
| **Milestone 6** (Nov 10 – Final Deadline) | **Commit 9 & 10:** Perform qualitative linguistic error analysis on learned feature weights and sense confusions, finalize `README.md`, and compile `Report.pdf`. | Both |

---

## 9. Clear and Equal Division of Work (50% / 50%)

Because each student's contribution is graded separately and verified via GitHub commit history, the architecture is cleanly divided into two equal, independent tracks plus joint evaluation:

### **Yashaswi Priya (`2025114007`) — Knowledge-Based Lexical Semantics (Lesk, WordNet Taxonomy, Selectional Preferences) + Naive Bayes WSD**
1. **Corpus Loader & Zipfian Sense Analysis (`wsd_corpus_loader.py`):**
   - Parsing `Senseval-2` (`interest.pos`, `line.pos`, `hard.pos`, `serve.pos`) and `SemCor` XML/tagged paragraphs; verifying Zipf's Law on sense distributions and implementing Random and MFS (`B0`) baselines.
2. **Knowledge-Based & Selectional WSD Engine (`knowledge_wsd.py`):**
   - Implementing **Simplified Lesk (`K1`)** and **Extended Taxonomic Lesk (`K2`)** using WordNet hypernyms, hyponyms, meronyms, and troponyms with $n^2$ phrasal overlap and Inverse Gloss Frequency (IGF) weighting.
   - Implementing **Verb–Argument Selectional Preference scoring** using WordNet Wu–Palmer and Information Content similarity.
3. **Multinomial Naive Bayes WSD Classifier (`naive_bayes_wsd.py`):**
   - Implementing multiclass Multinomial Naive Bayes from scratch with add-$k$ smoothing over collocational n-grams, POS windows, and hybrid knowledge features.
4. **Lexical Error Analysis & Visualization (`evaluate_wsd.py`):**
   - Generating Zipfian sense distribution plots, per-word confusion matrices, and analyzing lexical/taxonomic failure cases.

### **Baani Solanki (`2025114016`) — Anaphora Context Projection, RST Discourse Structure + Logistic Regression WSD**
1. **Anaphora-Driven Context Projection (`anaphora_wsd_context.py`):**
   - Adapting CFG NP chunking, Binding Theory constraints (Principles A & B), and Hobbs'/feature-based anaphora resolution (`it, they, its, them`) to resolve pronouns across adjacent sentences and project their governing verbs and modifiers onto the target ambiguous word.
2. **RST Discourse Weighting & One-Sense-Per-Discourse (`discourse_rst_wsd.py`):**
   - Implementing rule-based Elementary Discourse Unit (EDU) clause segmentation, explicit connective weighting (*Cause*, *Elaboration*, *Contrast*), and Yarowsky's (1995) discourse-level sense propagation (`K3`).
3. **Multinomial L2 Logistic Regression WSD Classifier (`logistic_regression_wsd.py`):**
   - Implementing multiclass L2-regularized Logistic Regression (Softmax + SGD/mini-batch gradient descent) from scratch, hyperparameter tuning on the dev split, and extracting top learned feature weights per sense.
4. **Hard Anaphoric Subset & Discourse Error Analysis (`discourse_wsd_analysis.py`):**
   - Constructing the Hard Anaphoric & Discourse evaluation subset from `SemCor`/`Senseval-2` and conducting qualitative/quantitative comparison between sentence-local and discourse-aware WSD.

---

## 10. Exact Deliverables

1. **GitHub Repository (`semester3/cl2_project/`):**
   - Clean, modular, well-documented Python codebase (`wsd_corpus_loader.py`, `knowledge_wsd.py`, `anaphora_wsd_context.py`, `discourse_rst_wsd.py`, `naive_bayes_wsd.py`, `logistic_regression_wsd.py`, `evaluate_wsd.py`, `run_ablation.py`) with balanced, multi-day commits from both Yashaswi and Baani.
   - Comprehensive `README.md` with exact reproduction steps and output tables.
2. **Experimental Results & Plots:**
   - Complete quantitative ablation tables (`B0`, `K1`–`K3`, `S1`–`S3`) reporting Fine-Grained Accuracy, Macro-Precision, Macro-Recall, and Macro-F1 across `Senseval-2` and `SemCor`.
   - Zipfian sense frequency plots and per-word Confusion Matrix heatmaps.
3. **Final Project Report (`Report.pdf`):**
   - Academic report presenting the formal algorithms for Extended Taxonomic Lesk, Selectional Preferences, Anaphora Context Projection, RST Clause Weighting, Naive Bayes, and Logistic Regression, alongside comprehensive linguistic error analysis.

---

## 11. Key Research Paper References

1. **Banerjee, S., & Pedersen, T. (2002).** *An Adapted Lesk Algorithm for Word Sense Disambiguation Using WordNet.* Proceedings of the 3rd International Conference on Intelligent Text Processing and Computational Linguistics (CICLing 2002), 136–145. *(Foundational paper introducing Extended Lesk using WordNet hypernym, hyponym, and meronym gloss hierarchies.)*
2. **Yarowsky, D. (1995).** *Unsupervised Word Sense Disambiguation Rivaling Supervised Methods.* Proceedings of the 33rd Annual Meeting of the Association for Computational Linguistics (ACL 1995), 189–196. *(Establishes the two foundational linguistic laws of WSD: "One Sense Per Collocation" and "One Sense Per Discourse".)*
3. **Resnik, P. (1997).** *Selectional Preference and Sense Disambiguation.* Proceedings of the ACL SIGLEX Workshop on Tagging Text with Lexical Semantics: Why, What, and How?, 52–57. *(Models compositional verb–argument selectional restrictions using WordNet taxonomic information content for WSD.)*
4. **Lee, Y. K., & Ng, H. T. (2002).** *An Empirical Evaluation of Knowledge Sources and Learning Algorithms for Word Sense Disambiguation.* Proceedings of EMNLP 2002, 41–48. *(Systematic evaluation of Naive Bayes, Maximum Entropy / Logistic Regression, and linguistic feature sources—POS, local collocations, and syntactic relations—on Senseval benchmarks.)*
5. **Mann, W. C., & Thompson, S. A. (1988).** *Rhetorical Structure Theory: Toward a Functional Theory of Text Organization.* Text - Interdisciplinary Journal for the Study of Discourse, 8(3), 243–281. *(Theoretical framework for Nucleus–Satellite discourse relations used in our cross-clause WSD context weighting.)*
