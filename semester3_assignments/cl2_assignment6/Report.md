# Computational Linguistics 2 (CL-2) — Assignment 6 Report
## Word Embeddings (Co-occurrence Matrix & SVD) and Word Sense Disambiguation (WSD)

- **Student Name:** Baani Solanki
- **Roll Number:** `2025114016`

---

# Part I: Word Embeddings (Co-occurrence Matrix & SVD)

## 1. Introduction & Methodology
Distributional semantic models represent words as continuous real-valued vectors based on the **Distributional Hypothesis**: words that occur in similar contexts tend to have similar meanings. In Part I, we implement a **frequency-based word embedding pipeline** on the provided news corpus (`train.csv`), ignoring the `Class Index` column and processing $19,999$ sentences:
1. **Vocabulary & Co-occurrence Matrix Construction (`part1_task_2_1`):** After lowercasing and tokenizing the $19,999$ sentences into alphabetic words, we extract the top $|V| = 5,000$ most frequent words. For a symmetric sliding window of size $\pm w$ around each target word $w_i$, we count how many times each context word $w_j$ appears within $[t - w, t + w]$ ($t \neq t'$) and store the counts in a sparse matrix $M \in \mathbb{R}^{5000 \times 5000}$ (`scipy.sparse.csr_matrix`).
2. **Dimensionality Reduction Using SVD (`part1_task_2_2`):** Because the raw $5000 \times 5000$ co-occurrence matrix is high-dimensional and sparse, we factorize it using truncated Singular Value Decomposition (`scipy.sparse.linalg.svds`):
   $$M \approx U_k \Sigma_k V_k^T$$
   keeping the top $k = 100$ singular components sorted in descending order. Each row of $U_k \in \mathbb{R}^{5000 \times 100}$ provides a dense $100$-dimensional embedding for a word in the vocabulary.
3. **Evaluating Word Embeddings (`part1_task_2_3`):** We compute **Cosine Similarity** from scratch between word vector pairs $\vec{u}_a$ and $\vec{u}_b$:
   $$\text{CosineSimilarity}(\vec{u}_a, \vec{u}_b) = \frac{\vec{u}_a \cdot \vec{u}_b}{\|\vec{u}_a\|_2 \, \|\vec{u}_b\|_2}$$

---

## 2. Experimental Results (Tasks 2.1, 2.2, and 2.3)

### 2.1 Co-occurrence Matrix & SVD Summary ($w = 5, k = 100$)
- **Sentences Processed:** $19,999$ sentences from `train.csv`
- **Vocabulary Size ($|V|$):** $5,000$ words
- **Co-occurrence Matrix Shape:** $5000 \times 5000$
- **Non-Zero Entries ($w = 5$):** $1,247,192$ (approx. $4.99\%$ density, $95.01\%$ sparsity)
- **Word Embedding Matrix $U$ Shape:** $5000 \times 100$
- **Top 5 Singular Values ($\Sigma$):**
  $$\sigma_1 = 43369.36,\quad \sigma_2 = 9356.60,\quad \sigma_3 = 4073.58,\quad \sigma_4 = 3071.69,\quad \sigma_5 = 2987.26$$

### 2.2 Cosine Similarity Evaluation on 5 Selected Word Pairs ($w = 5$)

| Word Pair | Relationship Category | Cosine Similarity ($w = 5$) | Interpretation |
| :--- | :--- | :---: | :--- |
| **`(company, firm)`** | **Synonyms** | **`0.4707`** | Highest similarity among all pairs; both words are near-synonyms in business/financial news and share almost identical verb and adjective contexts. |
| **`(computer, software)`** | **Topical / Domain Related** | **`0.1493`** | Second-highest positive similarity; both belong to the technology domain and frequently co-occur with words like *system, microsoft, network, data*. |
| **`(win, lose)`** | **Antonyms** | **`0.1209`** | Moderate positive similarity; despite opposite meanings, antonyms are **distributionally substitutable** in sports and election contexts (*win/lose a game, win/lose the match*). |
| **`(president, government)`** | **Political / Institutional** | **`0.0033`** | Near-zero similarity at $w = 5$; although topically related, `"president"` acts primarily as a personal title before proper names (*"President Bush"*), whereas `"government"` appears in broader institutional syntax. |
| **`(market, football)`** | **Unrelated** | **`-0.0562`** | Slightly negative / near-zero similarity; `"market"` (business/finance) and `"football"` (sports) occur in completely disjoint contexts. |

---

## 3. Task 2.4: Analysis of Similarity Scores & Context Window Variations ($w = 2$ vs. $w = 5$)

### 3.1 Comparison Table Across Window Sizes

| Word Pair | Relationship Category | Window $w = 2$ | Window $w = 5$ | Change ($w=2 \to w=5$) |
| :--- | :--- | :---: | :---: | :---: |
| **`(company, firm)`** | Synonyms | `0.4346` | **`0.4707`** | **`+0.0361`** (Increases with broader window) |
| **`(win, lose)`** | Antonyms | **`0.1494`** | `0.1209` | `-0.0285` (Higher in tight local syntax) |
| **`(computer, software)`** | Topical / Domain Related | **`0.2220`** | `0.1493` | `-0.0727` (Strong direct collocation at $w=2$) |
| **`(president, government)`** | Political / Institutional | **`0.0288`** | `0.0033` | `-0.0255` (Higher in immediate local window) |
| **`(market, football)`** | Unrelated | `0.0930` | **`-0.0562`** | **`-0.1492`** (Drops below zero as noise is removed) |

### 3.2 Detailed Analysis of Results
1. **Why Synonyms `(company, firm)` Improve with a Larger Window ($0.4346 \to 0.4707$):**
   - `"company"` and `"firm"` rarely appear right next to each other in the same phrase, so a narrow window ($w=2$) only captures immediate determiners and verbs (*"the company/firm said"*). Expanding the window to $w=5$ captures the broader sentence-level business topic (*shares, chief, executive, profit, billion*), pulling the two synonyms closer together in the $100$-dimensional SVD space.
2. **Why Antonyms `(win, lose)` Have Positive Similarity and Peak at $w = 2$ ($0.1494$ vs. $0.1209$):**
   - Co-occurrence models do not know logical negation; they measure **contextual substitutability**. In a narrow syntactic window ($w=2$), `"win"` and `"lose"` take the exact same immediate subjects and objects (*"to win/lose the"*, *"could win/lose"*), giving them a positive cosine similarity of `0.1494`. At $w=5$, broader outcome words (*victory, champion* vs. *defeat, injury*) slightly differentiate them (`0.1209`).
3. **Why `(computer, software)` Is Stronger at $w = 2$ ($0.2220$) than $w = 5$ ($0.1493$):**
   - In the AG News corpus, `"computer software"` and `"software company / computer maker"` are frequent direct compound collocations. At $w=2$, their immediate neighbors overlap heavily; at $w=5$, `"computer"` also appears in hardware/retail contexts while `"software"` appears in licensing/security contexts.
4. **How Larger Windows Separate Unrelated Words `(market, football)` ($0.0930 \to -0.0562$):**
   - At $w=2$, any two common nouns share adjacent function words (`"the"`, `"in"`, `"of"`), creating a small artificial baseline similarity (`0.0930`). When the window expands to $w=5$, domain-specific content words dominate the co-occurrence counts, pushing unrelated concepts from different news categories (Business vs. Sports) into orthogonal/opposite subspaces (`-0.0562`).

---

# Part II: Word Sense Disambiguation (WSD)

## 1. Problem 1: Preprocessing and POS Tagging (5 Marks)
We loaded $2,500$ sense-annotated instances from `wsd-data/wsd_train.txt` ($2,000$ training instances and $500$ held-out test instances). Each instance consists of a gold WordNet sense key (`keep%2:42:07::`), a target `lemma.pos` (`keep.v`), the 0-based token index of the target word, and a multi-sentence context passage.
- **Tokenization & POS Tagging:** Each passage was segmented into sentences using `nltk.tokenize.sent_tokenize`, tokenized into words via `nltk.tokenize.word_tokenize`, and POS-tagged using `nltk.pos_tag`.
- **Sample POS Tagging Output (Instance 1):**
  `[('Action', 'NN'), ('by', 'IN'), ('the', 'DT'), ('Committee', 'NNP'), ('In', 'IN'), ('pursuance', 'NN'), ('of', 'IN'), ('its', 'PRP$'), ('mandate', 'NN'), (',', ',')]`

---

## 2. Problem 2: Listing Possible Senses for the First 10 Sentences (5 Marks)
For every content word (**noun, verb, adjective, adverb**) in the first $10$ training sentences, we mapped its Penn Treebank POS tag to WordNet (`NOUN`, `VERB`, `ADJ`, `ADV`), queried `wn.synsets()`, and saved each sense's synset name, definition (`gloss`), and example usage (`examples`) to `first_10_sentences_senses.json`.

### Sample Extracted Senses from Sentence 1 (`first_10_sentences_senses.json`):
- **`Action` (`NN`, 10 senses):**
  - `action.n.01`: *Gloss:* `"something done (usually as opposed to something said)"` | *Example:* `["there were stories of murders and other unnatural actions"]`
  - `action.n.09`: *Gloss:* `"an act by a government body or supranational organization"` | *Example:* `["the United Nations must have the power to propose and organize action without being hobbled by irrelevant issues"]`
- **`Committee` (`NNP`, 2 senses):**
  - `committee.n.01`: *Gloss:* `"a special group delegated to consider some matter; - Milton Berle"` | *Example:* `["a committee is a group that keeps minutes and loses hours"]`
  - `committee.n.02`: *Gloss:* `"a self-constituted organization to promote something"` | *Example:* `[]`
- **`mandate` (`NN`, 3 senses):**
  - `mandate.n.01`: *Gloss:* `"a document giving an official instruction or command"`
  - `mandate.n.02`: *Gloss:* `"a territory surrendered by Turkey or Germany after World War I..."`
  - `mandate.n.03`: *Gloss:* `"the commission that is given to a government and its policies through an electoral victory"`

---

## 3. Problem 3: Most Frequent Sense (MFS) Baseline (5 Marks)
For each of the $2,000$ training instances, we extracted WordNet's most frequent sense (`synsets[0]`, ordered by SemCor frequency) for the target word:
- **Precision:** **`15.90%`**
- **Recall:** **`15.90%`**
- **F1-Score:** **`15.90%`**

*(Note: Precision, Recall, and F1 are equal because every target word in the dataset is present in WordNet, yielding $100\%$ coverage with $\text{Attempted} = \text{Total} = 2,000$. Furthermore, because `wsd_train.txt` is drawn from formal United Nations diplomatic documents where secondary/idiomatic senses like `"in line with"`, `"keep under review"`, and `"hold that"` are heavily used, WordNet's general-domain #1 sense achieves `15.90%` rather than the $50\%+$ seen on everyday text.)*

---

## 4. Problem 4: Simplified Lesk Algorithm From Scratch (10 Marks)
We implemented the **Simplified Lesk Algorithm** from scratch in `simplified_lesk()`. For each marked target word, we collect the lowercase alphabetic words in the local sentence window containing the target word and compute the exact word overlap with the WordNet gloss and example sentences of each candidate sense.

### Illustrative Example of Overlap Computation (`target_word = 'keep'`)
- **Passage:** *"Action by the Committee In pursuance of its mandate , the Committee will continue to keep under review the situation relating to the question of Palestine and participate in relevant meetings of the General Assembly and the Security Council . The Committee will also continue to monitor the situation on the ground..."*
- **Gold Intended Sense:** `continue.v.01` (*"continue a certain state, condition, or activity"*)
- **Predicted Sense (Basic Lesk):** `retain.v.02` (*"allow to remain in a place or position or maintain a property or feature"*)
- **Candidate Glosses & Computed Overlaps:**
  - `support.n.06`: **Overlap = 2** (`['the', 'to']`) $\to$ *Gloss:* `"the financial means whereby one lives"`
  - `keep.n.02`: **Overlap = 2** (`['of', 'the']`) $\to$ *Gloss:* `"the main tower within the walls of a medieval castle or fortress"`
  - `hold.n.07`: **Overlap = 1** (`['in']`) $\to$ *Gloss:* `"a cell in a jail or prison"`
  - `keep.v.01`: **Overlap = 2** (`['in', 'the']`) $\to$ *Gloss:* `"keep in a certain state, position, or activity; e.g.,"`
  - `continue.v.01` (Gold): **Overlap = 3** (`['continue', 'the', 'to']`) $\to$ *Gloss:* `"continue a certain state, condition, or activity"`
  - `keep.v.03`: **Overlap = 1** (`['of']`) $\to$ *Gloss:* `"retain possession of"`
  - `retain.v.02` (Winner): **Overlap = 4** (`['in', 'of', 'the', 'to']`) $\to$ *Gloss:* `"allow to remain in a place or position or maintain a property or feature"`

### Comparison: Simplified Lesk vs. MFS Baseline (Training Set)

| WSD Model (Training Set — 2,000 Instances) | Precision (%) | Recall (%) | F1-Score (%) |
| :--- | :---: | :---: | :---: |
| **Most Frequent Sense (MFS) Baseline** | **`15.90%`** | **`15.90%`** | **`15.90%`** |
| **Simplified Lesk Algorithm (Basic)** | `9.20%` | `9.20%` | `9.20%` |

**Why Basic Simplified Lesk Underperforms MFS (`9.20%` vs. `15.90%`):**
As the illustrative walkthrough for `'keep'` proves, Basic Lesk's overlap counts are dominated by **stopwords** (`'in'`, `'of'`, `'the'`, `'to'`). Even though the gold sense `continue.v.01` matched the meaningful content word `'continue'`, `retain.v.02` won purely because its definition and examples happened to contain all four common prepositions/articles (`'in'`, `'of'`, `'the'`, `'to'`). Additionally, Basic Lesk checks noun senses (`keep.n.02`, `support.n.06`) even when `'keep'` is used as a verb.

---

## 5. Problem 5: Improved Lesk Algorithm (10 Marks)
We extended our Lesk implementation in `improved_lesk()` with **all four** textbook enhancements:
1. **Lemmatization and Stopword Removal:** Removes English stopwords (`nltk.corpus.stopwords`) and short tokens ($\le 2$ chars) and lemmatizes both context words and sense definitions using `WordNetLemmatizer`.
2. **POS-Based Filtering:** Uses the POS tag at `target_index` to restrict candidate synsets to the matching WordNet POS (`NOUN`, `VERB`, `ADJ`, `ADV`).
3. **Hypernym & Hyponym Gloss Expansion:** Concatenates the definitions and examples of `syn.hypernyms()` and `syn.hyponyms()` into each candidate sense's word set.
4. **Expanded Context Window (Neighboring Sentences):** Expands the context window from the single target sentence to include the neighboring sentences in the passage.

### Quantitative Comparison: Improved Lesk vs. Basic Lesk vs. MFS Baseline

| WSD System (Training Set — 2,000 Instances) | Precision (%) | Recall (%) | F1-Score (%) | vs. Basic Lesk | vs. MFS Baseline |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Simplified Lesk (Basic)** | `9.20%` | `9.20%` | `9.20%` | — | `-6.70%` |
| **Most Frequent Sense (MFS) Baseline** | `15.90%` | `15.90%` | `15.90%` | `+6.70%` | — |
| **Improved Lesk (All 4 Enhancements)** | **`18.60%`** | **`18.60%`** | **`18.60%`** | **`+9.40%` (`+102.2%` rel.)** | **`+2.70%`** |

### Analysis of Observed Improvements:
- **Doubling the F1-Score over Basic Lesk (`9.20%` $\to$ `18.60%`):** Removing stopwords immediately eliminates false matches on `'the'`, `'of'`, `'in'`, and `'to'`. POS filtering discards impossible part-of-speech candidates (such as adjective or noun senses when disambiguating a verb).
- **Beating the MFS Baseline (`15.90%` $\to$ `18.60%`):** Because WordNet glosses are very brief, single-sentence content overlap is often zero (which would otherwise force a tie-break fallback to MFS). Expanding candidate signatures with **hypernym and hyponym glosses** and expanding the context window to **neighboring sentences** creates genuine content-word intersections that allow Improved Lesk to outperform MFS by `+2.70%`.

---

## 6. Problem 6: Manual Evaluation and Analysis of 10 Ambiguous Words (5 Marks)

Below is the manual evaluation of the **10 ambiguous words** output by our system against WordNet's intended sense:

| # | Word | Gold Intended Sense & Gloss | Basic Lesk Prediction & Gloss | Improved Lesk Prediction & Gloss | Manual Evaluation & Analysis |
| :-: | :--- | :--- | :--- | :--- | :--- |
| **1** | **`keep`** | `continue.v.01` (*continue a certain state, condition, or activity*) | `retain.v.02` (*allow to remain in a place or position...*) | `keep.v.01` (*keep in a certain state, position, or activity*) | Improved Lesk eliminated `retain.v.02`'s stopword win and picked the closely related synset `keep.v.01` (*keep in a certain state*), showcasing WordNet's ultra-fine sense granularity between `keep.v.01` and `continue.v.01`. |
| **2** | **`national`** | `national.a.01` (*of or relating to or belonging to a nation or country*) | `home.s.01` (*inside the country*) | **`national.a.01`** (*of or relating to or belonging to a nation or country*) | **Fixed by Improved Lesk!** Context words (*"States"*, *"flags"*) overlapped with `national.a.01`'s expanded gloss once stopword noise in `home.s.01` was removed. |
| **3** | **`built`** | `build.v.08` (*found or ground*) | `built.s.01` (*(used of soaps or cleaning agents) having a substance added...*) | `build_up.v.02` (*form or accumulate steadily*) | **POS filtering** fixed Basic Lesk's severe POS error (matching the adjective sense `built.s.01` about soap/detergent instead of a verb), though metaphorical `build.v.08` (*"built on the following elements"*) had sparse gloss overlap. |
| **4** | **`place`** | `position.n.06` (*a job in an organization*) | `place.n.03` (*an abstract mental location*) | `topographic_point.n.01` (*a point located with respect to surface features...*) | Idiomatic phrase *"remain in place"*; geographic/regional terms in the UN passage (*Pakistan, Tunisia*) caused hypernym overlap with `topographic_point.n.01`. |
| **5** | **`positions`** | `position.n.06` (*a job in an organization*) | `place.n.15` (*an item on a list or in a sequence*) | `status.n.01` (*the relative position or standing of things or persons in a society*) | Basic Lesk matched `"list"` in the sentence to `place.n.15`; Improved Lesk moved closer to human/social roles (`status.n.01`), though `position.n.06`'s brief 5-word gloss lacked overlap with *"scientific and engineering"*. |
| **6** | **`serve`** | `serve.v.07` (*devote (part of) one's life or efforts to, as of countries, institutions...*) | `serve.v.02` (*do duty or hold offices; serve in a specific function*) | `suffice.v.01` (*be sufficient; be adequate, either in quality or quantity*) | Context words *"meet the specific needs"* overlapped with `suffice.v.01`'s hypernym/hyponym definitions (*meet/satisfy needs*). |
| **7** | **`holds`** | `deem.v.01` (*keep in mind or convey as a conviction or view*) | `hold.v.10` (*be the physical support of; carry the weight of*) | `keep.v.01` (*keep in a certain state, position, or activity*) | Metaphorical usage (*"one school of thought holds that..."*); none of the surrounding diplomatic words (*negotiations, disarmament*) literally appear in `deem.v.01`'s gloss. |
| **8** | **`line`** | `line.n.16` (*acting in conformity*) | `line.n.01` (*a formation of people or things one beside another*) | `occupation.n.01` (*the principal activity in your life that you do to earn money*) | Idiomatic prepositional phrase (*"bring law into line with..."*); `line` has 30 noun senses in WordNet, and financial/business terms in the sentence triggered overlap with `occupation.n.01`. |
| **9** | **`see`** | `see.v.05` (*deem to be*) | `witness.v.02` (*perceive or be contemporaneous with*) | `understand.v.02` (*perceive (an idea or situation) mentally*) | Improved Lesk shifted from physical/temporal witnessing (`witness.v.02`) to mental perception (`understand.v.02`), which is semantically very close to `see.v.05` (*"see the NPT as the cornerstone"*). |
| **10** | **`time`** | `time.n.03` (*an indefinite period (usually marked by specific attributes or activities)*) | **`time.n.03`** (*an indefinite period...*) | **`time.n.03`** (*an indefinite period...*) | **Correctly predicted by both** Basic and Improved Lesk due to rich temporal context words (*"lengthy"*, *"age"*, *"little time to spare"*). |

### Discussion: Helpful Features & Key Limitations of Lesk
1. **Most Helpful Linguistic & Knowledge-Based Features:**
   - **POS-Based Filtering:** Immediately prevents embarrassing cross-POS errors (such as predicting the soap/detergent adjective `built.s.01` for the verb `"built"`, or medieval castle tower `keep.n.02` for the verb `"keep"`).
   - **Stopword Removal & Lemmatization:** Eliminates function-word bias toward long definitions and matches inflected words (`"positions"` $\to$ `"position"`, `"holds"` $\to$ `"hold"`).
   - **Hypernym/Hyponym Gloss Expansion:** Mitigates dictionary sparsity when the target sense's own definition is only 3–5 words long (e.g., `build.v.08`: *"found or ground"*).
2. **Key Limitations of the Lesk Algorithm for Real-World Disambiguation:**
   - **Exact Lexical Overlap Bottleneck (Vocabulary Mismatch):** Dictionary definitions are written using abstract meta-language (*"a conviction or view"*, *"acting in conformity"*), whereas real sentences contain concrete domain vocabulary (*"nuclear disarmament"*, *"Financial Action Task Force"*). Even when a human immediately recognizes the meaning, exact word intersection can be zero.
   - **Idioms and Multi-Word Expressions:** Phrases like *"bring into line with"*, *"remain in place"*, and *"keep under review"* have non-compositional meanings whose surrounding domain words accidentally overlap with literal noun/verb senses.
   - **Extreme Fine-Grained Polysemy in WordNet:** WordNet splits common verbs and nouns (`keep`, `hold`, `see`, `line`, `serve`) into $15–30$ overlapping micro-senses (e.g., `continue.v.01` vs. `keep.v.01`, or `see.v.05` vs. `understand.v.02`), where dictionary glosses alone cannot separate near-identical senses.

---

## 7. Problem 7 (Extra Credit): Supervised Naive Bayes WSD System (15 Marks)

### 7.1 Model Architecture & Extracted Features
We implemented a **from-scratch Multinomial Naive Bayes WSD classifier** (`part2_naive_bayes.py`) trained on the $2,000$ training instances and evaluated on the **$500$ held-out test instances**. For each instance, we extract three linguistic feature types:
1. **Target POS Tag:** `POS=<tag>` at `target_index`.
2. **Local Collocations ($\pm 2$ Window):** Exact words and POS tags at offsets $\{-2, -1, +1, +2\}$ (`W_offset=<word>`, `P_offset=<pos>`), which directly capture idioms and local phrasal patterns like `"into line with"` or `"keep under review"`.
3. **Bag-of-Words Context (`BOW=<word>`):** Stopword-filtered content words across the passage.

For each candidate sense $s$ of a target `lemma.pos`, we compute the Laplace-smoothed ($\alpha = 1$) log-posterior score:
$$\hat{s} = \arg\max_{s} \left[ \log P(s) + \sum_{f \in F} \log \frac{\text{count}(f, s) + 1}{\sum_{f'} \text{count}(f', s) + |V_{\text{lemma}}|} \right]$$

### 7.2 Test Set Performance Comparison (500 Held-Out Test Instances)

| WSD System (Evaluated on 500 Test Instances) | Precision (%) | Recall (%) | F1-Score (%) | Gain over Basic Lesk | Gain over Improved Lesk |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Simplified Lesk Algorithm** | `12.20%` | `12.20%` | `12.20%` | — | `-6.40%` |
| **Most Frequent Sense (MFS) Baseline** | `16.60%` | `16.60%` | `16.60%` | `+4.40%` | `-2.00%` |
| **Improved Lesk Algorithm** | `18.60%` | `18.60%` | `18.60%` | `+6.40%` | — |
| **Supervised Naive Bayes WSD (Extra Credit)** | **`51.00%`** | **`51.00%`** | **`51.00%`** | **`+38.80%`** | **`+32.40%`** |

### 7.3 Why Naive Bayes Dramatically Outperforms Lesk (`51.00%` vs. `18.60%` F1)
1. **Learning Domain Sense Priors $\log P(s)$:** Instead of relying on WordNet's general-English sense ordering (where MFS only gets `16.60%`), Naive Bayes learns the true empirical sense distribution of the UN corpus from the training set.
2. **Capturing Fixed Collocations ($\pm 2$ Offsets):** Local collocation features (`W_-1=into`, `W_1=with` for `line.n.16`; `W_1=under`, `W_2=review` for `continue.v.01`) directly solve the idiomatic and phrasal usages where dictionary gloss overlap fails.
3. **Probabilistic Weighting of Corpus Context:** Rather than requiring a context word to literally appear inside a 10-word dictionary definition, Naive Bayes learns statistical associations between every corpus content word and the gold sense across $2,000$ training examples, Nearly **tripling** the F1-score of Improved Lesk (`18.60%` $\to$ `51.00%`) and **more than quadrupling** Simplified Lesk (`12.20%` $\to$ `51.00%`).
