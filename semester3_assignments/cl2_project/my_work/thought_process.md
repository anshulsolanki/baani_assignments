# Complete Thought Process & Implementation Guide (Phases 3 & 4)

This document walks you through **how to think** when designing and writing the code for our Computational Linguistics 2 project—from the initial problem statement all the way to the final evaluation scripts.

For every module we built, we will walk through five exact questions:
1. **What was our goal?** (What problem are we trying to solve in plain English?)
2. **What technology/method did we choose, and WHY?** (Why this method instead of something else?)
3. **What parameters and design choices did we consider?** (How did we pick the numbers and rules?)
4. **How did we think about writing the code step-by-step?** (If you sat down with a blank `.py` file, what order would you write the functions in?)
5. **What traps and edge cases were we careful of?** (What could go wrong and how did we guard against it?)

---

## 0. The Big Picture: How All the Pieces Fit Together

### What was our overall goal?
In movie reviews, a simple Bag-of-Words model (`M0`) just counts words. Even after your teammate added a sentiment dictionary (`M1`) and negation/intensifier rules (`M2`), two huge linguistic problems remained:

1. **The Pronoun Problem (Solved by `M3` — Anaphora & Salience):**
   Reviewers don't repeat *"the movie"* or *"the director"* in every sentence. They write:
   > *"The director adapted a classic novel. While **it** was a masterpiece, **his** screenplay was shallow."*
   If the computer doesn't know what **"it"** and **"his"** refer to, it doesn't know which opinion words are talking about the main topic of the review versus a random side detail.

2. **The "Although / But" Clause Problem (Solved by `M4` — RST Discourse):**
   Reviewers constantly write sentences with two contrasting halves:
   > *"Although the cinematography was breathtaking, the plot was predictable and tedious."*
   A normal model sees one positive word (*"breathtaking"*) and two negative words (*"predictable"*, *"tedious"*) and treats both clauses as equally important. But in **Rhetorical Structure Theory (RST)**, the *"Although..."* part is just a **Satellite** (a concession the writer is setting aside), while the main clause (*"the plot was predictable and tedious"*) is the **Nucleus** (what the writer actually wants to conclude!).

### Why did we split the code into 8 small modular files?
Nobody wants to read or debug a 1,200-line Python file. If a bug happens in pronoun resolution, you should only have to open `anaphora_salience.py`. If a bug happens in discourse connectives, you only open `rst_discourse.py`. Every file has **one single job** (~120 to 220 lines) and is orchestrated by `main.py`.

---

## 1. Stage 1: Pronominal Anaphora Resolution & Entity Salience (`anaphora_salience.py` — Model M3)

### 1.1 What was our goal?
We wanted to:
1. Find all the **Noun Phrases (NPs)** (people, movies, plots, characters) in each sentence.
2. Link third-person pronouns (`he, him, his, she, her, it, its, they, them, their`) back to the noun phrase they refer to (their **antecedent**).
3. Find out which entities are the **main topics** of the review (the most frequently mentioned entities), and **boost the weight** of sentiment words that describe those main entities.

### 1.2 What technology did we choose, and WHY?
- **Technology Chosen:** NLTK's `RegexpParser` (Context-Free Grammar chunker) + **Binding Theory rules** + **Hobbs-inspired salience scoring** over a **2-sentence window**.
- **Why did we choose this?**
  - In our CL2 course (specifically Assignment 3 on CFGs and Assignment 4 on Anaphora Resolution), we used NLTK POS tags and `RegexpParser` chunking rules along with gender/number agreement and Binding Theory.
  - Our project proposal strictly forbids neural networks or deep learning coreference libraries (like `spaCy` neural coref or `AllenNLP`).
  - `RegexpParser` with the pattern `NP: {<DT|PRP\$>?<JJ.*>*<NN.*>+}` is fast, deterministic, easy to explain in a viva, and runs on 2,000 movie reviews in seconds using only NLTK.

