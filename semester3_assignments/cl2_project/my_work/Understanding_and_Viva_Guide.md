# Understanding & Viva Preparation Guide — CL2 Course Project

**Project Title:** Sentiment Classification Using Rhetorical Structure Theory (RST) and Compositional Semantics  
**Student:** Baani Solanki (`2025114016`) & Yashaswi Priya (`2025114007`)

---

## 1. Concept & Problem Walkthrough

### 1.1 The Core Linguistic Motivation
Standard Bag-of-Words (`M0`) and raw dictionary lookup (`M1`) treat a movie review as an unordered bag of words where every sentence and clause has weight `1.0`. They fail on three classic linguistic phenomena:
1. **Compositional Semantic Shifters (`M2`):**
   - **Negation Scope:** Words like *"not"*, *"never"*, *"hardly"* invert or shift sentiment polarity up to the next clause boundary (*"not good"* $\rightarrow$ `+1.0 - 1.5 = -0.5`).
   - **Intensifiers & Downtoners:** Words like *"very"* (`1.5x`), *"utterly"* (`1.8x`), *"slightly"* (`0.5x`) scale the polarity of the following opinion word.
   - **Irrealis Modals:** Words like *"would"*, *"could"*, *"should"*, *"might"* indicate hypothetical or counterfactual statements (*"could have been great"*), so polarity is dampened by `IRREALIS_FACTOR = 0.35`.
2. **Pronominal Anaphora & Topical Entity Salience (`M3`):**
   - Reviewers use third-person pronouns (`he, him, his, she, her, it, its, they, them, their`) across sentences to refer back to the film, director, plot, or lead actor.
   - Without resolving pronouns, opinion words in sentences like *"It was a masterpiece, though his screenplay felt rushed"* lose their connection to the review's main topic (**discourse center**).
