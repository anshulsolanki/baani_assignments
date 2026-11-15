# CL2 Project Proposal 2 — Viva & Proposal Defense Guide (For Baani & Yashaswi)

This guide prepares you to present and defend **Proposal 2** (*Disambiguating Meaning Across Sentences: Hybrid Knowledge-Based and Supervised Word Sense Disambiguation Using WordNet Selectional Preferences, Anaphora Resolution, and Discourse Structure*) to **Prof. Parameswari Krishnamurthy**, **Prof. Rajakrishnan Rajkumar**, and your TAs.

---

## 1. 30-Second Elevator Pitch (What to Say First)

> *"In our project, we are solving **Word Sense Disambiguation (WSD)**—combining Topics P1, P2, P9, and P10 from the course project handout—by bridging **Lexical Semantics**, **Anaphora Resolution**, **Rhetorical Structure Theory (RST)**, and **Classical Statistical Classifiers (Naive Bayes and Logistic Regression)**.*
>
> *Standard WSD algorithms like Simplified Lesk only look at exact word overlap inside a single sentence. That fails for two reasons: first, dictionary definitions are short, so we need **Extended Taxonomic Lesk** (using WordNet hypernyms, hyponyms, and meronyms) and **Verb–Argument Selectional Preferences** (like knowing 'deposit' selects a financial sense of 'bank'). Second, in multi-sentence texts, the disambiguating clue is often in the next sentence attached to a **pronoun**—for example, 'The customer walked toward the **bank**. **It** had already locked its vault.' A sentence-bound WSD model misses 'locked its vault' because it modifies 'It'. By using **Anaphora Resolution** to resolve 'It' to 'bank', and **RST discourse connectives** plus **One-Sense-Per-Discourse** to weight related clauses, we project cross-sentence semantic clues back onto the target word. We evaluate both Knowledge-Based WSD (`K1`–`K3`) and Supervised **Naive Bayes vs. Logistic Regression** (`S1`–`S3`) on the gold-annotated **Senseval-2** and **SemCor** benchmarks."*

---

## 2. Likely Proposal Viva Questions & Model Answers

### Q1: How does Anaphora Resolution actually help Word Sense Disambiguation? Give a concrete linguistic example.
**Answer:**  
Consider a two-sentence passage containing the polysemous noun **bank** (`bank.n.01` = river slope vs. `bank.n.02` = financial institution):
- **Passage A:** *"The man walked toward the **bank** at noon. **It** was steep and muddy after the rain."*
- **Passage B:** *"The man walked toward the **bank** at noon. **It** was closed for the federal holiday."*
- In Sentence 1 (*"The man walked toward the bank at noon"*), the verb *"walked toward"* gives zero clue about which sense of *bank* is meant! The disambiguating predicates (*"steep and muddy"* vs. *"closed for the federal holiday"*) are in Sentence 2, attached to the subject pronoun **"It"**.
- Using **Binding Theory filters and Hobbs' CFG / feature-based anaphora resolution**, our system resolves `"It"` $\to$ `"bank"` and **projects the governing predicates and modifiers of the pronoun directly into the disambiguation context of `"bank"`**.

---

### Q2: What is the difference between Classical/Simplified Lesk (`K1`) and your Extended Taxonomic Lesk (`K2`)?
**Answer:**  
- **Simplified Lesk (`K1`)** only counts shared lemmatized words between the target word's context and the WordNet gloss (definition + example sentences) of each candidate synset $s_i$. Because a WordNet gloss is typically only 8–15 words long, many valid context words do not literally appear in the gloss.
- **Extended Taxonomic Lesk (`K2`)** (Banerjee & Pedersen, 2002) expands the signature of each candidate synset $s_i$ by traversing the **WordNet semantic graph** to include the glosses of its:
  - **Hypernyms** (*is-a* supertypes, e.g., *financial institution*)
  - **Hyponyms** (*is-a* subtypes, e.g., *credit union, commercial bank*)
  - **Meronyms / Holonyms** (*part-whole* relations, e.g., *vault, teller, Automated Teller Machine*)
  - **Troponyms** (manner relations for verbs)
- Furthermore, we weight overlapping words by **Inverse Gloss Frequency ($\text{IGF}(w) = \log \frac{N}{df(w)}$)** so rare domain terms (like *vault* or *mortgage*) score much higher than generic words, and reward contiguous multi-word overlaps of length $n$ with $n^2$.

---

### Q3: What are "Verb–Argument Selectional Preferences" and how do you compute them using WordNet?
**Answer:**  
In compositional semantics, verbs place semantic restrictions (**selectional preferences**) on the arguments they take (Resnik, 1997):
- For example, in *"serve the dish"*, the direct object *dish* is a `[+FOOD]` noun, which activates the *supply with food* sense of **serve**. In *"serve a four-year term"*, the direct object *term* is a `[+TIME_PERIOD]` noun, which activates the *hold an office/duty* sense of **serve**.
- Similarly, if the target ambiguous word is a noun in `[Verb + Target_Noun]` (e.g., *"climb the bank"* vs. *"rob the bank"*), we compare the candidate noun synsets against the typical argument classes of the governing verb in WordNet using **Wu–Palmer similarity (`wup_similarity`)** and **Resnik/Lin Information Content similarity**.

