# Understanding & Viva Preparation Guide — CL-2 Assignment 6
## Word Embeddings (Co-occurrence Matrix & SVD) and Word Sense Disambiguation (WSD)

- **Student Name:** Baani Solanki
- **Roll Number:** `2025114016`
- **Modular Code Files:** `main.py`, `data_loader.py`, `part1_embeddings.py`, `part2_preprocessing.py`, `part2_lesk.py`, `part2_naive_bayes.py`

---

## 1. Concept & Problem Walkthrough ("What & Why Before How")

### Part I: Frequency-Based Word Embeddings (`train.csv`)
1. **What are we trying to do?**
   We want to convert words into $100$-dimensional numerical vectors (embeddings) purely from corpus co-occurrence counts so that semantically similar words (`"company"` and `"firm"`) have vectors pointing in similar directions.
2. **Why Co-occurrence Matrix + SVD?**
   - **Co-occurrence Matrix ($M$):** Counts how often each target word appears within $\pm w$ tokens of each context word across $19,999$ sentences in `train.csv` (ignoring the `Class Index` column). For $|V| = 5,000$ words, $M$ is $5000 \times 5000$ with $1,247,192$ non-zero entries at $w = 5$.
   - **Truncated SVD ($M \approx U \Sigma V^T$):** Raw co-occurrence rows are $5000$-dimensional, sparse ($95\%$ zeros), and noisy. `scipy.sparse.linalg.svds(cooc_matrix, k=100)` compresses $M$ into the top $100$ latent semantic dimensions, giving us the dense target word matrix $U \in \mathbb{R}^{5000 \times 100}$.

---

### Part II: Word Sense Disambiguation (`wsd-data/wsd_train.txt`)
1. **What are we trying to do?**
   Each line in `wsd_train.txt` gives a gold WordNet sense key (`keep%2:42:07::`), a target `lemma.pos` (`keep.v`), the 0-based position of the target word (`15`), and a multi-sentence passage. Our goal is to predict the exact WordNet synset (`continue.v.01`) intended in that context.
2. **How our 4 WSD models progress from `9.20%` $\to$ `15.90%` $\to$ `18.60%` $\to$ `51.00%`:**
   - **Basic Simplified Lesk (`9.20%` train, `12.20%` test):** Compares raw words in the target sentence against raw words in each candidate sense's WordNet gloss + examples. Fails frequently because stopwords (`"the"`, `"of"`, `"in"`, `"to"`) dominate the overlap count and POS is not filtered.
   - **Most Frequent Sense — MFS Baseline (`15.90%` train, `16.60%` test):** Always picks `wn.synsets(lemma, pos)[0]`. Because `wsd_train.txt` comes from formal UN documents where idiomatic/secondary senses (*"in line with"*, *"keep under review"*) are common, static WordNet sense #1 only gets `15.90%`.
   - **Improved Lesk (`18.60%` train, `18.60%` test):** Adds **(1) Lemmatization & stopword removal**, **(2) POS filtering**, **(3) Hypernym & hyponym gloss expansion**, and **(4) Neighboring sentences context**. This doubles Basic Lesk's F1 (`9.20%` $\to$ `18.60%`) and beats the MFS baseline (`15.90%` $\to$ `18.60%`).
   - **Supervised Naive Bayes (`51.00%` test):** Learns empirical sense priors $\log P(s)$, $\pm 2$ word/POS collocations, and bag-of-words likelihoods $\log P(f \mid s)$ directly from the $2,000$ training instances, jumping to **`51.00%` F1** on the $500$ test instances.

---

## 2. Key Viva Pointers ("What to Show the TA")