3. **Rhetorical Structure Theory (`RST`) Nucleus–Satellite Asymmetry (`M4`):**
   - According to Mann & Thompson (1988), multi-clause sentences are organized into a **Nucleus** (the writer's central claim) and a **Satellite** (concession, contrast setup, condition, or background).
   - For example, in *"Although the cinematography was breathtaking [Satellite], the plot was predictable and tedious [Nucleus]"*, upweighting the **Nucleus** ($w_N = 1.5$) and downweighting the **Satellite** ($w_S = 0.5$) ensures the author's true stance dominates.

---

## 2. Step-by-Step Mapping to Functions in the Codebase

| File in `my_work/` | Key Functions | What to Show the TA / Professor |
| :--- | :--- | :--- |
| `preprocess.py` | `preprocess()`, `Token`, `Sentence` | Splits reviews into sentences, runs NLTK `pos_tag` and `WordNetLemmatizer`, and assigns `clause_id` using punctuation and subordinating/coordinating connectives (Line 110). |
| `lexicon_semantics.py` | `build_lexicon()`, `apply_lexicon()`, `lexicon_features()` | Maps positive/negative words to `+1.0` / `-1.0` (checking `token.text.lower()` first and falling back to `token.lemma` at Line 22 so `-ing` adjectives like *"fascinating"* aren't lost) and computes `M1` density features. |
| `compositional_rules.py` | `apply_shifters()`, `shifter_features()` | Applies intensifiers first, clause-bounded negation second (`NEGATION_SHIFT = 1.5`), and irrealis modal dampening third (`IRREALIS_FACTOR = 0.35`), computing `M2` features. |
| `anaphora_salience.py` | `extract_sentence_nps()`, `apply_anaphora()`, `anaphora_features()` | Uses `nltk.RegexpParser` (`NP: {<DT\|PRP\$>?<JJ.*>*<NN.*>+}`) to extract NPs, filters out pleonastic *"it"* (`is_pleonastic_it`), enforces **Binding Theory Principles A & B** and gender/number agreement across a 2-sentence window, and boosts sentiment tokens in clauses mentioning top-5 salient entities (`SALIENT_ENTITY_BOOST = 1.35`). |
| `rst_discourse.py` | `segment_sentence_edus()`, `is_valid_discourse_connective()`, `apply_rst()`, `rst_features()` | Segments sentences into EDUs using punctuation and ~45 connectives across *Concession*, *Contrast*, *Result*, *Cause*, and *Condition*; disambiguates polysemous `"while"` (`VBG` = Temporal vs. finite verb = Concession); assigns Nucleus ($1.5$) and Satellite ($0.5$) weights. |
| `features_2.py` | `bow_features()`, `extract_features()` | Combines unigrams/bigrams (`M0`) with `M1` lexicon, `M2` shifters, `M3` anaphora salience, and `M4` RST discourse features. |
| `custom_classifiers.py` | `CustomNaiveBayes`, `CustomLogisticRegression` | From-scratch Python implementations of Multinomial Naive Bayes (add-$k$ smoothing) and L2-regularized Logistic Regression (stochastic gradient descent), cross-checked against `naive_bayes_model.py` and `logistic_regression_model.py`. |
| `evaluate_models.py`, `hard_subset_ablation.py`, `statistical_tests_cv.py`, `error_analysis.py` | `evaluate_all_models()`, `run_hard_subset_evaluation()`, `run_ablation_study()`, `mcnemar_test()`, `paired_bootstrap_test()`, `run_cross_validation()`, `run_error_analysis()` | Full experimental pipeline producing all CSV tables, 5-fold CV, statistical significance tests, and learned feature weight analysis. |

---

## 3. Likely Viva Questions & Ready-to-Speak Model Answers

### Q1: Why did you use additive negation shifting (`NEGATION_SHIFT = 1.5`) instead of simply multiplying polarity by `-1`?
**Answer:**  
In natural language (as shown by Taboada et al., 2011 in the SO-CAL paper), negating a strong positive word like *"excellent"* (*"not excellent"*) does not mean *"terrible"* (`-1.0`)—it means mildly negative or mediocre. Similarly, *"not bad"* means mildly positive (`+0.5`), not *"excellent"*. On our `-1.0` to `+1.0` lexicon scale, shifting by `1.5` turns `+1.0` (*"good"*) into `-0.5` (*"not good"*) and `-1.0` (*"bad"*) into `+0.5` (*"not bad"*), which captures pragmatically softened negation.

### Q2: Why must intensifiers be applied *before* negation in `compositional_rules.py`?
**Answer:**  
Consider the phrase *"not very good"*. Syntactically, the adverb *"very"* modifies the adjective *"good"* first (`1.0 * 1.5 = +1.5`), and the negator *"not"* scopes over the entire adjective phrase `[very good]` (`1.5 - 1.5 = 0.0` or mildly negative). If we applied negation first (`1.0 - 1.5 = -0.5`) and then multiplied by `"very"` (`-0.5 * 1.5 = -0.75`), *"not very good"* would become more negative than *"not good"*, which is the opposite of what it means in English!

### Q3: How does your Anaphora Resolution module (`anaphora_salience.py`) prevent cascading coreference errors across long reviews?
**Answer:**  
We use four linguistic filters:
1. **Strict 2-sentence window:** We only search the current sentence and the immediately preceding two sentences (`max(0, s_idx - 2)`).
2. **Pleonastic "it" filtering:** `is_pleonastic_it()` skips non-referential dummy *"it"* constructions like *"It is obvious that..."* or *"It seems that..."*.
3. **Binding Theory Principles A & B:** Reflexives (*himself, herself, itself*) must bind within the same sentence, while non-reflexive object pronouns cannot bind to a non-subject NP right next to them in the same clause.
4. **Gender and Number Agreement:** Plural nouns (`NNS/NNPS`) only match `they/them/their`, masculine/feminine nouns match `he/she`, and inanimate singular nouns match `it/its`.

### Q4: How do you disambiguate polysemous discourse markers like *"while"* and *"since"* in `rst_discourse.py`?
**Answer:**  
- The word **"while"** can be **Temporal** (*"While watching the film, I laughed"*) or **Concessive** (*"While the acting was strong, the plot failed"*). In `is_valid_discourse_connective()`, if `"while"` is immediately followed by a gerund participle (`VBG`) or lacks a finite verb (`VBD, VBP, VBZ, MD`) in its clause, we classify it as Temporal (neutral weight `1.0`). Only when `"while"` introduces a finite clause do we treat it as a Concession Satellite ($w_S = 0.5$).
- Similarly, **"since"** followed by a cardinal number (`CD`, e.g., *"since 1995"*) or a noun phrase without a verb is Temporal, whereas *"since"* followed by a finite verb clause is classified as **Cause**.

### Q5: In RST (`rst_discourse.py`), why is the clause after *"although"* a Satellite, whereas the clause after *"but"* or *"however"* is a Nucleus?
**Answer:**  
- **Subordinating Concession (*"Although X, Y"*):** The subordinator *"although"* marks `X` as a conceded background fact (Satellite, $w_S = 0.5$), while the main matrix clause `Y` carries the writer's primary claim (Nucleus, $w_N = 1.5$).
- **Coordinating/Adverbial Contrast (*"X, but Y"* or *"X; however, Y"*):** In English discourse, the first clause `X` sets up an expectation (Satellite, $w_S = 0.6$), and the clause introduced by *"but"* or *"however"* (`Y`) delivers the speaker's actual conclusion or pivot (Nucleus, $w_N = 1.5$).

### Q6: Why did Multinomial Naive Bayes initially ignore `M1` and `M2` features before your correction?
**Answer:**  
Two reasons:
1. Multinomial Naive Bayes models word/feature occurrence counts and requires non-negative numbers ($x_j \ge 0$), so signed net polarity features had been dropped.
2. Length-normalized densities (like `0.02`) are ~50,000 times smaller than the sum of integer Bag-of-Words unigram/bigram counts (~1,200 per review). In the log-likelihood $\sum_j x_j \log P(f_j \mid c)$, multiplying by `0.02` contributes almost zero weight. By adding non-negative excess features (`pos_excess_density`, `neg_excess_density`) and scaling densities to "counts per 100 words" ($\times 100$), Naive Bayes properly weights the linguistic features.

### Q7: Why does the rule-based `SO-CAL` classifier achieve ~70% accuracy while Naive Bayes and Logistic Regression achieve ~87–88%?
**Answer:**  
`SO-CAL` is completely **unsupervised**—it uses only a fixed general-purpose sentiment lexicon without learning from the 1,600 labeled training reviews. In movie reviews, many domain-specific expressions (e.g., *"predictable"*, *"b-movie"*, *"oscar-worthy"*, *"edge of your seat"*) or plot descriptions of horror/war movies contain negative dictionary words (*"war"*, *"kill"*, *"dark"*) even in positive reviews. Supervised classifiers (`Naive Bayes` and `Logistic Regression`) learn domain-specific weights from the training corpus while still benefiting from our linguistic features.

### Q8: Why does `SO-CAL (M4 Anaphora+RST)` show its largest gain (+6.67% accuracy) on the Hard Contrastive-Discourse Subset?
**Answer:**  
The Hard Subset specifically selects reviews containing a high density of contrastive/concessive connectives (*although, however, but, despite, while*) and mixed positive/negative opinion words. On these reviews, unweighted `SO-CAL (M2)` averages positive Satellite words and negative Nucleus words equally and gets confused (`55.0%` accuracy). When `M4` downweights Satellite concessions ($0.5$) and upweights Nucleus claims ($1.5$) and salient entities ($1.35$), accuracy jumps to `61.67%` (`+6.67%`).

### Q9: How do McNemar's test and Paired Bootstrap Resampling work in `statistical_tests_cv.py`?
**Answer:**  
- **McNemar's Test** looks only at the disagreements between two models on the exact same test examples: $b$ (number of reviews Model A got right and Model B got wrong) and $c$ (number of reviews Model A got wrong and Model B got right), computing $\chi^2 = \frac{(|b - c| - 1)^2}{b + c}$.
- **Paired Bootstrap Resampling** draws 1,000 random samples of size $N$ (with replacement) from the test predictions and counts the fraction of times Model B's accuracy exceeds Model A's accuracy.

### Q10: What are the main failure cases (false positives and false negatives) that still remain even in `M4`?
**Answer:**  
From our qualitative inspection in `error_analysis_report.md`:
1. **Plot Synopsis vs. Review Evaluation:** Many movie reviews spend the first 3 paragraphs describing a dark/violent plot (full of negative words in main clauses) before giving a 1-sentence positive verdict at the very end, or vice versa.
2. **Sarcasm and Irony:** Sentences like *"What a brilliant way to waste two hours and \$10"* use positive words (*"brilliant"*) in a Nucleus clause without any explicit negation cue.
3. **Implicit Discourse Relations:** When two clauses contrast without an explicit connective (e.g., *"The trailer promised thrills. I fell asleep in ten minutes."*), connective-based RST segmentation leaves both clauses at neutral weight `1.0`.
