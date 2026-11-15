# Understanding & Viva Preparation Guide: CL-2 Tutorial 1 (WordNet in NLTK)

---

## 1. Concept & Problem Walkthrough ("What & Why Before How")

### What are we trying to do, and why?
In natural language processing, words are **ambiguous** (one word like `"dog"` or `"head"` can mean many different things, called **polysemy**) and **redundant** (many different words like `"frankfurter"`, `"wiener"`, and `"hot dog"` can refer to the exact same concept, called **synonymy**).

**WordNet** is a lexical database of English that organizes words by **meaning** rather than spelling. The core building block of WordNet is a **Synset** (short for *synonym set*):
- A **Synset** represents a single distinct **concept** or **sense** (e.g., `frank.n.02` is the concept of a smooth-textured sausage).
- Inside each Synset are **Lemmas**, which are the specific word forms that express that concept in that specific sense (e.g., `frank`, `frankfurter`, `hotdog`, `hot_dog`, `dog`, `wiener`, `wienerwurst`, `weenie`).

In this tutorial, we write code to:
1. Find all synonyms of a given word form (across all of its senses) and return them as clean strings without duplicates.
2. Explore the macro-structure of WordNet's noun vocabulary: how many unique noun strings exist, how many distinct noun concepts (synsets) exist, and which nouns are the most polysemous (have the most senses overall vs. the most noun senses).

---

## 2. Step-by-Step Code Walkthrough ("What to Show the TA")