| Assignment Task | File & Function | Exact Lines | What to Highlight to the TA |
| :--- | :--- | :---: | :--- |
| **Data Loading (Part 1 & 2)** | `data_loader.py` $\to$ `load_sentences_from_csv()`, `load_wsd_data()` | `L6–L86` | Ignores column 0 (`Class Index`) in `train.csv`; parses the 4 tab-separated columns of `wsd_train.txt` and converts `sense_key` via `wn.lemma_from_key(sense_key).synset().name()`. |
| **Part 1 — Task 2.1** | `part1_embeddings.py` $\to$ `part1_task_2_1()` | `L8–L39` | Top-$5000$ `Counter` vocabulary, symmetric window `[i - window_size, i + window_size]`, stored in a `csr_matrix`. |
| **Part 1 — Task 2.2** | `part1_embeddings.py` $\to$ `part1_task_2_2()` | `L42–L51` | Calls `svds(cooc_matrix, k=100)` and reverses singular values into descending order (`np.argsort(singular_values)[::-1]`). |
| **Part 1 — Task 2.3 & 2.4** | `part1_embeddings.py` $\to$ `compute_cosine_similarity()`, `part1_task_2_3()`, `part1_task_2_4()` | `L54–L93` | Explicit loop computing dot product and norms from scratch; compares $w=2$ vs. $w=5$ on 5 word pairs. |
| **Part 2 — Problem 1 & 2** | `part2_preprocessing.py` $\to$ `part2_problem_1()`, `part2_problem_2()` | `L25–L60` | Runs `sent_tokenize`, `word_tokenize`, and `nltk.pos_tag`; writes all content-word senses/glosses/examples for first 10 sentences to `first_10_sentences_senses.json`. |
| **Part 2 — Problem 3 (MFS)** | `part2_lesk.py` $\to$ `predict_mfs_sense()`, `part2_problem_3()` | `L11–L30` | Extracts `synsets[0]` and computes Precision, Recall, and F1 (`15.90%`). |
| **Part 2 — Problem 4 (Basic Lesk)** | `part2_lesk.py` $\to$ `simplified_lesk()`, `part2_problem_4()` | `L39–L81` | Set intersection between local sentence words and candidate gloss+example words (`9.20%` F1). |
| **Part 2 — Problem 5 (Improved Lesk)** | `part2_lesk.py` $\to$ `clean_and_lemmatize()`, `get_expanded_gloss_words()`, `improved_lesk()` | `L86–L164` | Applies all 4 enhancements (`18.60%` F1 — more than double Basic Lesk and beats MFS). |
| **Part 2 — Problem 6 (10 Words)** | `part2_lesk.py` $\to$ `part2_problem_6()` | `L169–L189` | Prints Gold vs. Basic Lesk vs. Improved Lesk senses and glosses for 10 distinct ambiguous lemmas. |
| **Part 2 — Problem 7 (Naive Bayes)** | `part2_naive_bayes.py` $\to$ `extract_features()`, `train_naive_bayes()`, `predict_naive_bayes()` | `L10–L80` | Extracts target POS, $\pm 2$ collocations, and BOW; computes Laplace-smoothed log-probabilities (`51.00%` Test F1). |

---

## 3. 12 Likely Viva Questions & Ready-to-Speak Answers

1. **Q: Why does `svds` need `np.argsort(singular_values)[::-1]`?**
   - **A:** `scipy.sparse.linalg.svds` returns singular values in ascending order (smallest to largest). Reversing the indices puts the largest singular values (e.g., $\sigma_1 = 43369.36$) and their corresponding singular vectors first.
2. **Q: Why did `(company, firm)` increase from `0.4346` ($w=2$) to `0.4707` ($w=5$), while `(market, football)` dropped from `0.0930` ($w=2$) to `-0.0562` ($w=5$)?**
   - **A:** At $w=2$, shared adjacent stopwords (`"the"`, `"in"`, `"of"`) create slight baseline similarity even between unrelated nouns (`0.0930`). At $w=5$, broader topical words enter the window, pulling true synonyms (`company, firm`) closer together while pushing unrelated domains (`market` vs. `football`) apart.
3. **Q: Why do antonyms like `(win, lose)` have a positive cosine similarity (`0.1494` at $w=2$, `0.1209` at $w=5$)?**
   - **A:** Because distributional embeddings measure **contextual substitutability**, not logical truth value. `"win"` and `"lose"` appear in the exact same syntactic slots (*"win/lose the game"*), so they share similar context vectors.
