# CL-2 Tutorial 1: WordNet Activity — Solution & Report

## 1. Scope & Problem Breakdown

The assignment asks us to use the **NLTK WordNet** corpus (`nltk.corpus.wordnet`) to complete two main tasks:
1. **Synonym Retrieval Procedure (`nltk_get_synonyms`)**:
   - Write a Python function `nltk_get_synonyms(form, pos=None)` that takes a word form string (e.g., `'dog'`) and an optional part-of-speech tag (e.g., `'n'`), and returns a list of synonym strings across all synsets of that word.
   - **Strict constraints**:
     - The returned elements must be plain strings (word forms), **not** `Synset` or `Lemma` objects.
     - Multi-word expressions stored with underscores in WordNet (like `'Canis_familiaris'`, `'domestic_dog'`, `'hot_dog'`) must have underscores replaced with spaces (`'Canis familiaris'`, `'domestic dog'`, `'hot dog'`).
     - The returned list must contain **no duplicates**.
2. **Answer Four Quantitative Questions about WordNet Nouns**:
   - **Question 1**: How many nouns are there in WordNet?
   - **Question 2**: How many noun synsets are there?
   - **Question 3**: What noun has the largest number of senses (where each synset corresponds to a sense)?
   - **Question 4**: What noun has the largest number of *noun* senses?

---

## 2. Code Architecture

To keep the solution clean, simple, and modular, the code is split across three focused Python files:
- [`synonyms.py`](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut1/synonyms.py): Implements `nltk_get_synonyms(form, pos=None)`.
- [`wordnet_questions.py`](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut1/wordnet_questions.py): Implements `get_all_noun_forms()`, `question_1()`, `question_2()`, `question_3()`, and `question_4()`.
- [`main.py`](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut1/main.py): Imports the functions, verifies `nltk_get_synonyms('dog', 'n')`, and prints the answers to Questions 1–4.

> **Note on NLTK 2 vs. NLTK 3 Compatibility**:
> The handout snippet comes from an older NLTK 2 reference where `synset.lemmas` and `l.name` were attributes. In modern NLTK 3 (`nltk >= 3.0`), these are methods and must be called with parentheses: `synset.lemmas()` and `l.name()`.

---

## 3. Procedure Verification: `nltk_get_synonyms('dog', 'n')`

When `nltk_get_synonyms('dog', 'n')` is called, WordNet looks up all 7 noun synsets containing `'dog'`:
1. `dog.n.01`: `['dog', 'domestic_dog', 'Canis_familiaris']`
2. `frump.n.01`: `['frump', 'dog']`
3. `dog.n.03`: `['dog']`
4. `cad.n.01`: `['cad', 'bounder', 'blackguard', 'dog', 'hound', 'heel']`
5. `frank.n.02`: `['frank', 'frankfurter', 'hotdog', 'hot_dog', 'dog', 'wiener', 'wienerwurst', 'weenie']`
6. `pawl.n.01`: `['pawl', 'detent', 'click', 'dog']`
7. `andiron.n.01`: `['andiron', 'firedog', 'dog', 'dog-iron']`

After replacing `'_'` with `' '` and removing duplicates (since `'dog'` appears in all 7 synsets), our function returns the exact 22 unique strings specified in the handout:

```python
['dog', 'domestic dog', 'Canis familiaris', 'frump', 'cad', 'bounder', 'blackguard', 'hound', 'heel', 'frank', 'frankfurter', 'hotdog', 'hot dog', 'wiener', 'wienerwurst', 'weenie', 'pawl', 'detent', 'click', 'andiron', 'firedog', 'dog-iron']
```

---

## 4. Answers to the Four Questions

### Question 1: How many nouns are there in WordNet?
- **Answer (using the handout code snippet iterating over `wn.all_synsets('n')`)**: **`119,034` nouns**
- **Secondary Answer (using `wn.all_lemma_names('n')`)**: **`117,798` nouns**
- **Explanation**:
  Using the exact loop given in the handout (`for synset in wn.all_synsets('n'): for l in synset.lemmas(): all_noun_forms.add(l.name())`), there are **119,034** unique case-sensitive noun forms in WordNet 3.0.
  If you instead query WordNet's internal lowercase index table via `len(list(wn.all_lemma_names('n')))`, you get **117,798** because WordNet normalizes all index entries to lowercase, merging capitalized proper nouns with their lowercase common-noun counterparts (e.g., `'March'` and `'march'`, `'China'` and `'china'`).

---

### Question 2: How many noun synsets are there?
- **Answer**: **`82,115` noun synsets**
- **Explanation**:
  Iterating through `wn.all_synsets('n')` yields **82,115** distinct noun synsets in WordNet 3.0. Because each synset represents a distinct concept (grouped set of cognitive synonyms), there are 82,115 distinct noun concepts in WordNet.

---

### Question 3: What noun has the largest number of senses [Each synset of a noun corresponds to a sense]?
- **Answer**: **`'break'`** with **`75` senses** (or **`'head'`** with **`33` senses** if restricted strictly to noun senses—see Question 4).
- **Explanation**:
  A word form in `all_noun_forms` can also appear in synsets belonging to other parts of speech (verbs, adjectives, adverbs). When we check `len(wn.synsets(noun))` across **all** parts of speech for every noun in `all_noun_forms`:
  - **`'break'`** has the largest total number of senses: **75 synsets** (`16` noun senses + `59` verb senses).
  - Runner-up: `'cut'` with **70 synsets** (`20` noun + `41` verb + `9` adjective).
  - Third place: `'run'` with **57 synsets** (`16` noun + `41` verb).

---

### Question 4: What noun has the largest number of noun senses?
- **Answer**: **`'head'`** with **`33` noun senses**
- **Explanation**:
  When we restrict the sense lookup strictly to noun synsets using `len(wn.synsets(noun, 'n'))`:
  - **`'head'`** has the largest number of noun senses in WordNet: **33 noun synsets** (ranging from the anatomical upper part of the body `head.n.01`, to intellect `mind.n.01`, leader/chief `head.n.04`, source of a river `fountainhead.n.02`, grammatical head word `head.n.09`, school principal `principal.n.02`, read/write head `read/write_head.n.01`, drumhead `drumhead.n.01`, etc.).
  - Runner-up: `'line'` with **30 noun senses**.
  - Third place: `'point'` with **26 noun senses**.
