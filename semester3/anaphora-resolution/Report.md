# Assignment Report: Anaphora Resolution

## Problem 1 (10 Marks): Extracting Candidate Noun Phrases using a POS Tagger

### Methodology
Given a discourse segment $d$ and a target pronoun $p$ at character offset $c_p$, we identify all candidate Noun Phrases (NPs) using NLTK's Part-of-Speech (POS) tagger (`nltk.pos_tag_sents`) and a Context-Free Grammar (CFG) chunker (`nltk.RegexpParser`):
1. **Sentence & Word Tokenization**: Each discourse segment is split into sentences using `nltk.sent_tokenize` and into tokens using `nltk.word_tokenize`, recording exact `(start_char, end_char)` character spans for every token.
2. **POS Tagging & CFG Parsing**: Each sentence is tagged with Penn Treebank POS tags and parsed with recursive NP rules:
   - Base NPs: `{<DT>?<JJ.*>*<NNP.*>+}` and `{<DT>?<JJ.*>*<NN|NNS>+}`
   - Nested Possessive and Compound NPs: `{<NP><POS><NP>}` and `{<NP><NP>}`
3. **Antecedent Candidate Extraction**: All non-pronominal `NP` subtrees are extracted along with their character offsets, POS tags, sentence indices, and grammatical role (`is_subject`).

### Results on Test Set (`gap-test.tsv`)
- **Total test discourse segments**: 2,000
- **Total candidate NPs extracted**: 42,597
- **Average candidate NPs per segment**: 21.30

---

## Problem 2 (5 Marks): Random Assignment Baseline (100 Runs)

### Methodology
For each pronoun in `gap-test.tsv`, we randomly select one candidate NP from the extracted candidate NPs using `random.choice`. We repeat this experiment across **100 independent runs** and compute the mean accuracy across all 100 runs. Because the GAP dataset provides ground-truth coreference labels specifically for two named candidate entities (`A` and `B`), we report accuracy under two evaluation settings:
1. **Full POS-Extracted Candidate NP Pool**: Random selection across all POS-extracted NPs in the discourse segment.
2. **GAP Candidate Entities (`A` vs. `B`)**: Random selection between the extracted candidate NPs corresponding to entities `A` and `B`.

### Results
- **Average Accuracy (Full POS-Extracted Candidate NP Pool, 100 runs)**: **7.13%**
- **Average Accuracy (GAP Candidate Entities `A` vs. `B`, 100 runs)**: **44.07%** *(Note: slightly below 50% because ~10% of GAP segments have `A-coref = False` and `B-coref = False`, where neither `A` nor `B` is the true antecedent).*

---

## Problem 3 (5 Marks): Most Recent Antecedent Baseline

### Methodology
For each pronoun in `gap-test.tsv`, we deterministically assign the **most recent candidate NP** immediately preceding the pronoun (`preceding[-1]`) as its antecedent.

### Results
- **Most Recent Antecedent Accuracy (Full POS-Extracted Candidate NP Pool)**: **12.85%** (257 / 2000 segments)
- **Most Recent Antecedent Accuracy (GAP Candidate Entities `A` vs. `B`)**: **40.15%** (803 / 2000 segments)

**Analysis**: Across the full candidate NP pool, selecting the most recent NP nearly doubles accuracy compared to random guessing (`12.85%` vs. `7.13%`), confirming that **recency** is a strong baseline signal. However, when deciding between the two competing named entities `A` and `B`, surface recency (`40.15%`) underperforms random guessing (`44.07%`) because in English clauses (e.g., *"Subject [A] verb Object [B], and he..."*), the earlier grammatical **Subject** (`A`) is more frequently the antecedent than the more recent **Object** (`B`).

---

## Problem 4 (10 Marks): Custom Logistic Regression Classifier

### Model Implementation From Scratch
We implemented a binary Logistic Regression classifier (`SimpleLogisticRegression`) from scratch in pure Python using only `math.exp`:
- **Prediction**: Given a 12-dimensional feature vector $x \in \mathbb{R}^{12}$ for a `(pronoun, candidate_NP)` pair, the probability that the candidate NP is the true antecedent is:
  $$P(y = 1 \mid x) = \sigma(w^\top x + b) = \frac{1}{1 + e^{-(w^\top x + b)}}$$
- **Training Objective & Optimization**: Trained on `gap-development.tsv` (2,000 segments) via **Stochastic Gradient Descent (SGD)** minimizing weighted binary cross-entropy loss with $L_2$ regularization ($\lambda$) and positive class weighting (`pos_weight`) to handle the ~1:20 positive-to-negative candidate NP imbalance.
- **Inference**: For each test segment, the candidate NP with the maximum predicted probability $P(y=1 \mid x)$ (above threshold $0.25$) is selected as the antecedent.

