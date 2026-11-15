# Corrections Made to Teammate's Work (Phase 1 & Phase 2)

This document explains the small bugs we found in the Phase 1 & Phase 2 code and how we fixed them in `my_work/`. We kept 100% of your teammate's original code and original comments untouched, and only added a `# CORRECTION ...` comment right above the exact lines we fixed.

---

## Correction 1: Fixing the "Not Good" / "Not Bad" Score Scale and Order

### Where it was fixed
- `my_work/config.py` (Line 4)
- `my_work/compositional_rules.py` (Line 35)

### What was happening earlier
In `lexicon_semantics.py`, every positive word (like *"good"* or *"excellent"*) gets a score of **`+1.0`**, and every negative word (like *"bad"* or *"terrible"*) gets a score of **`-1.0`**.

However, in `config.py`, the variable `NEGATION_SHIFT` (how much we subtract or add when we see the word *"not"*) was set to **`4.0`**.
- Why was it `4.0`? Because the reference paper (SO-CAL) scores words from **`-5` to `+5`**. On a `-5` to `+5` scale, subtracting `4` turns *"good"* (`+3`) into *"not good"* (`-1`, slightly negative).
- **The Problem:** Because our dictionary only uses **`-1` to `+1`**, subtracting `4.0` from `+1.0` turned *"not good"* into **`-3.0`**! That meant the code treated *"not good"* (`-3.0`) as **three times worse than *"terrible"* (`-1.0`)**, and treated *"not bad"* (`-1.0 + 4.0 = +3.0`) as **three times better than *"excellent"* (`+1.0`)**!

Also, inside `compositional_rules.py`, two small things were happening in the loop:
1. **Order of "not" and "very":** The code applied *"not"* first and *"very"* second. So in a sentence like *"The movie was not very good"*, `"not"` first changed `"good"` (`+1.0`) to `-3.0`, and then `"very"` multiplied `-3.0` by `1.5` to get **`-4.5`**! In real English, *"not very good"* is milder than *"not good"*, not worse.
2. **Missing `break` after negation:** When the code saw `"not"`, it changed *every* opinion word for the next 6 words instead of stopping after it negated the first opinion word.

### How we fixed it
1. In `config.py` (Line 4), we changed `NEGATION_SHIFT` from `4.0` to **`1.5`**. Now, on our `-1.0` to `+1.0` scale:
   - *"good"* (`+1.0`) -> *"not good"* (`1.0 - 1.5 = -0.5`, mildly negative, less negative than *"terrible"* at `-1.0`).
   - *"bad"* (`-1.0`) -> *"not bad"* (`-1.0 + 1.5 = +0.5`, mildly positive, less positive than *"excellent"* at `+1.0`).
2. In `compositional_rules.py` (Line 35), we applied **intensifiers** (like *"very"*) before **negation** (like *"not"*), and added a `break` so one *"not"* only shifts the opinion word it actually modifies.

---

## Correction 2: Catching "-ing" and "-ed" Opinion Words (like *"fascinating"*, *"charming"*, *"disappointing"*)

### Where it was fixed
- `my_work/lexicon_semantics.py` (Line 7 and Line 22)
- `my_work/socal.py` (Line 24)

### What was happening earlier
In `preprocess.py`, NLTK tags every word as a Noun, Verb, Adjective, etc., and then strips the ending to find its root word (`lemma`).
- Often, NLTK mistakes opinion words ending in `-ing` or `-ed`—such as *"fascinating"*, *"charming"*, *"disappointing"*, or *"boring"*—for **Verbs** instead of **Adjectives**.
- When NLTK thinks *"fascinating"* is a verb, the lemmatizer chops off `-ing` and turns it into `"fascinate"`. Similarly, *"charming"* becomes `"charm"`, and *"disappointing"* becomes `"disappoint"`.
- **The Problem:** In `lexicon_semantics.py`, `apply_lexicon()` only looked up `token.lemma` (the chopped root word). Because the sentiment dictionary stores `"fascinating"` rather than `"fascinate"`, the lookup returned **`0.0`**—meaning those opinion words were completely skipped!
- *(Also, `build_lexicon()` did not call `ensure_nltk()` before reading the NLTK dictionary, which caused an error if `build_lexicon()` was run before `preprocess()`).*