### 1.3 What parameters and design choices did we consider?
When designing `anaphora_salience.py`, we had to decide on four key parameters:
1. **How far back should we look for a pronoun's antecedent? (`2-sentence window`)**
   - *Why 2 sentences?* In English prose, over 90% of third-person pronouns (`he, she, it, they`) refer to an entity in the **same sentence** or the **immediately preceding 1–2 sentences**. If you look back 5 or 10 sentences, you get false matches (cascading errors).
2. **How do we score candidate NPs when more than one noun matches in gender/number?**
   - We gave each candidate NP a simple additive score:
     - **Recency (`-2.0 * sentence_distance`):** Prefer nouns in the current sentence (`dist = 0`) or previous sentence (`dist = 1`).
     - **Subject Preference (`+2.5` if `is_subject`):** In Hobbs' algorithm and Centering Theory, the grammatical **subject** of a sentence is the most likely focus of a pronoun in the next sentence.
     - **Topic Frequency (`+0.5 * count`, capped at `+3.0`) & Core Movie Nouns (`+1.0`):** If an entity like `"movie"` or `"director"` is mentioned many times, pronouns are much more likely to refer to it.
3. **How many entities count as "Topical Entities (Discourse Centers)"? (`top_k = 5`)**
   - A full-length movie review usually revolves around 3 to 5 main things: the *film/movie*, the *director*, the *lead actor/character*, and the *plot/script*.
4. **How much should we boost sentiment words attached to a topical entity? (`SALIENT_ENTITY_BOOST = 1.35`)**
   - If the boost is too huge (e.g., `5.0`), a single positive sentence about the main actor would overpower the entire review. If it's too tiny (e.g., `1.02`), the classifier won't notice it. A **35% boost (`1.35`)** gives topical opinions a clear edge without distorting the rest of the review.

### 1.4 How did we think about writing `anaphora_salience.py` step-by-step?
If you were writing this file from scratch, here is the exact mental order:
- **Step A (Define word lists at the top):** List the pronouns we care about (`PERSONAL_PRONOUNS`, `REFLEXIVE_PRONOUNS`), masculine/feminine word hints (`MASCULINE_WORDS`, `FEMININE_WORDS`), movie nouns (`CORE_MOVIE_NOUNS`), and generic filler nouns to ignore (`STOP_ENTITIES` like *"way"*, *"time"*, *"thing"*).
- **Step B (Write small agreement helper functions):**
  - Write `get_pronoun_category(word)` -> returns `"M"` (he/him), `"F"` (she/her), `"N"` (it/its), or `"P"` (they/them).
  - Write `get_np_category(np_tokens, head_token)` -> checks if the head noun is plural (`NNS`/`NNPS` -> `"P"`), matches male/female lists (`"M"`/`"F"`), is a proper noun (`NNP` -> `"PERSON"`), or is a singular thing (`"N"`).
  - Write `check_agreement(pron_cat, np_cat)` -> returns `True` only if they match!
- **Step C (Write `extract_sentence_nps(sentence)`):** Run `NP_PARSER.parse(pos_pairs)` on the sentence, grab each `NP` subtree, take its last word (`np_tokens[-1]`) as the **head noun** (since in English, the main noun of *"the brilliant young director"* is the last word, *"director"*), and record its position and clause ID.
- **Step D (Write `apply_anaphora(sentences)`):**
  1. Loop over all sentences to extract NPs and count how often each entity appears.
  2. Loop over every pronoun, filter candidates using our 2-sentence window, **Binding Theory**, and **gender/number agreement**, pick the candidate with the highest score, and save `token.entity = best_entity`.
  3. Find the top 5 entities in the review and multiply `token.weight *= 1.35` for every sentiment word in the same clause as a top entity.
- **Step E (Write `anaphora_features(sentences)`):** Summarize the positive and negative sentiment attached to salient entities into normalized dictionary features (`ana_salient_pos_density`, `ana_salient_neg_density`, etc.) so `features_2.py` can feed them to our classifiers.