---

### Q4: How do you use Rhetorical Structure Theory (RST) and Discourse Coherence in WSD?
**Answer:**  
When we expand WSD context beyond a single clause, not all nearby clauses are equally helpful:
1. **RST Clause Weighting:** If two clauses are connected by an explicit **Causal/Explanation** marker (*because, since, therefore, so that*) or **Elaboration/Contrast** marker (*for example, specifically, although, whereas*), the satellite clause directly explains or contrasts the event in the nucleus clause:
   - *"He couldn't play the **bass** [Nucleus] because the **strings** were snapped [Causal Satellite]."* $\to$ *bass* = musical instrument.
   - *"He couldn't catch the **bass** [Nucleus] because the **river** was frozen [Causal Satellite]."* $\to$ *bass* = fish.
   We segment sentences into **Elementary Discourse Units (EDUs)** and assign higher context weight to clauses linked by these rhetorical relations than to unrelated clauses.
2. **Yarowsky's (1995) "One Sense Per Discourse":** When a polysemous word appears multiple times within the same discourse passage, it refers to the same sense over 98% of the time. Our discourse module aggregates evidence across all occurrences of the target lemma in the passage so a high-confidence disambiguation in one sentence resolves ambiguous occurrences in other sentences.

---

### Q5: How does Zipf's Law relate to Word Sense Disambiguation?
**Answer:**  
Just as word frequencies in a corpus follow **Zipf's Law**, the **sense frequencies of an individual polysemous word also follow a steep Zipfian power-law distribution** (Kilgarriff, 2004):
- Sense #1 (the **Most Frequent Sense, MFS**) often accounts for 50–70% of all tokens, while senses #4, #5, and #6 are in the long tail.
- Because of this Zipfian skew, we:
  1. Plot and verify the Zipfian distribution of senses in `SemCor` and `Senseval-2`.
  2. Use the **Most Frequent Sense (`B0`)** as a tough statistical baseline.
  3. Report both **Accuracy (Micro-F1)** and **Macro-Averaged F1** (which weights rare senses equally with frequent senses), and show how combining Knowledge-Based Extended Lesk (`K2/K3`) with Supervised Classifiers (`S2/S3`) improves performance on rare tail senses where training data is sparse.

---

### Q6: Why compare Multinomial Naive Bayes and Multinomial Logistic Regression (`S1`–`S3`)?
**Answer:**  
Following Lee & Ng (2002) and Topic **P2**:
- **Multinomial Naive Bayes** is a generative model that multiplies conditional probabilities $P(f_j \mid s_k)$ assuming all features are conditionally independent given the sense $s_k$. Because local collocations ($w_{-1}$, bigram $w_{-1}w_{+1}$, POS $t_{-1}$) and Lesk scores overlap, Naive Bayes can over-count correlated features.
- **Multinomial Logistic Regression (MaxEnt)** is a discriminative model trained with Cross-Entropy loss and L2 regularization that optimizes feature weights jointly, handling overlapping collocational, syntactic, semantic, and discourse features without independence assumptions.

---

### Q7: Which datasets are you using, and why do they require zero human evaluation?
**Answer:**  
Both datasets are gold-standard human-annotated WSD corpora built directly into NLTK:
1. **`nltk.corpus.senseval` (Senseval-2 English Lexical Sample):** 4,328 multi-sentence instances across four classic ambiguous words covering Nouns (`interest.pos`, `line.pos`), Verbs (`serve.pos`), and Adjectives (`hard.pos`).
2. **`nltk.corpus.semcor` (SemCor):** Multi-sentence passages from the Brown Corpus where every content word is hand-tagged with its exact WordNet 3.0 synset.
Because every instance has a gold WordNet sense tag, **Accuracy, Macro-Precision, Macro-Recall, Macro-F1, and Confusion Matrices** are computed 100% automatically.

---

### Q8: How is the work divided 50/50 between Yashaswi and Baani?
**Answer:**  
- **Yashaswi Priya (`2025114007`)** owns **Knowledge-Based Lexical & Compositional Semantics + Naive Bayes**:
  - Data loaders & Zipfian sense distribution analysis (`wsd_corpus_loader.py`)
  - Simplified Lesk (`K1`), Extended Taxonomic Lesk with Inverse Gloss Frequency & $n^2$ phrasal overlap, and WordNet Verb–Argument Selectional Preferences (`knowledge_wsd.py`)
  - Custom Multinomial Naive Bayes WSD classifier (`naive_bayes_wsd.py`)
- **Baani Solanki (`2025114016`)** owns **Anaphora & Discourse Context Enrichment + Logistic Regression**:
  - Binding Theory + Hobbs'/feature-based Anaphora Context Projection (`anaphora_wsd_context.py`)
  - Rule-based EDU segmentation, RST connective weighting, and One-Sense-Per-Discourse propagation (`discourse_rst_wsd.py`)
  - Custom Multinomial L2 Logistic Regression WSD classifier (`logistic_regression_wsd.py`)
