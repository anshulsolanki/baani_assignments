# Why Proposal 2 Is Strong & Will Not Be Rejected

**Project Title:** *Disambiguating Meaning Across Sentences: A Hybrid Knowledge-Based and Supervised Word Sense Disambiguation System Using WordNet Selectional Preferences, Anaphora Resolution, and Discourse Structure*  
**Team:** Yashaswi Priya (`2025114007`) & Baani Solanki (`2025114016`)

---

## 1. It Directly Synthesizes the #1 Group of Topics (`P1, P2, P9, P10`) in `project-titles.pdf`

On Pages 1–2 of `project-titles.pdf` (*Project titles for "Computational Semantics"*), Prof. Parameswari Krishnamurthy and Prof. Rajakrishnan Rajkumar explicitly list **four separate project titles** centered on **Word Sense Disambiguation (WSD) and Lexical Semantics**:
- **P1:** *"Word Sense Disambiguation using Thesaurus/Dictionary/Knowledge-based Methods: Develop algorithms that leverage thesauri, dictionaries, or knowledge bases to determine the correct sense of ambiguous words in text."*
- **P2:** *"Word Sense Disambiguation Using Supervised Machine Learning Algorithms: Implement machine learning techniques to disambiguate word senses by training models on labeled data."*
- **P9:** *"Comparative Analysis of LESK Algorithm with Other Word Sense Disambiguation Methods: Evaluate the performance of the LESK algorithm against other word sense disambiguation methods for comparison."*
- **P10:** *"Word Similarity/Relatedness using Lexical Resources: Develop models to measure word similarity or relatedness using lexical resources such as WordNet, Synset, VerbNet, or FrameNet."*

### Why Combining These with Discourse & Anaphora Makes It Ideal for a 2-Person Team:
- Implementing basic Lesk (`P1`) alone is too small for two students.
- By combining **Knowledge-Based WSD (`P1 + P9 + P10`: Simplified Lesk $\to$ Extended WordNet Taxonomic Lesk + Verb–Argument Selectional Preferences)** with **Supervised Statistical WSD (`P2`: Naive Bayes vs. Logistic Regression)** AND extending both with **Cross-Sentence Anaphora Resolution** and **Rhetorical Structure Theory (RST) Discourse Weighting**, this proposal hits the exact sweet spot of Computational Linguistics 2: **deep semantics + discourse structure + classical statistical modeling**.

---

## 2. How Proposal 2 Differs Completely from Proposal 1

| Dimension | Proposal 1 (`proposal 1/`) | Proposal 2 (`proposal 2/`) |
| :--- | :--- | :--- |
| **Core Task** | Document-Level **Sentiment Analysis** (Positive vs. Negative Opinion Classification) | **Word Sense Disambiguation (WSD)** (Multiclass Fine-Grained WordNet Sense Classification) |
| ** Handout Topics Used** | `P13 + P20 + P21 + P22` | `P1 + P2 + P9 + P10 + P22` |
| **Primary Datasets** | Cornell Movie Reviews (`nltk.corpus.movie_reviews`) + MPQA & Hu–Liu Polarity Lexicons | **Senseval-2** (`nltk.corpus.senseval`: `interest, line, serve, hard`) + **SemCor** (`nltk.corpus.semcor`) + **WordNet 3.0** |
| **Semantic Theory** | Compositional Polarity Shifters (Negation Scope, Intensifiers, Irrealis Modals) | Lexical Taxonomies (Hypernyms, Meronyms, Troponyms), Extended Lesk, & Verb–Argument Selectional Preferences |
| **Role of Anaphora** | Identifying whether an opinion word modifies a central topical entity (discourse center) | **Projecting disambiguating predicates** from a pronoun (`it, they`) in sentence $s_{t+1}$ back onto an ambiguous target noun in sentence $s_t$ |
| **Role of Discourse (RST)** | Weighting Nucleus clauses over Concessive Satellite clauses (*"Although X, Y"*) | Weighting *Cause/Explanation*, *Elaboration*, and *Contrast* clauses + **Yarowsky's "One Sense Per Discourse"** |

---

## 3. Point-by-Point Comparison: Why the Preliminary Proposal Was Rejected vs. How Proposal 2 Fixes It

| Why Preliminary Proposal (Medical Summarization) Was Rejected | How Proposal 2 (Discourse- & Anaphora-Aware WSD) Solves It |
| :--- | :--- |
| **1. "Simply evaluated pre-existing models without adding any of our own input"** | Zero pre-trained models or black-box APIs are used. Every algorithm—Simplified Lesk, Extended Taxonomic Lesk, Selectional Preference Scorer, Anaphora Context Projector, RST Clause Weighter, Multinomial Naive Bayes, and Multinomial Logistic Regression—is **implemented from scratch by Yashaswi and Baani**. |
| **2. "Did not utilize our linguistic knowledge"** | Uses **every single linguistic concept taught in CL2**:<br>• **Lexical & Compositional Semantics:** WordNet synsets, hypernym/meronym graphs, Wu–Palmer & Information Content similarity, Verb–Argument selectional restrictions.<br>• **Discourse & Pragmatics:** Binding Theory Principles A & B, Anaphora Resolution, RST discourse relations, and Yarowsky's One-Sense-Per-Discourse.<br>• **Statistical NLP:** Zipf's Law of Meaning (sense skew), Collocational N-grams, Smoothing, Naive Bayes, and Logistic Regression. |
| **3. "Used Neural Networks / LLMs"** | **Strictly 0% neural networks.** Purely symbolic (WordNet/CFG) and classical statistical NLP. |
| **4. "Human evaluation would be too difficult to execute"** | **100% automatic, objective evaluation** on gold-standard human-annotated datasets (`Senseval-2` and `SemCor`) built directly into `nltk.corpus`. |
| **5. "Building our own summarizer from scratch is too challenging"** | Discrete multiclass sense classification over gold-annotated instances is completely tractable (~500–650 lines of clean Python) with immediate, reproducible accuracy and F1 metrics. |

---

## 4. Clean, Equal 50/50 Division of Work for Separate Grading

- **Yashaswi Priya (`2025114007`) — Lexical & Compositional Semantics + Generative Classifier:**
  - `wsd_corpus_loader.py`: Senseval-2 & SemCor loaders, Zipfian sense distribution analysis, MFS baseline (`B0`).
  - `knowledge_wsd.py`: Simplified Lesk (`K1`), Extended Taxonomic Lesk with Inverse Gloss Frequency & $n^2$ phrasal scoring, and WordNet Verb–Argument Selectional Preferences (`K2`).
  - `naive_bayes_wsd.py`: Multiclass Multinomial Naive Bayes from scratch with add-$k$ smoothing (`S1`–`S3`).
- **Baani Solanki (`2025114016`) — Anaphora & Discourse Structure + Discriminative Classifier:**
  - `anaphora_wsd_context.py`: Binding Theory + Hobbs'/feature-based anaphora resolution (`it, they, its, them`) projecting pronoun predicates onto target ambiguous nouns.
  - `discourse_rst_wsd.py`: Rule-based EDU segmentation, RST connective weighting (*Cause, Elaboration, Contrast*), and One-Sense-Per-Discourse propagation (`K3`).
  - `logistic_regression_wsd.py`: Multiclass L2-Regularized Logistic Regression (Softmax + SGD) from scratch and feature weight inspection (`S1`–`S3`).