### Feature Representation (12 Linguistic Features)
Following Jurafsky & Martin (Chapter 21), we extract 12 features for each `(pronoun, candidate_NP)` pair:
1. `is_hobbs_top1`: Indicator ($1.0$) if the candidate is ranked #1 by Hobbs' tree traversal.
2. `in_hobbs_top3`: Indicator ($1.0$) if the candidate is ranked in the top 3 by Hobbs' tree traversal.
3. `gender_match`: Indicator ($1.0$) if candidate gender matches pronoun gender.
4. `gender_mismatch`: Indicator ($1.0$) if candidate gender conflicts with pronoun gender.
5. `number_agreement`: Indicator ($1.0$) if candidate head noun is singular (`NN`/`NNP`), matching the singular GAP pronoun.
6. `is_proper_noun`: Indicator ($1.0$) if the candidate NP contains a proper noun (`NNP`/`NNPS`), capturing animacy/personhood for personal pronouns.
7. `grammatical_role_subj`: Indicator ($1.0$) if the candidate NP is in syntactic Subject position (`NP` outside `VP`/`PP` under `S`).
8. `parallel_role`: Indicator ($1.0$) if candidate NP and pronoun share the same grammatical role (Subject-to-Subject or Non-Subject-to-Non-Subject).
9. `recency_inv_rank`: Inverse rank $1 / \text{rank}$ among preceding NPs ($1.0$ for closest NP).
10. `same_sentence`: Indicator ($1.0$) if the candidate NP is in the same sentence as the pronoun.
11. `char_distance_closeness`: Normalized character proximity $1 - \text{dist}/\text{text\_len}$ before the pronoun.
12. `entity_frequency`: Normalized discourse mention count $\min(\text{count}/4, 1.0)$ of the candidate NP across the passage.

### Hyperparameter Tuning & Test Set Results
Tuning on `gap-validation.tsv` (454 segments) over learning rate $\eta \in \{0.01, 0.05, 0.10\}$, $L_2$ regularization $\lambda \in \{0.0, 0.0001, 0.001\}$, and `pos_weight` $\in \{2.0, 4.0\}$ selected $\eta = 0.10, \lambda = 0.001, \text{pos\_weight} = 4.0$.

| Evaluation Setting on `gap-test.tsv` (2,000 segments) | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: |
| **1. Full POS-Extracted Candidate NP Pool** | **40.58%** | **45.57%** | **42.93%** |
| **2. GAP Candidate Entities (`A` vs. `B`)** | **56.65%** | **58.60%** | **57.61%** |

---

## Problem 5 (5 Marks): Learned Feature Weights & Top-5 Features

Ranking all 12 learned weights $w_j$ by absolute magnitude $|w_j|$ (Learned Intercept $b = -6.6300$):

| Rank | Feature Name | Learned Weight ($w_j$) | Linguistic Justification |
| :---: | :--- | :---: | :--- |
| **1** | **`entity_frequency`** | **`+4.5121`** | **Discourse Topicality / Salience**: Repeatedly mentioned entities are the primary discourse topic (backward-looking center in Centering Theory) and are far more likely to be pronominalized. |
| **2** | **`is_proper_noun`** | **`+2.5635`** | **Animacy / Named Entity Filter**: GAP pronouns (`he, she, him, her, his`) refer exclusively to human referents. Proper nouns (`NNP`) strongly separate human names from inanimate common NPs (*"the club"*, *"a contract"*). |
| **3** | **`grammatical_role_subj`** | **`+1.0527`** | **Grammatical Role Hierarchy**: Validates the linguistic salience hierarchy ($\text{Subject} > \text{Object} > \text{Oblique}$); subjects are the default focus of subsequent pronouns. |
| **4** | **`gender_mismatch`** | **`-0.9855`** | **Morphosyntactic Agreement Constraint**: Strongly penalizes candidates whose lexical/gazetteer gender contradicts the pronoun's gender. |
| **5** | **`is_hobbs_top1`** | **`+0.6018`** | **Syntactic Tree Proximity & Binding Constraints**: Rewards the #1 candidate favored by Hobbs' left-to-right breadth-first CFG search (which enforces Binding Condition B and prefers syntactic subjects). |
| 6 | `recency_inv_rank` | `+0.5994` | Surface recency rank boost ($1/\text{rank}$). |
| 7 | `same_sentence` | `+0.5968` | Intra-sentential proximity boost. |
| 8 | `char_distance_closeness` | `+0.5918` | Continuous character closeness boost. |
| 9 | `in_hobbs_top3` | `+0.5723` | Top-3 candidate in Hobbs' CFG tree search. |
| 10 | `parallel_role` | `+0.1476` | Syntactic role parallelism preference. |
| 11 | `gender_match` | `+0.0762` | Small positive weight (since both `A` and `B` in GAP share the same gender). |
| 12 | `number_agreement` | `-0.0315` | Near zero because almost all proper noun candidates are already singular (`NNP`). |