### File 1: [`synonyms.py`](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut1/synonyms.py)
- **Function `nltk_get_synonyms(form, pos=None)` ([Lines 9–39](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut1/synonyms.py#L9-L39))**:
  1. **Line 19**: Replaces spaces with underscores (`lookup_form = form.replace(' ', '_')`) so multi-word inputs work properly with WordNet.
  2. **Lines 22–25**: Calls `wn.synsets(lookup_form, pos=pos)` to get all synsets (senses) of the word for the requested part of speech. For `('dog', 'n')`, this returns 7 `Synset` objects (`dog.n.01`, `frump.n.01`, `dog.n.03`, `cad.n.01`, `frank.n.02`, `pawl.n.01`, `andiron.n.01`).
  3. **Lines 30–37**: Loops over each `synset` and each `lemma` in `synset.lemmas()`.
     - Calls `lemma.name().replace('_', ' ')` (Line 33) so we extract a **plain Python string** (not a `Synset` or `Lemma` object) and convert WordNet's internal underscores (`'Canis_familiaris'`, `'hot_dog'`) into normal spaces (`'Canis familiaris'`, `'hot dog'`), matching the handout's sample output.
     - Checks `if word_form not in synonyms:` (Line 36) before appending so that `'dog'` (which is in all 7 synsets) is added only once, guaranteeing **zero duplicates** while preserving synset order.

### File 2: [`wordnet_questions.py`](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut1/wordnet_questions.py)
- **Function `get_all_noun_forms()` ([Lines 10–21](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut1/wordnet_questions.py#L10-L21))**:
  - Directly implements the handout's code snippet: iterates over `wn.all_synsets('n')`, then over `synset.lemmas()`, and adds `l.name()` to a Python `set()`.
  - **Key pointer for the TA**: Point out that the handout's snippet (`synset.lemmas` and `l.name` without parentheses) was written for **NLTK 2**. In **NLTK 3**, `.lemmas()` and `.name()` are methods, so we add `()`.
- **Function `question_1()` ([Lines 24–36](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut1/wordnet_questions.py#L24-L36))**:
  - Computes `len(all_noun_forms)` = **`119,034`** (and also shows `len(list(wn.all_lemma_names('n')))` = **`117,798`**).
- **Function `question_2()` ([Lines 39–46](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut1/wordnet_questions.py#L39-L46))**:
  - Computes `len(list(wn.all_synsets('n')))` = **`82,115`**.
- **Function `question_3()` ([Lines 49–71](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut1/wordnet_questions.py#L49-L71))**:
  - Loops over every noun in `all_noun_forms` and checks `len(wn.synsets(noun))` (without a POS filter, counting senses across all parts of speech). Finds **`'break'`** with **`75`** senses.
- **Function `question_4()` ([Lines 74–95](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut1/wordnet_questions.py#L74-L95))**:
  - Loops over every noun in `all_noun_forms` and checks `len(wn.synsets(noun, 'n'))` (restricting strictly to noun synsets). Finds **`'head'`** with **`33`** noun senses.

### File 3: [`main.py`](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut1/main.py)
- Orchestrates the entire execution cleanly in sequence and verifies that `nltk_get_synonyms('dog', 'n')` matches the handout's 22 expected strings.

---

## 3. Likely Viva Questions & Model Answers

### Q1: What is the difference between a `Synset`, a `Lemma`, and a word form (`str`) in NLTK WordNet?
- **Answer**:
  - A **`Synset`** (e.g., `Synset('dog.n.01')`) represents an abstract **concept or sense** shared by a group of synonymous words.
  - A **`Lemma`** (e.g., `Lemma('dog.n.01.domestic_dog')`) represents a **specific word paired with a specific sense**. Even if the string `'dog'` is the same, `Lemma('dog.n.01.dog')` and `Lemma('frump.n.01.dog')` are two distinct `Lemma` objects because they belong to different synsets.
  - A **word form** (e.g., `'dog'` or `'domestic dog'`) is just the plain surface string obtained by calling `lemma.name()`.

### Q2: Why did the code snippet at the bottom of the assignment PDF (`for l in synset.lemmas: all_noun_forms.add(l.name)`) raise a `TypeError` if run directly in modern Python/NLTK?
- **Answer**:
  That snippet was written for **NLTK 2**, where `.lemmas` and `.name` were Python properties/attributes. Starting in **NLTK 3**, the WordNet corpus reader changed them into methods: `synset.lemmas()` and `l.name()`. Calling `for l in synset.lemmas:` without parentheses tries to iterate over a `method` object, raising `TypeError: 'method' object is not iterable`.

### Q3: Why does `nltk_get_synonyms('dog', 'n')` need `.replace('_', ' ')` on `lemma.name()`?
- **Answer**:
  Inside WordNet's database files, multi-word expressions (collocations) are stored with underscores connecting the tokens, such as `'Canis_familiaris'`, `'domestic_dog'`, and `'hot_dog'`. The expected output in the assignment prompt requires natural space-separated strings (`'Canis familiaris'`, `'domestic dog'`, `'hot dog'`), so we replace `'_'` with `' '`.

### Q4: Why would duplicates appear in `nltk_get_synonyms('dog', 'n')` if we didn't filter them out?
- **Answer**:
  Because the query word `'dog'` itself is a member of all **7** noun synsets returned by `wn.synsets('dog', 'n')`. When we iterate over every lemma in all 7 synsets, `'dog'` is encountered 7 times. Checking `if word_form not in synonyms:` (or using a `set`) ensures `'dog'` only appears once in the returned list.

### Q5: Why is there a difference between the number of nouns from the handout's loop (`119,034`) and `len(list(wn.all_lemma_names('n')))` (`117,798`)?
- **Answer**:
  When we iterate over `synset.lemmas()` and collect `l.name()`, the strings preserve their original **case sensitivity** (e.g., `'March'` the month vs. `'march'` the walking pace). In contrast, `wn.all_lemma_names('n')` reads from WordNet's internal lookup index, which normalizes all lemma names to **lowercase**, collapsing pairs that only differ by capitalization into a single entry.

### Q6: Why are there more nouns (`119,034`) than noun synsets (`82,115`)?
- **Answer**:
  A single synset often contains multiple synonymous lemmas (for example, `frank.n.02` contains 8 different noun forms: `'frank'`, `'frankfurter'`, `'hotdog'`, `'hot_dog'`, `'dog'`, `'wiener'`, `'wienerwurst'`, `'weenie'`). Even though many words are polysemous (belonging to multiple synsets), on average each noun synset contains about $1.78$ lemmas, so the total vocabulary of unique noun strings (`119,034`) is larger than the number of distinct noun concepts (`82,115`).

### Q7: What is the difference between Question 3 and Question 4?
- **Answer**:
  - **Question 3** asks: *"What noun has the largest number of senses?"* Many English words that are nouns also function as verbs or adjectives (zero-derivation / conversion). If we take every word in the set of nouns and count **all** of its senses across all parts of speech via `wn.synsets(noun)`, the word **`'break'`** wins with **75 senses** (16 noun senses + 59 verb senses).
  - **Question 4** asks: *"What noun has the largest number of **noun** senses?"* Here we restrict the sense count strictly to `pos='n'` via `wn.synsets(noun, 'n')`. The word **`'head'`** wins with **33 noun senses**.

### Q8: Why does `'dog.n.03'` only have `'dog'` in its lemma list (`['dog']`)? Doesn't a "synonym set" need at least two words?
- **Answer**:
  No! A synset represents a **distinct concept/sense**, not necessarily a group of multiple words. `dog.n.03` represents the informal sense *"informal term for a man; 'you lucky dog'"*. In English, no other single word is an exact cognitive synonym for `"dog"` in that specific expression, so `dog.n.03` is a singleton synset with only 1 lemma (`'dog'`).

### Q9: What happens if you call `nltk_get_synonyms('dogs', 'n')` on a plural form?
- **Answer**:
  `wn.synsets('dogs', 'n')` automatically runs WordNet's built-in morphological analyzer (**Morphy**), which strips the plural suffix `-s`, maps `'dogs'` to the base lemma `'dog'`, and returns the exact same 7 noun synsets and 22 synonyms!

### Q10: Why did we use a list with `if word_form not in synonyms:` instead of just `list(set(...))` in `nltk_get_synonyms`?
- **Answer**:
  A Python `set` is unordered, so converting a `set` to a `list` scrambles the order of the synonyms across runs (because Python randomizes string hash seeds). By appending to a list with `if word_form not in synonyms:`, we guarantee zero duplicates **and** preserve the deterministic order of WordNet's synsets (from the most frequent sense `dog.n.01` down to `andiron.n.01`). Since a word has at most a few dozen synonyms, checking `not in synonyms` takes microseconds.
