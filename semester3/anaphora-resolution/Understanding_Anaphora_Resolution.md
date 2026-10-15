# Understanding Anaphora Resolution: A Complete Step-by-Step Guide

This guide explains the concepts, algorithms, and exact Python implementation in [anaphora_resolution.py](file:///Users/solankianshul/Documents/projects/temp_work/baani_work/assignments/semester3/anaphora-resolution/anaphora_resolution.py) for your **Anaphora Resolution** assignment (based on Jurafsky & Martin, *Speech and Language Processing*, 2nd Edition, Chapter 21).

Everything in **Problems 1–8** is written in **plain, straightforward Python** using only Python's standard library (`csv`, `math`, `random`, `os`) and `nltk`—with **our own implementation of a simple Logistic Regression classifier from scratch** (`SimpleLogisticRegression`).

---

## 1. What is Anaphora Resolution & The GAP Dataset?

### What is Anaphora?
In natural language, speakers avoid repeating the same noun phrase over and over by using **pronouns** (called **anaphors**) such as *he, she, him, her, his, hers*. The noun phrase that a pronoun refers back to is called its **antecedent**.
- **Example**: *"When **Dehner** left Finland, **he** signed a contract in Germany."*
  - **Pronoun (Anaphor)**: *he*
  - **Antecedent**: *Dehner*
  - Finding which noun phrase (NP) is the true antecedent of a pronoun is called **Pronominal Anaphora Resolution**.

### How the GAP Dataset Works
The **Google GAP (Gender-Balanced Coreference) Dataset** contains 4,454 Wikipedia passages ("discourse segments"):
- **Training set (`data/gap-development.tsv`)**: 2,000 segments
- **Development/Validation set (`data/gap-validation.tsv`)**: 454 segments (used to tune hyperparameters)
- **Test set (`data/gap-test.tsv`)**: 2,000 segments (used for final evaluation)

Each row in the `.tsv` file gives us:
1. `Text`: A short multi-sentence passage from Wikipedia.
2. `Pronoun` and `Pronoun-offset`: The target singular personal/possessive pronoun (`he`, `him`, `his`, `she`, `her`, `hers`) and its exact character index in `Text`.
3. `A`, `A-offset`, `A-coref`: The first candidate person named in the passage, its character offset, and whether it is the true antecedent (`TRUE` or `FALSE`).
4. `B`, `B-offset`, `B-coref`: The second candidate person named in the passage, its character offset, and whether it is the true antecedent (`TRUE` or `FALSE`).

> **Why we report two metrics in every problem**:
> When we extract **all** Noun Phrases (NPs) from a passage using an NLTK Part-of-Speech (POS) tagger, a single passage has around **21 candidate NPs** on average (e.g., *"the country"*, *"the clan"*, *"Ali Aladhadh"*, *"Saddam"*). However, GAP only tells us ground-truth `TRUE`/`FALSE` labels for two specific mentions (`A` and `B`). Therefore, our code evaluates every method in two ways:
> 1. **Full Candidate NP Pool (All POS-Extracted NPs)**: Choosing among all ~21 NPs extracted in the segment.
> 2. **GAP Candidate Entities (`A` vs. `B`)**: Choosing between the candidate NPs corresponding to `A` and `B`.

---

## 2. How Each Problem is Implemented

### Problem 1 (10 Marks): Extracting Candidate Noun Phrases using a POS Tagger

#### Goal
For each discourse segment in the test set, extract all the candidate noun phrases (NPs) that can potentially serve as the antecedent of the given pronoun using a standard POS tagger.

#### How We Implemented It (`process_dataset` and `run_problem_1`)
1. **Sentence & Word Tokenization with Character Offsets**:
   - In GAP, the pronoun and gold antecedents are identified by their **character offset** (e.g., character position `383`).
   - In `process_dataset(rows, split_name)`, we use `nltk.sent_tokenize(text)` to split the passage into sentences and `nltk.word_tokenize(s)` to split each sentence into words, while tracking the exact `(start_char, end_char)` index of every word in the original passage (`tok_spans`).
2. **POS Tagging**:
   - We run `nltk.pos_tag_sents(all_tokenized_sents)` across all tokenized sentences. Every word receives a Penn Treebank POS tag:
     - `NNP` / `NNPS`: Proper nouns (e.g., *Dehner*, *Jennifer Keller*)
     - `NN` / `NNS`: Common nouns (e.g., *contract*, *uncles*)
     - `DT`: Determiner (e.g., *the*, *a*)
     - `JJ`: Adjective (e.g., *German*, *pregnant*)
     - `PRP` / `PRP$`: Personal or possessive pronoun (e.g., *he*, *his*, *her*)
3. **Chunking / CFG Parsing into Noun Phrases (`NP`)**:
   - We use `nltk.RegexpParser` (`CFG_PARSER`) with a Context-Free Grammar (`CFG_GRAMMAR`) to group POS-tagged words into Noun Phrases (`NP`), Prepositional Phrases (`PP`), Verb Phrases (`VP`), and Clauses (`S`, `SBAR`):
     ```python
     CFG_GRAMMAR = r"""
       NP: {<DT>?<JJ.*>*<NNP.*>+}
           {<DT>?<JJ.*>*<NN|NNS>+}
           {<PRP.*>}
       NP: {<NP><POS><NP>}
           {<NP><NP>}
       PP: {<IN|TO><NP>}
       VP: {<MD|RB.*>*<VB.*>+<RB.*>*<NP|PP>*}
       S:  {<NP><CC><NP><VP>}
           {<NP><RB.*>?<VP>}
       SBAR: {<IN|WDT|WP|WRB><S>}
     """
     ```
   - Notice the recursive `NP` rule `{<NP><POS><NP>}`. Why is this important? Because in English, a possessive phrase like *"Dehner's uncles"* has an inner base NP (*"Dehner"*) and another base NP (*"uncles"*), grouped under an outer `NP` (*"Dehner's uncles"*). Our tree walker `annotate_tree(node)` labels every base NP with a unique ID (`NP#0`, `NP#1`, ...) and records whether it appears in a **Subject** position (outside `VP`/`PP`) or a **Non-Subject** position (inside `VP`/`PP`).
4. **Filtering Non-Pronominal Candidate NPs**:
   - Every non-pronominal `NP` in the segment is added to `candidate_nps` along with its character span, words, POS tags, sentence index, and grammatical role (`is_subject`).

#### Problem 1 Results
- Across the 2,000 test segments (`gap-test.tsv`), our POS tagger + CFG parser extracted **42,597 candidate NPs**, or an average of **21.30 candidate NPs per segment**.

---

### Problem 2 (5 Marks): Random Assignment Baseline (100 Runs)

#### Goal
Randomly assign an antecedent to the pronoun from the candidate NPs extracted in Problem 1, repeat for 100 runs, and calculate the average accuracy on the test set (`gap-test.tsv`).

#### How We Implemented It (`run_problem_2`)
- We loop `for _ in range(100):` (using `random.Random(12345)` for exact reproducibility).
- In each run, for every test segment:
  1. We use `rng.choice(cands)` to pick one random NP from all POS-extracted candidate NPs, and check if `chosen["is_antecedent"]` is `True`.
  2. We also pick randomly between the candidate NPs matching GAP entities `A` and `B` (`ab_cands`).
- Finally, we average the accuracy across all 100 runs.

#### Problem 2 Results
- **All POS-Extracted Candidate NPs Pool**: **7.13%** average accuracy (since there are ~21 NPs per passage, random guessing succeeds roughly $1/15$ to $1/21$ of the time).
- **GAP Candidates (`A` vs. `B`)**: **44.07%** average accuracy (slightly under 50% because ~10% of GAP test segments have `A-coref = False` and `B-coref = False`, meaning neither `A` nor `B` is the true antecedent).

---

### Problem 3 (5 Marks): Most Recent Antecedent Baseline

#### Goal
Select the **most recent candidate NP** preceding the pronoun and compute accuracy on the test set.

#### How We Implemented It (`run_problem_3`)
- Since `seg["candidates"]` is sorted in order of appearance in the text, we filter for candidates preceding the pronoun (`preceding = [c for c in seg["candidates"] if c["start"] < p_off]`) and select the last element: `most_recent = preceding[-1]`.
- Similarly, for the GAP `A` vs. `B` evaluation, we pick the most recent candidate among `A` and `B` preceding the pronoun (`preceding_ab[-1]`).

#### Problem 3 Results
- **All POS-Extracted Candidate NPs Pool**: **12.85%** accuracy (`257 / 2000` segments).
  - *Why it beats Random*: Simply choosing the closest preceding NP nearly **doubles** accuracy over random guessing (`12.85%` vs. `7.13%`), proving that **recency** is an important linguistic signal.
- **GAP Candidates (`A` vs. `B`)**: **40.15%** accuracy (`803 / 2000` segments).
  - *Interesting insight*: Why is Most Recent (`40.15%`) slightly worse than Random (`44.07%`) when choosing between `A` and `B`? Because in English sentences like *"Dehner (A) signed a contract with Wolfsburg (B), and **he** scored 10 goals"*, the **Subject** (`A`, earlier in the sentence) is more likely to be the antecedent than the **Object** (`B`, more recent in the sentence)! Pure surface recency gets tricked by objects and prepositional phrases.

---

### Problem 4 (10 Marks): Your Own Implementation of a Simple Logistic Regression Classifier

#### Goal
Build a **custom Logistic Regression classifier from scratch** (using only basic Python and `math.exp`), extract features from the candidate NPs (including parse-tree features from Hobbs' algorithm), learn feature weights from the training data (`gap-development.tsv`), tune hyperparameters on the development set (`gap-validation.tsv`), and report **Precision, Recall, and F-score** on the test set (`gap-test.tsv`).

#### Step 4A: Linguistic Features Extracted (`extract_features_for_segment`)
For every `(pronoun, candidate_NP)` pair, we extract **12 interpretable linguistic features** (`FEATURE_NAMES`) grounded in Jurafsky & Martin (Section 21.4):

| # | Feature Name | What It Measures (Linguistic Intuition) |
| :--- | :--- | :--- |
| 1 | `is_hobbs_top1` | `1.0` if the candidate NP is the #1 choice of Hobbs' syntactic tree search algorithm on the CFG parse tree. |
| 2 | `in_hobbs_top3` | `1.0` if the candidate NP is in the top 3 choices of Hobbs' tree search algorithm. |
| 3 | `gender_match` | `1.0` if the candidate NP's inferred gender (from titles like *Mr./Mrs./Lord/Lady*, common first names, or gendered nouns like *sister/father*) matches the pronoun's gender (`M` vs. `F`). |
| 4 | `gender_mismatch` | `1.0` if the candidate NP's inferred gender **conflicts** with the pronoun's gender (agreement violation filter). |
| 5 | `number_agreement` | `1.0` if the candidate NP's head noun is singular (`NN`/`NNP`) matching the singular GAP pronoun, `0.0` if plural (`NNS`/`NNPS`). |
| 6 | `is_proper_noun` | `1.0` if the NP contains a proper noun tag (`NNP` / `NNPS`). Personal pronouns (`he`/`she`) refer to animate/human entities, which are usually named entities. |
| 7 | `grammatical_role_subj` | `1.0` if the candidate NP is in syntactic Subject position (outside `VP`/`PP` under `S`). Captures the **Grammatical Role Hierarchy** (Subject > Object > Oblique). |
| 8 | `parallel_role` | `1.0` if both the candidate NP and the pronoun share the same grammatical role (both Subject or both Non-Subject). Captures **Syntactic Parallelism**. |
| 9 | `recency_inv_rank` | $\frac{1}{\text{rank}}$ where rank $1$ is the closest NP before the pronoun, rank $2$ is second closest, etc. Captures **Recency**. |
| 10 | `same_sentence` | `1.0` if the candidate NP is in the same sentence as the pronoun, else `0.0`. |
| 11 | `char_distance_closeness` | $1 - \frac{\text{char\_dist}}{\text{text\_len}}$ before the pronoun. Continuous character proximity to the pronoun. |
| 12 | `entity_frequency` | $\min(\frac{\text{count}}{4.0}, 1.0)$. How many times the candidate NP string is mentioned in the passage. Captures **Discourse Topicality / Salience**. |

#### Step 4B: How Our Custom `SimpleLogisticRegression` Works From Scratch
Instead of importing an external ML library, we wrote `class SimpleLogisticRegression` in ~55 lines of plain Python:

1. **Linear Score (`predict_proba_one`)**:
   For a feature vector $x = [x_1, x_2, \dots, x_{12}]$, we compute the dot product with learned weights $w = [w_1, w_2, \dots, w_{12}]$ plus bias $b$:
   $$z = b + \sum_{j=1}^{12} w_j x_j$$

2. **Sigmoid Activation Function (`sigmoid`)**:
   Maps $z \in (-\infty, +\infty)$ to a valid probability $\hat{y} \in (0, 1)$:
   $$\hat{y} = P(y = 1 \mid x) = \sigma(z) = \frac{1}{1 + e^{-z}}$$
   *(We clamp $z$ to $[-30, 30]$ so `math.exp(-z)` never overflows).*

3. **Stochastic Gradient Descent (SGD) Training (`fit`)**:
   For each training example $(x^{(i)}, y^{(i)})$ where $y^{(i)} \in \{0, 1\}$:
   - Compute prediction: $\hat{y}^{(i)} = \sigma(w \cdot x^{(i)} + b)$
   - Compute prediction error: $\text{weighted\_err} = (\hat{y}^{(i)} - y^{(i)}) \times \text{sample\_w}$
     - Why `pos_weight`? Because out of ~21 candidate NPs in a segment, only **1** is the true antecedent ($y=1$) and **20** are negative ($y=0$). Weighting positive examples by `pos_weight` (e.g., `4.0`) prevents the classifier from ignoring positive examples!
   - Update each weight $w_j$ and bias $b$ in the opposite direction of the gradient (with L2 regularization $\lambda$):
     $$w_j \leftarrow w_j - \eta \cdot \left(\text{weighted\_err} \cdot x_j^{(i)} + \lambda w_j\right)$$
     $$b \leftarrow b - \eta \cdot \text{weighted\_err}$$

4. **Inference & Evaluation (`evaluate_model_predictions`)**:
   During evaluation, for a given pronoun, our classifier computes $P(y=1 \mid x)$ for every candidate NP and selects the candidate NP with the **highest probability** (above threshold `0.25`).
   - **Precision ($P$)**: $\frac{TP}{TP + FP}$ (fraction of predicted antecedents that are correct).
   - **Recall ($R$)**: $\frac{TP}{TP + FN}$ (fraction of gold-annotated pronouns that are resolved to the correct antecedent).
   - **F1-Score ($F_1$)**: $\frac{2 \cdot P \cdot R}{P + R}$ (harmonic mean of Precision and Recall).

#### Problem 4 Results
- **Best Hyperparameters (tuned on `gap-validation.tsv`)**: `learning_rate = 0.1`, `l2_reg = 0.001`, `pos_weight = 4.0`.
- **Test Set (`gap-test.tsv`) Performance**:
  - **Full Candidate NP Pool**: **Precision = 40.58%**, **Recall = 45.57%**, **F1-Score = 42.93%** (more than **6x better** than Random and **3.3x better** than Most Recent!).
  - **GAP Candidate Entities (`A` vs. `B`)**: **Precision = 56.65%**, **Recall = 58.60%**, **F1-Score = 57.61%**.

---

### Problem 5 (5 Marks): Top-5 Features Learned by Logistic Regression

#### Goal
Print all features and their weights learned by the Logistic Regression model, and write a short note on the **Top-5 features** (in terms of weight magnitude $|w_j|$) and how they can be interpreted.

#### All 12 Learned Weights (Ranked by Magnitude $|w_j|$)

| Rank | Feature Name | Learned Weight ($w_j$) | Direction & Linguistic Explanation |
| :---: | :--- | :---: | :--- |
| **1** | **`entity_frequency`** | **`+4.5121`** | **Strongest Positive Signal**: In Wikipedia articles, the central person (discourse topic) is mentioned repeatedly across sentences. According to **Centering Theory**, frequently mentioned entities are the most salient backward-looking centers. |
| **2** | **`is_proper_noun`** | **`+2.5635`** | **2nd Strongest Positive Signal**: Every target pronoun in GAP (`he, she, him, her, his`) is an animate human pronoun. Out of ~21 NPs in a passage, most are inanimate common nouns (*"the country"*, *"a contract"*). Checking for `NNP`/`NNPS` filters out inanimate objects and focuses on human names. |
| **3** | **`grammatical_role_subj`** | **`+1.0527`** | **3rd Strongest Signal**: Validates the **Grammatical Role Hierarchy** ($\text{Subject} > \text{Direct Object} > \text{Indirect Object} > \text{Oblique}$). Syntactic subjects are much more likely to be referred to by subsequent pronouns than objects. |
| **4** | **`gender_mismatch`** | **`-0.9855`** | **Strongest Negative Signal**: When a candidate NP has an identifiable gender that conflicts with the pronoun (e.g., *feminine* name *"Erika"* for pronoun *"his"*), the negative weight sharply penalizes its log-odds. |
| **5** | **`is_hobbs_top1`** | **`+0.6018`** | **5th Strongest Signal**: Rewards the #1 candidate proposed by Hobbs' syntactic CFG tree search (combining structural prominence, Binding Condition B, and left-to-right breadth-first order). |
| 6 | `recency_inv_rank` | `+0.5994` | Surface recency rank boost ($1/\text{rank}$). |
| 7 | `same_sentence` | `+0.5968` | Intra-sentential candidates are closer in working memory. |
| 8 | `char_distance_closeness` | `+0.5918` | Linear character proximity boost. |
| 9 | `in_hobbs_top3` | `+0.5723` | Top-3 candidate in Hobbs' CFG tree search. |
| 10 | `parallel_role` | `+0.1476` | Syntactic parallelism preference (Subject $\rightarrow$ Subject). |
| 11 | `gender_match` | `+0.0762` | Small positive weight because in GAP, both `A` and `B` are explicitly selected to have the **same gender** (Gender-Balanced Coreference), so matching gender does not distinguish `A` from `B`, whereas `gender_mismatch` (`-0.9855`) actively rules out opposite-gender distractors in the full NP pool! |
| 12 | `number_agreement` | `-0.0315` | Near zero because almost all proper noun candidates (`A` and `B`) are already singular (`NNP`), providing little discriminative variance. |

---

### Problem 6 (5 Marks): Error Analysis & How the Algorithm Can Be Improved

#### Goal
Describe the errors made by our Logistic Regression implementation on the test set and explain how the algorithm can be improved.

#### Part A: Major Error Categories Found (with Real Examples from `gap-test.tsv`)

1. **Kinship Relations & Possessive Nesting (`test-1`)**:
   - **Passage Snippet**: *"Former NHLer **Gary Suter** and Olympic-medalist **Bob Suter** are **Dehner**'s uncles. **His** cousin is Minnesota Wild alternate captain Ryan Suter."*
   - **Predicted**: `'Former NHLer Gary Suter'` ($P = 0.530$) | **True Gold**: `'Dehner'`
   - **Why it failed**: *Gary Suter* is the grammatical subject of the preceding sentence (`grammatical_role_subj = 1.0`), whereas *Dehner* is inside a possessive modifier (*"Dehner's uncles"*). Resolving *"His cousin"* to *Dehner* requires **world knowledge of kinship relations** (if Gary and Bob Suter are Dehner's uncles, then Ryan Suter is Dehner's cousin, not Gary Suter's cousin!).

2. **Quoted Speech vs. Main Narrative Frame (`test-4`)**:
   - **Passage Snippet**: *"At the trial, **Pisciotta** said: 'Those who have made promises to us are called Bernardo Mattarella, Prince Alliata, the monarchist MP **Marchesano** and also Signor Scelba... it was **Marchesano**, Prince Alliata and Mattarella who came to see me...' Before the trial, Pisciotta had been examined by **his** Judges..."*
   - **Predicted**: `'Marchesano'` ($P = 0.823$) | **True Gold**: `'Pisciotta'`
   - **Why it failed**: *Marchesano* is mentioned multiple times inside the direct quote right before the pronoun, giving it a high `entity_frequency` and `recency_inv_rank` score, even though *Marchesano* only appeared inside quoted speech and the narrative returned to the speaker (*Pisciotta*).

3. **Fictional Character vs. Actor Aliasing in Parentheticals (`test-5` and `test-6`)**:
   - **Passage Snippet (`test-5`)**: *"It is about a pair of United States Navy shore patrollers (Tom Berenger and **William McNamara**) ... **Eddie Devane** (**William McNamara**) is a young sailor on **his** way to..."*
   - **Predicted**: `'William McNamara'` ($P = 0.575$) | **True Gold**: `'Eddie'`
   - **Why it failed**: Wikipedia movie plots mention the actor's name (*William McNamara*) in parentheses right after the character's name (*Eddie Devane*). Because *William McNamara* was mentioned twice in the passage, it has higher `entity_frequency` and is closer in character distance to *"his"*, even though *"a young sailor on his way"* semantically describes the character (*Eddie*), not the actor.

4. **Multi-Entity Action Sequences & Commonsense Event Semantics (`test-8`)**:
   - **Passage Snippet**: *"The monster arrives and bites **Jeni**'s tongue, but David manages to break free... **Sophie** and David manage to lock the monster inside... **Jeni** is killed when the monster breaks through a window and pulls **her** in."*
   - **Predicted**: `'Sophie'` ($P = 0.636$) | **True Gold**: `'Jeni'`
   - **Why it failed**: Both *Sophie* and *Jeni* are feminine proper nouns mentioned multiple times, and both appear in subject positions. Knowing that *"pulls her in"* refers to *Jeni* requires understanding the causal verb-event structure (*"Jeni is killed when..."*).

#### Part B: How the Algorithm Can Be Improved
1. **Full Dependency Parsing & Fine-Grained Grammatical Roles**:
   - Replace shallow regex chunking with a full syntactic dependency parser to distinguish main-clause subjects (`nsubj`), passive subjects (`nsubjpass`), direct objects (`dobj`), prepositional objects (`pobj`), and possessive modifiers (`poss`).
2. **Quotation & Discourse-Segment Awareness**:
   - Track quotation marks (``` ... ''`) and speaker attribution verbs (*said, stated, wrote*) so that entities mentioned only inside embedded quotes do not override the main narrative protagonist outside the quote.
3. **Appositive & Parenthetical Detection**:
   - Detect parenthetical appositions like `Character Name (Actor Name)` and link or down-weight parenthetical actor names when resolving narrative pronouns.
4. **Entity-Centric / Cluster-Level Features**:
   - Group partial name mentions (e.g., *"Dr. Ali Aladhadh"* and *"Ali Aladhadh"*, or *"Eddie Devane"* and *"Eddie"*) into a single **entity cluster** before computing mention frequency and grammatical salience, and add verb selectional preference features (e.g., matching verbs like *sailor / killed / played* with their semantic agent/patient).

---

### Problem 7 (10 Marks): Rule-Based Hobbs' Algorithm on CFG Trees

#### Goal
Implement the classic **Rule-Based Hobbs' Algorithm** (Jurafsky & Martin, Section 21.6.1) using Context-Free Grammar (CFG) parse trees and report its performance in terms of Precision, Recall, and F-scores.

#### How Hobbs' Algorithm Works Step-by-Step (`hobbs_rank_candidates_for_segment`)
We convert each sentence's `nltk.Tree` into a `ParentedTree` (`cfg_trees`) where every node has a `.parent()` pointer and `.subtrees()`, allowing us to climb **up** parent links and search **down** child subtrees in left-to-right Breadth-First Search (`_bfs_collect_nps`).

Then we follow Hobbs' 9-step tree traversal:
- **Step 1**: Start at the `NP#id` node immediately dominating the target pronoun (`start_node`).
- **Step 2**: Climb **up** the tree to the first `NP` or `S` node encountered. Call this node $X$, and call the path we climbed $p$.
- **Step 3**: Traverse all branches below $X$ to the **left** of path $p$ in a **left-to-right, breadth-first** manner (`_bfs_collect_nps(left_siblings, require_intervening_np_or_s=True)`). Propose any `NP` node encountered that has an `NP` or `S` node between it and $X$.
  - *Linguistic reason*: This enforces **Binding Theory Condition B**! In *"Dehner helped him"*, *"him"* is inside `VP`, so the first `NP`/`S` node above *"him"* is `S`. Because there is no intervening `NP` or `S` node between `S` and the subject *"Dehner"*, Step 3 blocks *"Dehner"* as the antecedent of *"him"*. By contrast, in *"Dehner's mother helped him"*, *"Dehner"* is inside `NP("Dehner's mother")`, so there **is** an intervening `NP` node and Step 3 proposes *"Dehner"*!
- **Step 4 (Prior Sentences)**: When $X$ reaches the root `S` node of the current sentence, iterate backwards through the preceding sentences $s_{t-1}, s_{t-2}, \dots, s_0$. For each preceding sentence, perform a **left-to-right, breadth-first search** (`_bfs_collect_nps([prev_tree])`) and propose every compatible `NP` encountered.
- **Steps 5–8 (Higher Clauses in the Current Sentence)**: Before reaching the root of the current sentence, climb up from $X$ to the next enclosing `NP` or `S` node:
  - **Step 6**: If $X$ is an `NP` node, propose $X$.
  - **Step 7**: Traverse all branches below $X$ to the **left** of path $p$ in a left-to-right, breadth-first manner (without requiring an intervening `NP`/`S` node, so a possessive pronoun like *"his"* in *"Dehner helped his club"*—which stopped at `NP("his club")` in Step 2—now climbs to `S` in Step 5 and proposes the subject *"Dehner"* in Step 7!).
  - **Step 8**: If $X$ is an `S` node, traverse all branches of $X$ to the **right** of path $p$ in a left-to-right, breadth-first manner without going below any `NP` or `S` node (`stop_below_np_or_s=True`).

#### Problem 7 Results
- **Full Candidate NP Pool (All POS-Extracted Candidate NPs)**:
  - **Precision = 30.42%**, **Recall = 34.29%**, **F1-Score = 32.24%**
  - Without any machine learning, Hobbs' algorithm improves F1-score from **7.13%** (Random) and **12.85%** (Most Recent) all the way to **32.24%**—a **2.5x jump** over surface recency!
- **GAP Candidate Entities (`A` vs. `B`)**:
  - **Precision = 43.46%**, **Recall = 42.36%**, **F1-Score = 42.90%**.

---

### Problem 8 (5 Marks): Comparing Logistic Regression vs. Hobbs' Algorithm

#### Quantitative Comparison Table on `gap-test.tsv` (2,000 Segments)

| Method | Full Candidate NP Pool F1 | GAP (`A`/`B`) Precision | GAP (`A`/`B`) Recall | GAP (`A`/`B`) F1 |
| :--- | :---: | :---: | :---: | :---: |
| **1. Random Assignment (100 runs)** | 7.13% | 44.07% | 44.07% | 44.07% |
| **2. Most Recent Antecedent** | 12.85% | 40.15% | 40.15% | 40.15% |
| **3. Rule-Based Hobbs' Algorithm** | 32.24% | 43.46% | 42.36% | 42.90% |
| **4. Custom Logistic Regression (Ours)** | **42.93%** | **56.65%** | **58.60%** | **57.61%** |
| *Extra Credit: Scikit-Learn Logistic Regression* | *42.33%* | *55.61%* | *59.22%* | *57.36%* |

#### Qualitative Comparison: Why Does Logistic Regression Outperform Hobbs' Algorithm?
1. **Global Discourse Topicality vs. Single-Sentence Tree Search**:
   - Hobbs' algorithm processes sentences one by one backwards ($s_{t}, s_{t-1}, s_{t-2}$) and picks the **first** compatible NP in left-to-right breadth-first order. If sentence $s_{t-1}$ begins with a minor character in subject position, Hobbs' algorithm blindly picks that minor character.
   - Logistic Regression combines local syntax with **discourse-wide salience** (`entity_frequency`, weight `+4.5121`). Even if the main protagonist is not the subject of the immediately preceding clause, their high mention frequency across the passage allows Logistic Regression to identify them as the discourse topic.
2. **Soft Probabilistic Trade-offs vs. Hard Deterministic Rules**:
   - Hobbs' algorithm uses a rigid, fixed traversal order. If a lexicon does not know the gender of an unfamiliar foreign surname (e.g., *"Dehner"* or *"Pisciotta"*), Hobbs treats all unknown names as equally compatible and relies purely on tree position.
   - Logistic Regression **weights and sums 12 complementary cues simultaneously** (Entity Frequency, Proper Noun status, Subject role, Gender mismatch, Hobbs' Top-1/Top-3 rank, Recency, Same Sentence, and Parallelism), yielding a **+10.69%** F1 boost on the full NP pool and a **+14.71%** F1 boost on GAP (`A` vs. `B`).
3. **Why Hobbs Still Helps Inside Logistic Regression**:
   - Notice that our Logistic Regression model includes `is_hobbs_top1` (`+0.6018`, #5 feature overall!) and `in_hobbs_top3` (`+0.5723`) among its features. Thus, our statistical model absorbs the syntactic tree wisdom of Hobbs' algorithm while overcoming its brittleness.

---

### Extra Credit (10 Marks): Scikit-Learn Logistic Regression Implementation

#### How We Implemented It (`run_extra_credit_sklearn`)
- Kept completely separate at the bottom of `anaphora_resolution.py` so Problems 1–8 remain 100% basic Python + NLTK.
- Uses `sklearn.linear_model.LogisticRegression(C=c_val, class_weight={0: 1.0, 1: pw}, max_iter=500, random_state=42)` on the exact same 12 features, and answers all questions above:
  1. **Hyperparameter Tuning (Problem 4)**: Tuned $C \in \{0.01, 0.1, 1.0, 10.0\}$ and `pos_weight` $\in \{2.0, 3.0, 4.0\}$ on `gap-validation.tsv`, selecting $C = 0.1, \text{pos\_weight} = 4.0$.
  2. **Test Set Evaluation (Problem 4)**:
     - **Full Candidate NP Pool**: Precision = **39.99%**, Recall = **44.95%**, F1 = **42.33%** (vs. **42.93%** for our custom implementation).
     - **GAP Candidates (`A` vs. `B`)**: Precision = **55.61%**, Recall = **59.22%**, F1 = **57.36%** (vs. **57.61%** for our custom implementation).
  3. **Learned Feature Weights & Top-5 Features (Problem 5)**:
     - #1 `entity_frequency` (`+4.2958`)
     - #2 `is_proper_noun` (`+2.9008`)
     - #3 `grammatical_role_subj` (`+1.1571`)
     - #4 `recency_inv_rank` (`+0.9065`)
     - #5 `gender_mismatch` (`-0.7172`)
     - *(Followed by #6 `in_hobbs_top3` at `+0.6831`)*. Both `scikit-learn` and our from-scratch SGD classifier learn nearly identical weights and top features!
  4. **Error Analysis & Comparison with Hobbs (Problems 6 & 8)**:
     - Makes 971 errors on gold-annotated test segments (vs. 960 for our custom LR) with the exact same 4 linguistic error patterns, and outperforms Hobbs' algorithm by **+10.09%** F1 on the full NP pool and **+14.46%** F1 on GAP (`A`/`B`).

---

## 3. How to Run the Code Yourself

Open a terminal in the `anaphora-resolution` folder and run:

```bash
python3 anaphora_resolution.py
```

The script takes about **6 seconds** to run from start to finish and prints the formatted results for **Problems 1 through 8** and **Extra Credit** directly to the terminal.