---

## Problem 6 (5 Marks): Error Analysis & How the Algorithm Can Be Improved

### Part A: Major Error Patterns on `gap-test.tsv`
1. **Kinship Semantics & Possessive Nesting (`test-1`)**:
   - *Predicted*: `'Former NHLer Gary Suter'` ($P=0.530$) | *Gold*: `'Dehner'` | *Pronoun*: `'His'`
   - *Explanation*: In *"Former NHLer Gary Suter and Olympic-medalist Bob Suter are Dehner's uncles. His cousin is..."*, *Gary Suter* is the grammatical subject (`grammatical_role_subj = 1`), whereas resolving *"His cousin"* to *Dehner* requires relational reasoning over kinship terms (*uncles* vs. *cousin*).
2. **Local Quoted Speech vs. Global Discourse Topic (`test-4`)**:
   - *Predicted*: `'Marchesano'` ($P=0.823$) | *Gold*: `'Pisciotta'` | *Pronoun*: `'his'`
   - *Explanation*: Inside a direct quotation spoken by *Pisciotta*, *Marchesano* is mentioned twice in close succession right before the pronoun, inflating its `entity_frequency` and `recency_inv_rank` scores, even though the narrative frame returns to the speaker (*Pisciotta*).
3. **Character vs. Actor Parenthetical Apposition (`test-5`, `test-6`)**:
   - *Predicted*: `'William McNamara'` ($P=0.575$) | *Gold*: `'Eddie'` | *Pronoun*: `'his'`
   - *Explanation*: In Wikipedia film synopses (*"Eddie Devane (William McNamara) is a young sailor on his way..."*), the actor's name in parentheses precedes the pronoun more closely and appears earlier in the cast list, causing the model to pick the actor over the character.
4. **Commonsense Event Structure & Selectional Restrictions (`test-8`)**:
   - *Predicted*: `'Sophie'` ($P=0.636$) | *Gold*: `'Jeni'` | *Pronoun*: `'her'`
   - *Explanation*: In *"Jeni is killed when the monster breaks through a window and pulls her in"*, both *Sophie* and *Jeni* are feminine subjects in the discourse; knowing that the person who *"is killed"* is the one whom the monster *"pulls in"* requires verb-event semantics beyond surface syntax.

### Part B: How the Algorithm Can Be Improved
1. **Dependency Parsing for Exact Grammatical Relations**: Replace regex chunking with a syntactic dependency parser to distinguish main-clause subjects (`nsubj`), passive subjects (`nsubjpass`), direct objects (`dobj`), and possessive modifiers (`poss`).
2. **Quotation & Speaker Attribution Tracking**: Detect quotation boundaries so mentions inside direct speech do not override the main narrative speaker outside the quote.
3. **Parenthetical Appositive Filtering**: Identify `Character (Actor)` parenthetical constructions in Wikipedia articles and down-weight parenthetical actor aliases when resolving narrative pronouns.
4. **Entity-Cluster Salience & Selectional Restrictions**: Group coreferent string mentions (e.g., *"Eddie Devane"* and *"Eddie"*) into entity clusters before counting frequency, and incorporate verb-argument selectional preferences.

---

## Problem 7 (10 Marks): Rule-Based Hobbs' Algorithm on CFG Trees

### Methodology
We converted each POS-tagged sentence into a hierarchical Context-Free Grammar (CFG) tree (`ParentedTree`) with parent pointers and implemented the 9-step **Hobbs' Tree Search Algorithm** (Jurafsky & Martin, Section 21.6.1):
1. Begin at the `NP` node dominating the pronoun and climb up to the first `NP` or `S` node ($X$, path $p$).
2. Traverse all branches below $X$ to the left of $p$ in a **left-to-right, breadth-first** order, enforcing **Condition B** (`require_intervening_np_or_s=True`, requiring an intervening `NP` or `S` node between $X$ and the candidate).
3. Climb recursively through higher `NP`/`S` clauses in the current sentence, searching left branches (and right branches without descending into `NP`/`S`).
4. When the root of the current sentence is reached, iterate backwards through prior sentences $s_{t-1}, s_{t-2}, \dots, s_0$, performing left-to-right breadth-first search and selecting the first candidate NP that satisfies gender, number, and person/animacy compatibility.

