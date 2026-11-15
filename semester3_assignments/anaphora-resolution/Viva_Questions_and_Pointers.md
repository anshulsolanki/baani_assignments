# Viva Preparation Guide: Pointers & Questions for Anaphora Resolution

This document is your **quick-reference viva sheet** for defending your **Anaphora Resolution** assignment ([anaphora_resolution.py](file:///Users/solankianshul/Documents/projects/temp_work/baani_work/assignments/semester3/anaphora-resolution/anaphora_resolution.py)). It contains:
1. **Quick Code Pointers** (exact functions and line numbers to show the TA).
2. **Key Numbers to Remember** (so you can explain your results without hesitating).
3. **15 Likely TA / Professor Viva Questions with Clear Answers**.

---

## 1. Quick Code Pointers ("Where is Problem X in your code?")

If the TA asks you to open [anaphora_resolution.py](file:///Users/solankianshul/Documents/projects/temp_work/baani_work/assignments/semester3/anaphora-resolution/anaphora_resolution.py) and show where a specific problem is implemented, use this map:

- **Main Flow (`main()`, line 1040)**:
  - Show the bottom of the file first! Point out how `main()` loads `gap-development.tsv` (train), `gap-validation.tsv` (dev), and `gap-test.tsv` (test), and then calls `problem_1()` through `problem_8()` and `extra_credit()` in exact order.
- **Problem 1 — POS Tagging & Candidate NP Extraction (`problem_1()`, line 363)**:
  - Point to `CFG_GRAMMAR` (line 184) and `extract_candidates_from_dataset()` (line 250).
  - Explain that we use `nltk.sent_tokenize`, `nltk.word_tokenize`, and `nltk.pos_tag_sents`, and then use `nltk.RegexpParser` (`CFG_PARSER`) to group `DT + JJ + NN/NNP` tags into `NP` chunks.
- **Problem 2 — Random Baseline (`problem_2()`, line 393)**:
  - Point to the `for _ in range(100):` loop that uses `rng.choice(cands)` to pick a random candidate NP 100 times and averages the accuracy.
- **Problem 3 — Most Recent Antecedent (`problem_3()`, line 430)**:
  - Point to `preceding = [c for c in seg["candidates"] if c["start"] < p_off]` and `preceding[-1]`, which picks the closest NP right before the pronoun.
- **Problem 4 — Custom Logistic Regression from Scratch (`SimpleLogisticRegression`, line 532 & `problem_4()`, line 629)**:
  - Show `class SimpleLogisticRegression` (only ~35 lines of code!):
    - `sigmoid(self, z)`: computes $\frac{1}{1 + e^{-z}}$ using `math.exp(-z)`.
    - `predict_proba_one(self, x)`: computes the dot product $z = b + \sum w_j x_j$ and passes it to `sigmoid(z)`.
    - `fit(self, X, y, pos_weight)`: runs Stochastic Gradient Descent (SGD) for 20 epochs.
- **Problem 5 — Learned Feature Weights (`problem_5()`, line 679)**:
  - Sorts the 12 features in `FEATURE_NAMES` by `abs(w)` and prints the Top-5 features.
- **Problem 6 — Error Analysis (`problem_6()`, line 713)**:
  - Finds test examples where `best_cand["is_antecedent"] == False` and prints the predicted NP vs. true gold NP.
- **Problem 7 — Hobbs' Algorithm on CFG Trees (`hobbs_search_current_sentence()`, line 788 & `problem_7()`, line 892)**:
  - Show how we convert each sentence into a `ParentedTree` (so every node has `.parent()`) and run Breadth-First Search (`bfs_collect_nps()`, line 768) left-to-right across the tree.
- **Problem 8 — Comparison Table (`problem_8()`, line 943)**:
  - Prints the side-by-side comparison of Random, Most Recent, Hobbs' Algorithm, and Custom Logistic Regression.
- **Extra Credit — Scikit-Learn (`extra_credit()`, line 969)**:
  - Uses `from sklearn.linear_model import LogisticRegression`, tunes `C` and `pos_weight` on the dev set, and compares weights and F1 with our custom model.

---

## 2. Key Numbers & Takeaways to Remember

| Method | Full NP Pool (~21 NPs/seg) | GAP `A` vs. `B` Candidates | Key Takeaway for Viva |
| :--- | :---: | :---: | :--- |
| **Problem 1 (Candidate NPs)** | **42,597 NPs** (21.30/seg) | Covers `A` and `B` | A typical paragraph has ~21 NPs before/around the pronoun. |
| **Problem 2 (Random, 100 runs)** | **7.13%** Acc | **44.07%** Acc | ~1/15 to 1/21 chance on all NPs; <50% on A/B because ~10% of GAP rows have neither A nor B as true antecedent. |
| **Problem 3 (Most Recent)** | **12.85%** Acc | **40.15%** Acc | Nearly doubles accuracy over Random on all NPs, but loses on A/B because Subjects (earlier) beat Objects (more recent). |
| **Problem 7 (Hobbs' Algorithm)** | **32.24%** F1 | **42.90%** F1 | Huge jump (**12.85% $\rightarrow$ 32.24%**) without ML because BFS visits Subjects before Objects! |
| **Problem 4 (Custom LR)** | **42.93%** F1 | **57.61%** F1 | Best overall! Combines discourse frequency + proper noun + subject role + gender + Hobbs rank. |
| **Extra Credit (Scikit-Learn LR)** | **42.33%** F1 | **57.36%** F1 | Matches our from-scratch model within ~0.3–0.6% F1 and learns the same top features. |

---

## 3. Top 15 Likely Viva Questions & Model Answers

### Q1: What is the difference between Anaphora Resolution and Coreference Resolution?
- **Answer**: **Anaphora resolution** specifically finds the antecedent of a referring expression (usually a pronoun like *he, she, his, her*) that points back to a previous noun phrase in the text. **Coreference resolution** is the broader task of clustering *all* mentions in a document (proper names, common nouns, and pronouns) that refer to the same real-world entity.

### Q2: How did the GAP dataset files map to your Training, Development, and Test sets?
- **Answer**: The official Google GAP repository provides three TSV files:
  - `gap-development.tsv` (2,000 segments) $\rightarrow$ used as our **Training set** to learn feature weights.
  - `gap-validation.tsv` (454 segments) $\rightarrow$ used as our **Development set** for hyperparameter tuning.
  - `gap-test.tsv` (2,000 segments) $\rightarrow$ used as our **Test set** for final evaluation.

### Q3: Why do you report two sets of metrics ("Full Candidate NP Pool" and "GAP Candidates A vs. B")?
- **Answer**: Problem 1 asks us to extract *all* candidate NPs in each segment using a POS tagger, which gives ~21 candidate NPs per segment. However, the GAP dataset only provides ground-truth `TRUE`/`FALSE` annotations for two specific person names (`A` and `B`). Reporting both shows:
  1. How well our system finds the right antecedent out of **all ~21 POS-extracted NPs** (`42.93%` F1), and
  2. How well it distinguishes between the **two competing human entities `A` and `B`** (`57.61%` F1).

### Q4: In Problem 3, why is the "Most Recent Antecedent" baseline better than Random on all NPs (12.85% vs. 7.13%), but slightly worse than Random on A vs. B (40.15% vs. 44.07%)?
- **Answer**:
  - Across all ~21 NPs in a multi-sentence paragraph, NPs from 3 sentences ago are usually forgotten, so picking the closest NP beats picking a random NP from the beginning of the passage (`12.85%` vs. `7.13%`).
  - However, when `A` and `B` are in the same clause—for example, *"Alonso (A) argued with coach Di Stefano (B), and **he** left"*—`A` is the **Subject** (earlier) and `B` is the **Object** (more recent). In English, pronouns prefer the grammatical **Subject** (`A`) over the **Object** (`B`), so always picking the most recent entity (`B`) gets tricked!

### Q5: How did you implement Logistic Regression from scratch in Problem 4 without using `scikit-learn` or `numpy`?
- **Answer**: In `class SimpleLogisticRegression`, we store `self.weights` as a plain Python list of 12 floats and `self.bias` as a float:
  1. **Forward pass (`predict_proba_one`)**: We compute the linear dot product $z = b + \sum_{j=1}^{12} w_j x_j$ using a `for` loop, and pass $z$ into the **sigmoid function** $\sigma(z) = \frac{1}{1 + e^{-z}}$ using `math.exp(-z)`.
  2. **Training (`fit`)**: We use **Stochastic Gradient Descent (SGD)**. For each training pair $(x_i, y_i)$, the gradient of binary cross-entropy loss with respect to weight $w_j$ is $(\hat{y}_i - y_i) x_{i,j} + \lambda w_j$. We subtract `lr * grad_j` from `self.weights[j]`.

### Q6: Why did you clamp `z` between `-30` and `+30` inside `sigmoid(self, z)`?
- **Answer**: If $z$ becomes a large negative number (like $-1000$), `math.exp(-z)` tries to compute $e^{1000}$ and raises a Python `OverflowError`. Since $\frac{1}{1 + e^{30}} \approx 0.0$ and $\frac{1}{1 + e^{-30}} \approx 1.0$, clamping at $\pm 30$ prevents overflow without changing the probability.

### Q7: What is `pos_weight` in your Logistic Regression training, and why do we need it?
- **Answer**: Each segment has ~21 candidate NPs, of which only **1** is the true antecedent ($y = 1$) and **20** are negative ($y = 0$). Because of this 1:20 class imbalance, standard unweighted Logistic Regression would predict low probabilities for everything. Multiplying the error on positive examples ($y=1$) by `pos_weight = 4.0` tells SGD to care more about positive antecedents, which significantly boosts Recall and F1 on the dev set.

### Q8: How do you convert binary pair probabilities into a single antecedent choice for a pronoun?
- **Answer**: Logistic Regression scores each `(pronoun, candidate_NP)` pair independently with a probability $P(y = 1 \mid x)$. In `pick_best_candidate()`, we loop over all candidates for a pronoun and pick the candidate with the **maximum predicted probability** ($\arg\max_c P(y=1 \mid x_c)$), provided that probability is at least our decision threshold (`0.25`).

### Q9: What were the Top-5 features learned by your Logistic Regression model in Problem 5, and why do they make linguistic sense?
- **Answer**:
  1. `entity_frequency` (`+4.5122`): Mention frequency across the passage—captures the **discourse topic** (Centering Theory).
  2. `is_proper_noun` (`+2.5635`): Proper noun (`NNP`)—filters out inanimate common nouns since `he/she/his/her` refer to human beings.
  3. `grammatical_role_subj` (`+1.0529`): Subject position—captures the **Grammatical Role Hierarchy** (Subject > Object > Oblique).
  4. `gender_mismatch` (`-0.9860`): Negative weight that penalizes candidates whose gender conflicts with the pronoun.
  5. `is_hobbs_top1` (`+0.6022`): Top choice of Hobbs' CFG tree search—captures syntactic prominence and Binding Condition B.

### Q10: Why did `gender_mismatch` get a strong weight (`-0.9860`), while `gender_match` got a very small weight (`+0.0761`)?
- **Answer**: In the GAP dataset (*Gender-Balanced Coreference*), both main human candidates `A` and `B` in a passage are intentionally chosen to have the **same gender** (both male or both female). Therefore, having a matching gender does not distinguish `A` from `B`, whereas having a **mismatched** gender (`gender_mismatch = 1`) strongly rules out opposite-gender distractors in the full NP pool!

### Q11: How does Hobbs' Algorithm (Problem 7) work on a CFG parse tree?
- **Answer**: Hobbs' algorithm starts at the `NP` node of the pronoun and climbs up to the first enclosing `NP` or `S` node (called $X$):
  1. **Within the same minimal clause (Step 3)**: It searches branches to the **left** of the pronoun in **left-to-right, breadth-first order**, but requires an intervening `NP` or `S` node between $X$ and the candidate (`require_intervening_np_or_s=True`).
  2. **Higher clauses in the same sentence (Steps 5–8)**: It climbs up to higher `NP`/`S` nodes and searches left branches in left-to-right breadth-first order (without requiring an intervening `NP`/`S`).
  3. **Previous sentences (Step 4)**: It steps backwards through previous sentences ($s_{t-1}, s_{t-2}, \dots$) and searches each sentence tree in **left-to-right, breadth-first order**.

### Q12: Why does Hobbs' Algorithm use Breadth-First Search (BFS) instead of Depth-First Search (DFS), and why require an intervening NP/S node in Step 3?
- **Answer**:
  - **Why left-to-right BFS**: In a parse tree `S -> NP VP`, the **Subject** `NP` is higher in the tree and further left than the **Object** `NP` inside `VP`. Left-to-right BFS automatically visits the Subject before the Object!
  - **Why require an intervening NP/S in Step 3**: This implements **Chomsky's Binding Theory Condition B**—a non-reflexive pronoun (*him/her*) must be free in its minimal clause. In *"John helped him"*, *"him"* cannot be *"John"* (no intervening NP/S node). But in *"John's mother helped him"*, *"John"* is inside `NP("John's mother")`, so there *is* an intervening NP node and *"him"* can refer to *"John"*.

### Q13: Why did Logistic Regression outperform Hobbs' Algorithm in Problem 8 (`42.93%` vs. `32.24%` on all NPs; `57.61%` vs. `42.90%` on A/B)?
- **Answer**:
  1. Hobbs' algorithm is **memoryless across sentences**: when it checks the previous sentence $s_{t-1}$, it blindly picks the subject of $s_{t-1}$ even if that person was a minor character mentioned only once.
  2. Logistic Regression combines **global discourse topicality** (`entity_frequency`) with local syntax (`is_hobbs_top1`, `grammatical_role_subj`), animacy (`is_proper_noun`), and recency, weighting all 12 cues probabilistically instead of making a rigid single-rule decision.

### Q14: What were the main types of errors your model made in Problem 6, and how would you improve it?
- **Answer**:
  1. **Kinship/Relational reasoning (`test-1`)**: *"Gary Suter and Bob Suter are Dehner's uncles. His cousin..."* — model picked the subject *Gary Suter* instead of *Dehner*. **Fix**: Use a full dependency parser and relational/kinship features.
  2. **Quoted Speech (`test-4`)**: A name repeated inside a quote (`"..."`) tricked `entity_frequency` and `recency`. **Fix**: Track quotation boundaries so mentions inside quotes don't override the main speaker.
  3. **Character vs. Actor in Parentheticals (`test-5`)**: *"Eddie Devane (William McNamara) is a sailor on his way..."* — model picked the actor in parentheses because it was closer to *"his"*. **Fix**: Detect and down-weight parenthetical appositives.

### Q15: What if the TA asks you during the viva: "Change the learning rate or number of epochs and run it right now"?
- **Answer**:
  - Go to **`problem_4()` at line 640** of [anaphora_resolution.py](file:///Users/solankianshul/Documents/projects/temp_work/baani_work/assignments/semester3/anaphora-resolution/anaphora_resolution.py#L640-L645):
    ```python
    for lr in [0.01, 0.05, 0.1]:
        for l2 in [0.0, 0.0001, 0.001]:
            for pw in [2.0, 4.0]:
                model = SimpleLogisticRegression(len(FEATURE_NAMES), learning_rate=lr, l2_reg=l2, epochs=20)
    ```
  - You can change `epochs=20` or the `lr` list right there and run `python3 anaphora_resolution.py` (it finishes in ~6 seconds!).