### 1.5 What traps and edge cases were we careful of?
1. **Trap 1 — Pleonastic (Dummy) "It":**
   In sentences like *"It is obvious that the script failed"* or *"It seems that..."*, the word **"It"** does not refer to any noun! It is a dummy grammatical placeholder. We wrote `is_pleonastic_it()` to check if `"it"` is followed by `is/was/seems + adjective (obvious/clear/true/hard) + that/to` and skip it so we don't falsely link it to the previous sentence's noun.
2. **Trap 2 — Binding Theory Principle A & B:**
   - In *"The actor praised **himself**"*, `"himself"` (reflexive) **must** refer to a noun in the **same sentence** (Principle A).
   - In *"John saw Bill near **him**"*, `"him"` (non-reflexive) cannot refer to the object right next to it in the same clause (`"Bill"`), it refers to the subject (`"John"`) (Principle B).
3. **Trap 3 — Filler Nouns Stealing Pronoun Links:**
   Words like `"way"`, `"time"`, `"fact"`, and `"thing"` are tagged as singular nouns (`NN`), so without a stop-list, `"it"` would constantly resolve to `"way"` or `"time"` instead of `"movie"` or `"plot"`! Putting them in `STOP_ENTITIES` prevented this completely.

---

## 2. Stage 2: Rule-Based RST Discourse Segmentation & Weighting (`rst_discourse.py` — Model M4)

### 2.1 What was our goal?
We wanted to split each sentence into clause-level **Elementary Discourse Units (EDUs)**, detect explicit discourse connectives (like *"although"*, *"but"*, *"however"*, *"therefore"*, *"because"*, *"if"*), label each EDU as a **Nucleus** (core claim) or **Satellite** (concession/background/condition), and weight tokens accordingly ($w_N > 1$, $w_S < 1$).

### 2.2 What technology did we choose, and WHY?
- **Technology Chosen:** Deterministic connective-driven EDU segmentation + POS-based polysemy disambiguation + Mann & Thompson's (1988) Nucleus–Satellite assignment rules.
- **Why did we choose this?**
  - Full document-level RST tree parsers require heavy neural models or slow chart parsers that often guess wrong on long movie review paragraphs.
  - However, **intra-sentential clauses anchored by explicit discourse connectives** (~45 connectives across *Concession*, *Contrast*, *Result*, *Cause*, and *Condition*) have **deterministic Nucleus/Satellite directionality**! For example, an *"although..."* clause is *always* a Satellite, and a *"however, ..."* or *"but ..."* clause is *always* a Nucleus.

### 2.3 What parameters and design choices did we consider?
1. **Choosing the Weights (`NUCLEUS_WEIGHT = 1.5`, `SATELLITE_WEIGHT = 0.5`):**
   - Following Bhatia et al. (2015) (*"Better Document-Level Sentiment Analysis from RST Discourse Parsing"*), a Nucleus clause should receive roughly $3\times$ the relative importance of a conceded Satellite clause ($1.5$ vs. $0.5$).
   - For **Contrast** (`"X, but Y"`), the first clause `X` is slightly downweighted (`CONTRAST_PRE_SATELLITE_WEIGHT = 0.6`) while the counterpoint `Y` is upweighted (`1.5`).
   - For **Cause** (`"X because Y"`), the reason `Y` is still somewhat informative, so it gets a milder satellite weight (`CAUSE_SATELLITE_WEIGHT = 0.75`) rather than `0.5`.
2. **Ordering Multi-Word Connectives Before Single-Word Connectives:**
   - Look at `RST_CONNECTIVES` in `rst_discourse.py`: phrases like `"even though"`, `"in spite of"`, `"on the other hand"`, `"as a result"`, and `"provided that"` are placed **before** single words like `"though"`, `"as"`, or `"so"`.
   - *Why?* Because if we checked single words first, `"even though"` would match on `"though"` one token too late, and `"as a result"` would wrongly match `"as"` (Cause) instead of `"as a result"` (Result)!