### Results on Test Set (`gap-test.tsv`)

| Evaluation Setting on `gap-test.tsv` (2,000 segments) | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: |
| **1. Full POS-Extracted Candidate NP Pool** | **30.42%** | **34.29%** | **32.24%** |
| **2. GAP Candidate Entities (`A` vs. `B`)** | **43.46%** | **42.36%** | **42.90%** |

---

## Problem 8 (5 Marks): Comparison of Logistic Regression and Hobbs' Algorithm

### Quantitative Comparison Summary (`gap-test.tsv`)

| Method | Full Candidate NP Pool F1 | GAP (`A`/`B`) Precision | GAP (`A`/`B`) Recall | GAP (`A`/`B`) F1 |
| :--- | :---: | :---: | :---: | :---: |
| **Random Assignment (100 runs)** | 7.13% | 44.07% | 44.07% | 44.07% |
| **Most Recent Antecedent** | 12.85% | 40.15% | 40.15% | 40.15% |
| **Rule-Based Hobbs' Algorithm** | 32.24% | 43.46% | 42.36% | 42.90% |
| **Custom Logistic Regression (Ours)** | **42.93%** | **56.65%** | **58.60%** | **57.61%** |
| *Extra Credit: Scikit-Learn Logistic Regression* | *42.33%* | *55.61%* | *59.22%* | *57.36%* |

### Qualitative Comparison
1. **Why Hobbs' Algorithm Dramatically Beats Simple Baselines (`32.24%` vs. `12.85%` Full-Pool F1)**:
   - Unlike the Most Recent baseline—which blindly chooses the closest noun phrase (often an inanimate object or prepositional complement right before the pronoun)—Hobbs' algorithm searches each clause's CFG tree **left-to-right, breadth-first**, naturally prioritizing higher, left-most syntactic **Subjects** over embedded objects and enforcing **Binding Condition B**.
2. **Why Custom Logistic Regression Outperforms Hobbs' Algorithm (`42.93%` vs. `32.24%` Full-Pool F1; `57.61%` vs. `42.90%` GAP `A`/`B` F1)**:
   - **Discourse-Level Salience**: Hobbs' algorithm is strictly memoryless across sentences: when stepping back to sentence $s_{t-1}$, it picks the first compatible subject in $s_{t-1}$ even if that NP is a minor distractor mentioned only once. Logistic Regression incorporates `entity_frequency` ($w = +4.5121$), tracking the global discourse protagonist across the entire multi-sentence passage.
   - **Multi-Cue Probabilistic Combination**: Hobbs' algorithm makes hard, brittle decisions at each node. In contrast, Logistic Regression softly combines 12 syntactic, morphosyntactic, and discourse signals (including Hobbs' own tree rankings via `is_hobbs_top1` and `in_hobbs_top3`), achieving a **+10.69%** absolute F1 gain on the full NP pool and a **+14.71%** absolute F1 gain on the GAP (`A`/`B`) task.

---

## Extra Credit (10 Marks): Scikit-Learn Logistic Regression Comparison

We trained `scikit-learn`'s `LogisticRegression` (with `L-BFGS` optimization and tuned hyperparameters $C = 0.1, \text{pos\_weight} = 4.0$ on `gap-validation.tsv`) using the exact same 12 features:
- **Full Candidate NP Pool**: Precision = **39.99%**, Recall = **44.95%**, F1 = **42.33%** (vs. **42.93%** for our custom implementation).
- **GAP Candidate Entities (`A` vs. `B`)**: Precision = **55.61%**, Recall = **59.22%**, F1 = **57.36%** (vs. **57.61%** for our custom implementation).
- **Top-5 Learned Weights**: `entity_frequency` (`+4.2958`), `is_proper_noun` (`+2.9008`), `grammatical_role_subj` (`+1.1571`), `recency_inv_rank` (`+0.9065`), and `gender_mismatch` (`-0.7172`).
- **Error Analysis & Comparison vs. Hobbs**: Makes 971 errors on gold-annotated test segments (exhibiting the same 4 error patterns as Custom LR) and outperforms Hobbs' algorithm by **+10.09%** F1 on the full NP pool and **+14.46%** F1 on GAP (`A`/`B`).