### How we fixed it
In `apply_lexicon()` (Line 22) and `socal.py` (Line 24), we check `lexicon.get(token.text.lower(), lexicon.get(token.lemma, 0.0))` so it checks the exact lowercase word first and falls back to the root word (`token.lemma`). We also called `ensure_nltk()` at the start of `build_lexicon()` (Line 7).

---

## Correction 3: Stopping "Not" in One Sentence from Flipping Words in the Next Sentence in `socal.py`

### Where it was fixed
- `my_work/socal.py` (Line 33 and Line 44)

### What was happening earlier
In `socal.py`, the `score_review()` function flattened all the sentences of a review into one giant list of words (`tokens = flatten(sentences)`) and looked backward 6 words (`range(max(0, i - 6), i)`) whenever it saw a positive or negative word.
- **The Problem:** It never checked whether those previous 6 words were in the **same sentence (`sent_id`)** or the **same clause (`clause_id`)**!
- For example, in:
  > *"I did **not** wait. **Excellent** acting!"*
  Because `"Excellent"` is only 3 words after `"not"`, `socal.py` jumped right over the period `.` and flipped `"Excellent"` from `+1.0` to `-1.0`!

### How we fixed it
Inside the negation loop (Line 33) and intensifier loop (Line 44) in `socal.py`, we added:
`if previous.sent_id != token.sent_id or previous.clause_id != token.clause_id: continue`
so negation and intensifiers stay inside their own sentence and clause.

---

## Correction 4: Why Naive Bayes Gave the Exact Same Accuracy (`0.855`) on M0, M1, and M2

### Where it was fixed
- `my_work/lexicon_semantics.py` (Line 48)
- `my_work/compositional_rules.py` (Line 123)
- `my_work/naive_bayes_model.py` (Line 15)

### What was happening earlier
If you look at `phase2_final_comparison.csv`, Naive Bayes had the **exact same accuracy (`0.855`), precision (`0.838`), recall (`0.88`), and F1 (`0.8585`)** for `M0`, `M1`, and `M2`. In your teammate's Kaggle notebook, when she checked how many test reviews changed their prediction between `M1` and `M2`, the output was **`Different predictions: 0`**.

Why was Naive Bayes completely ignoring the `M1` and `M2` features? Two reasons:
1. **Negative numbers aren't allowed in Multinomial Naive Bayes:** Multinomial Naive Bayes works by counting how many times a feature appears, so it crashes if any feature is negative. Because overall polarity (`lex_polarity_density` and `shift_density`) can be negative, your teammate wrote a function in the notebook that **deleted** those features before giving the data to Naive Bayes.
2. **Tiny decimals vs. huge whole numbers:** For the remaining `M1` and `M2` features, she divided them by the total number of words in the review (~700 words), which turned them into tiny decimals like **`0.02`** or **`0.03`**. Meanwhile, the Bag-of-Words features (`UNI_movie`, `UNI_good`, etc.) are whole-number word counts (`1, 2, 5, 15...`) that add up to **over 1,000** in a review. When Naive Bayes adds `0.02` on top of `1,000+` word counts, `0.02` is so tiny that Naive Bayes ignores it!

### How we fixed it
1. In `lexicon_semantics.py` (Line 48) and `compositional_rules.py` (Line 123), we added two non-negative features (`pos_excess_density` and `neg_excess_density`) that record how much positive outweighs negative (or vice versa) without ever using a negative number.
2. Inside `naive_bayes_model.py` (Line 15), we added `_prepare_nb_features()` to filter out negative features and multiply the density features by `100.0` (converting "fraction per word" like `0.03` into "count per 100 words" = `3.0`). Now the `M1` and `M2` features are on the same number scale as normal word counts, so Naive Bayes actually uses them!

---

## Correction 5: Adding Missing Clause-Boundary Words in `preprocess.py`

### Where it was fixed
- `my_work/preprocess.py` (Line 110)

### What was happening earlier
In `preprocess.py`, a new clause (`clause_id += 1`) was only started when the code saw `"but"`, `"yet"`, `"however"`, or punctuation (`","`, `";"`, `":"`).
- **The Problem:** If a writer didn't put a comma before a connecting word—like in *"The movie was not good **because** the plot was rushed"* or *"It was not bad **although** it was long"*—the code treated the whole sentence as one single clause, so `"not"` could reach across `"because"` or `"although"`.

### How we fixed it
In `preprocess.py` (Line 110), we added `"although"`, `"though"`, `"while"`, `"whereas"`, `"because"`, `"since"`, `"if"`, `"unless"`, and `"despite"` to the clause-boundary set.