### 2.4 How did we think about writing `rst_discourse.py` step-by-step?
- **Step A (List the ~45 connectives by relation):** Group them cleanly into `"Concession"`, `"Contrast"`, `"Result"`, `"Cause"`, and `"Condition"`.
- **Step B (Write `is_valid_discourse_connective()` for polysemy):** Check the POS tags after ambiguous words like `"while"`, `"since"`, and `"as"` before accepting them as discourse markers.
- **Step C (Write `segment_sentence_edus(sentence)`):** Walk through the tokens of a sentence from left to right (`while i < n`). Increment `edu_id` whenever we hit punctuation (`,`, `;`, `:`, `--`) or a discourse connective after the start of the sentence, and record which relation introduced each EDU.
- **Step D (Write `apply_rst(sentences)`):** Apply the 5 nuclearity rules to assign `"Nucleus"` or `"Satellite"` and multiply `tok.weight *= edu["rst_weight"]`.
- **Step E (Write `rst_features(sentences)`):** Calculate the positive and negative polarity densities inside Nucleus EDUs (`rst_nucleus_pos_density`, `rst_nucleus_neg_density`), Satellite EDUs (`rst_satellite_pos_density`, `rst_satellite_neg_density`), and overall weighted polarity (`rst_weighted_pos_density`, `rst_weighted_neg_density`).

### 2.5 What traps and edge cases were we careful of?
1. **Trap 1 — Polysemous Connectives (`"while"` and `"since"`):**
   - *"While"* can mean **Time** (*"While watching the movie, I fell asleep"*) OR **Concession** (*"While the acting is great, the plot is awful"*).
   - How did we tell them apart? If `"while"` is followed by a gerund verb (`VBG` like *"watching"*, *"walking"*) or has no finite verb (`VBD/VBP/VBZ/MD`) in the clause, it is **Temporal**, so `is_valid_discourse_connective()` returns `False` and leaves its weight neutral (`1.0`). Only when `"while"` introduces a finite clause does it become a **Concession Satellite**!
   - Similarly, `"since 1995"` (`"since"` + number `CD` or noun phrase with no verb) is **Temporal**, whereas `"since the script was weak"` (`"since"` + clause with verb) is **Cause**.
2. **Trap 2 — Comma Right Before `"but"` (`"The trailer looked good, but the movie was awful"`):**
   - When the loop sees the comma `,` after `"good"`, it increments `edu_id` from `0` to `1` to start a new EDU. Immediately on the next token, it sees `"but"`. If `"but"` incremented `edu_id` *again* to `2` (or failed to label `edu_id = 1` because `edu_id = 1` was still empty), `"but"` wouldn't attach properly! We specifically handled this in `segment_sentence_edus()` and verified it in `test_phase3_modules.py`.

---

## 3. Stage 3: Connecting Features (`features_2.py`) & From-Scratch Classifiers (`custom_classifiers.py`)

### 3.1 How did we connect `M3` and `M4` into the feature vector?
When we first thought about `features_2.py`, we asked ourselves:
> *"In a movie review, there are ~500 unique Bag-of-Words features (`UNI_...`, `BI_...`). If `M3` and `M4` only add 6 or 10 summary numbers at the end of 500 word counts, will the classifier pay enough attention to them?"*

To make sure both Logistic Regression and Naive Bayes benefit from `M3` and `M4` without distorting the raw Bag-of-Words word counts:
1. **Keep `UNI_` and `BI_` counts clean:** If you directly overwrite `UNI_<word>` counts in a document, L2-regularized Logistic Regression loses its clean unigram decision boundary.
2. **Scale `ana_*` and `rst_*` densities to match word-count range (`scale = 25.0`):** Raw per-word densities are tiny decimals like `0.04`. Multiplying `ana_*` and `rst_*` by `25.0` puts them into the `0.0` to `3.0` range (the exact same numeric range as word counts like `1, 2, 3`), and in `naive_bayes_model.py`, multiplying them by `4.0` puts them on the `100.0` pseudo-count scale alongside `M1` and `M2`. This brought `M4` Logistic Regression up to **88.50% Test Accuracy** (and **91.67%** on the Hard Contrastive-Discourse Subset)!