4. **Q: How did you map the gold sense key (`keep%2:42:07::`) in `wsd_train.txt` to a WordNet synset?**
   - **A:** Using NLTK WordNet's `wn.lemma_from_key(sense_key).synset().name()`, which maps the sense key `keep%2:42:07::` directly to its canonical synset ID `continue.v.01`.
5. **Q: Why are Precision, Recall, and F1 identical (`15.90%`, `9.20%`, `18.60%`, `51.00%`) across your WSD models?**
   - **A:** In WSD, $\text{Precision} = \frac{\text{Correct}}{\text{Attempted}}$ and $\text{Recall} = \frac{\text{Correct}}{\text{Total}}$. Because every target word in `wsd_train.txt` has candidate synsets in WordNet, our models make a prediction on $100\%$ of instances ($\text{Attempted} = \text{Total}$), so $\text{Precision} = \text{Recall} = \text{F1}$.
6. **Q: Why is the MFS baseline `15.90%` on `wsd_train.txt` instead of $50\%+$?**
   - **A:** WordNet orders senses by frequency in general everyday English (SemCor), whereas `wsd_train.txt` consists of formal UN diplomatic documents where secondary, legal, and idiomatic senses (such as `line.n.16` in *"into line with"* or `continue.v.01` in *"keep under review"*) occur much more frequently than WordNet's literal #1 sense (`line.n.01` or `keep.v.01`).
7. **Q: Walk through why Basic Lesk failed on `'keep'` in Sentence 1 (Problem 4).**
   - **A:** The gold sense `continue.v.01` had an overlap of $3$ (`['continue', 'the', 'to']`), which included the content word `'continue'`. However, `retain.v.02` won with an overlap of $4$ purely by matching four stopwords (`['in', 'of', 'the', 'to']`). That is why removing stopwords in Improved Lesk is essential.
8. **Q: How did POS filtering help on the word `'built'` in Problem 6?**
   - **A:** In Basic Lesk, `'built'` matched the adjective sense `built.s.01` (*"used of soaps or cleaning agents..."*) because that long definition shared stopwords with the sentence. POS filtering restricted candidates to verb senses of `build`, eliminating the adjective sense completely.
9. **Q: Why did adding hypernyms and hyponyms in `get_expanded_gloss_words()` improve Lesk?**
   - **A:** Many WordNet glosses are only 3–6 words long (e.g., `build.v.08` is just *"found or ground"*), leading to zero word overlap with the sentence. Adding the definitions and examples of direct hypernyms (parent concepts) and hyponyms (child concepts) expands the vocabulary associated with each sense.
10. **Q: How does your code distinguish the local sentence window (Problem 4) from neighboring sentences (Problem 5)?**
    - **A:** Each line in `wsd_train.txt` contains a 2–4 sentence passage. In `part2_preprocessing.py`, `extract_local_sentence()` extracts only the single sentence containing `tokens[target_index]` (bounded by `.`, `!`, `?`, `;`) for Basic Lesk, whereas Improved Lesk uses `item["tokens"]` across the entire multi-sentence passage.
11. **Q: Why did Naive Bayes jump to `51.00%` F1 on the test set compared to `18.60%` for Improved Lesk?**
    - **A:** Naive Bayes learns directly from the $2,000$ training examples: (1) it learns the true corpus sense priors $\log P(s)$ instead of relying on WordNet's general sense rank, and (2) its $\pm 2$ collocation features (`W_-1`, `W_1`) capture recurring phrases like *"in line with"* or *"keep under review"* that never appear inside dictionary glosses.
12. **Q: Why do we use Laplace ($+1$) smoothing and `math.log()` in `predict_naive_bayes()`?**
    - **A:** Without $+1$ smoothing, any test-sentence word that never co-occurred with a candidate sense in training would have probability $0$, wiping out the entire product. We sum `math.log()` probabilities instead of multiplying raw probabilities to prevent floating-point underflow when combining dozens of context features.