### 3.2 Why did we also write `custom_classifiers.py`?
In our submitted project proposal (`cl2_finalprojectproposal.pdf`), we stated that we would implement Multinomial Naive Bayes (with add-$k$ smoothing) and L2-regularized Logistic Regression from scratch and verify them with `scikit-learn`.
- Your teammate used `scikit-learn` pipelines in `logistic_regression_model.py` and `naive_bayes_model.py`.
- So that her Phase 2 code stays 100% intact **and** our proposal promise is 100% fulfilled, we kept her `sklearn` classes AND wrote `CustomNaiveBayes` and `CustomLogisticRegression` from scratch in `custom_classifiers.py` using simple Python loops and `math.log` / `math.exp`.

---

## 4. Stage 4: Evaluation, Caching, Hard Subset, Statistical Tests & Error Analysis

### 4.1 The Caching Trick in `evaluate_models.py` (Saving 15+ Minutes!)
- **What problem could arise?**
  We have 2,000 movie reviews (1,600 train + 200 validation + 200 test), and each review is ~700 words long. Running NLTK sentence splitting, word tokenization, POS tagging, and lemmatization takes about 1.5 minutes for 2,000 reviews.
  If we called `extract_features(review, model=m)` separately for `M0`, `M1`, `M2`, `M3`, and `M4`, it would POS-tag all 2,000 reviews **5 separate times**!
- **How we solved it:**
  In `evaluate_models.py`, we wrote `extract_all_models_single_review(review, lexicon)`. It runs `preprocess(review)` **once** per review, and then peels off the `M0`, `M1`, `M2`, `M3`, and `M4` feature dictionaries step-by-step as it applies each layer! Then it saves the extracted features to `saved_models/all_features_cache.pkl` so re-running ablation studies, cross-validation, or error analysis takes **less than 5 seconds**.

### 4.2 Designing the Hard Subset & Ablation Study (`hard_subset_ablation.py`)
- **Why do we need a Hard Subset?**
  Many movie reviews are "easy"—every single sentence is positive, or every single sentence is negative. On those easy reviews, basic Bag-of-Words (`M0`) already gets ~87% accuracy because it doesn't matter which clause is the Nucleus or Satellite when all clauses agree!
- **How did we select the Hard Subset?**
  In `select_hard_subset_indices()`, we scored every test review by:
  1. How many **contrastive/concessive connectives** (`although, though, despite, while, but, however, yet...`) it contains,
  2. How many **third-person pronouns** (`he, she, it, they...`) it contains, and
  3. How **mixed** its positive and negative word counts are (`min(pos, neg) / max(pos, neg)`).
  Taking the top 60 hardest reviews gives us a focused testbed where surface Bag-of-Words struggles and discourse/anaphora modeling shines.

### 4.3 Statistical Significance & 5-Fold Cross-Validation (`statistical_tests_cv.py`)
- **Why statistical tests?**
  On a 200-review test set, each review is `0.5%` accuracy. To prove whether an improvement is statistically meaningful or due to chance, we implemented two standard NLP significance tests from scratch:
  1. **McNemar's Test:** Counts how many reviews Model A got right that Model B got wrong ($b$) versus how many Model B got right that Model A got wrong ($c$), computing $\chi^2 = \frac{(|b - c| - 1)^2}{b + c}$.
  2. **Paired Bootstrap Resampling (1,000 resamples):** Repeatedly samples 200 test reviews with replacement and checks how often the new model beats the baseline.
- **Why 5-Fold Stratified Cross-Validation?**
  Evaluating on all **2,000 reviews** across 5 balanced folds (400 reviews per fold) gives a much more reliable measurement than a single 200-review split.

### 4.4 Qualitative Error Analysis & Feature Weights (`error_analysis.py`)
- Finally, in `error_analysis.py`, we pull out the learned weights $w_j$ from Logistic Regression `M4` and save them to `feature_weights_M4.csv` and `error_analysis_report.md`.
- Why? Because in Computational Linguistics, numbers alone aren't enough—we want to **show** the professor that the classifier learned positive weights for `rst_nucleus_pos_density` and `ana_salient_pos_density`, negative weights for `rst_nucleus_neg_density` and `ana_salient_neg_density`, and show real movie review excerpts where `M4` fixed a prediction error made by `M0`/`M2`!
