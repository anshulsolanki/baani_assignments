# Complete Study, Code Walkthrough & Viva Guide — CL2 Assignment 5
## Discourse-Based Text Summarization using Rhetorical Structure Theory (RST)

- **Student Name:** Baani Solanki
- **Roll Number:** `2025114016`
- **Course:** Computational Linguistics 2 — Assignment 5

This document contains the complete, self-contained explanation of the assignment—from the underlying linguistics of **Rhetorical Structure Theory (RST)** to a **function-by-function walkthrough of the code**, **step-by-step macOS Terminal commands**, **how to interpret every metric and table**, and **expected Viva / evaluation questions and answers**.

---

## 1. Scope & Implementation Plan

### 1.1 What Is This Assignment About?
Most basic text summarizers treat a paragraph as a "bag of words" (e.g., counting word frequencies with TF-IDF). However, in **Computational Linguistics 2**, we study how **discourse structure** governs meaning.

When an author writes a paragraph, not all clauses have equal status:
- Some clauses state the **core claim or main point** (**Nucleus**).
- Other clauses provide supporting background, attribution, conditions, or examples (**Satellites**).

In this assignment, we build an **extractive text summarizer** that uses **Rhetorical Structure Theory (RST)** (Mann & Thompson, 1988) and **Marcu's (2000) Discourse Summarization Framework** to summarize 10 classic English paragraphs (`paragraph.txt`) without relying on word-frequency heuristics or black-box LLM summarization, and then compare our RST-based summaries against a modern **ChatGPT** baseline and a **learned Logistic Regression** discourse model.

---

### 1.2 Breakdown of Explicit & Implicit Requirements

| Problem | Points | Explicit Requirement in `assignment.pdf` | Implicit Engineering / Linguistic Details Handled |
| :--- | :---: | :--- | :--- |
| **Problem 1** | 10 | Run the pretrained `isanlp_rst` parser on the 10 paragraphs in `paragraph.txt`. Display the discourse tree and relation labels for each paragraph. | • Use model `'tchewik/isanlp_rst_v3'` (`version='rstdt'`).<br>• Cache the parsed trees in `rst_trees_cache.json` so repeated runs finish in `< 1 second` without re-downloading Hugging Face weights.<br>• Format the binary tree into a clean, readable ASCII tree showing `[Node ID]`, `Nucleus`/`Satellite` roles, `split_rel`, and leaf `[EDU ID]` spans. |
| **Problem 2** | 10 | Extract the Nucleus/Satellite labels and relation types from the parsed output and prepare structured information for summarization. | • `isanlp_rst` parses text into clause-level **Elementary Discourse Units (EDUs)**, whereas extractive summaries select **whole sentences**.<br>• We split each paragraph into sentences (carefully handling abbreviations like `"Ariz.,"` in Para 5 and `"U.S."` in Para 7, as well as multi-sentence quoted speech in Paras 6 and 9), align EDUs to sentences via character offsets `[start, end)`, and extract both local roles and global tree features (**Marcu's Promotion Depth**, **Promoted Nucleus Relations**, and **Path Nuclearity Purity**). |
| **Problem 3** | 10 | Design a set of rules using the extracted RST info (preferring nuclei, weighting top-level nodes, retaining key relations like *Result*, *Summary*, *Explanation*, *Contrast*) to generate 1–2 sentence summaries. | • Design 5 transparent, additive scoring rules (`R1` to `R5`) that print their exact numerical breakdown per sentence.<br>• Select 1 sentence if the paragraph only has 2 sentences (Para 4), and 2 sentences otherwise, preserving original discourse order. |
| **Problem 4** | 10 | Generate a 2–3 sentence summary for each paragraph using ChatGPT. Compare the rule-based RST summaries with ChatGPT and report **Accuracy** and **F1-score** with respect to reference key sentences/content. | • Report **Sentence-Level Classification Metrics** (Accuracy, Precision, Recall, F1 across all 40 sentences against Mann & Thompson's canonical central sentences) **and** **Token-Level Content-Word Overlap F1** (ROUGE-1 style unigram F1). |
| **Problem 5** | 5 | Provide a brief discussion of the results: summarization quality, rule patterns that worked well or failed, and ways to improve the system. | • Analyze why top-down RST rules excel on expository/argumentative paragraphs (**100% F1 on 7 out of 10 paragraphs**: Paras 1, 2, 3, 5, 7, 8, and 9) and explain the exact linguistic reasons for partial/different selections on Paras 4, 6, and 10. |
| **Extra Credit** | 10 | Learn weights for Nucleus and Satellite relations using a **Logistic Regression** model and interpret them in terms of RST itself. | • Implement `SimpleLogisticRegression` from scratch (batch gradient descent + L2 regularization).<br>• Evaluate both **Full-Dataset Fit** (`85.00%` Accuracy / `84.21%` F1) and **Leave-One-Paragraph-Out Cross-Validation (LOPO-CV)** (`75.00%` Accuracy / `73.68%` F1) on unseen paragraphs. |

---

## 2. Step-by-Step Local Mac / macOS Setup Guide

Open your macOS **Terminal** and run the following commands in sequence:

### Step 1: Go to the Project Directory & Check Files
```bash
cd /Users/solankianshul/Documents/projects/temp_work/baani_work/assignments/semester3/cl2_assignment5
ls -la
```
Make sure `paragraph.txt`, `rst_summarization.py`, and `rst_trees_cache.json` are present.

### Step 2: Create and Activate the Python Virtual Environment (`venv`)
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
> **Why do we use `pip install --no-deps isanlp_rst` on macOS?**
> The `isanlp_rst` package lists an old C++ library (`jsonnet`) in its `pyproject.toml` that fails to compile on Apple Silicon / Python 3.13, even though `isanlp_rst` v3 never actually imports `jsonnet`! Installing `isanlp_rst` with `--no-deps` and installing its actual Python dependencies directly avoids any C++ compiler error:

```bash
pip install --upgrade pip
pip install --no-deps isanlp_rst
pip install git+https://github.com/iinemo/isanlp.git
pip install razdel torch transformers huggingface_hub nltk tqdm numpy sentencepiece protobuf pillow playwright lxml matplotlib fire
```

### Step 4: Run the Script & Save Terminal Output
```bash
python3 rst_summarization.py | tee output_log.txt
```
- **How Caching Works:** By default, `parse_paragraphs_with_isanlp()` checks if `rst_trees_cache.json` exists. Since we already ran the live `isanlp_rst` (`rstdt`) parser and saved the exact trees in `rst_trees_cache.json`, the script runs in **under 1 second**.
- **How to Force Live Neural Parsing:** If you want to watch `isanlp_rst` download the Hugging Face model (`tchewik/isanlp_rst_v3`) and parse each paragraph live on CPU, either delete `rst_trees_cache.json` before running or pass `force_run=True` inside `parse_paragraphs_with_isanlp()`.

### Step 5: Verify Generated Outputs & Submission Archive
```bash
ls -lh output_log.txt summarization_results.json Report.pdf 2025114016_a5.tar
tar -tvf 2025114016_a5.tar
```

---

## 3. Theoretical Foundations & In-Depth Code Explanation

### 3.1 Rhetorical Structure Theory (Mann & Thompson, 1988)
1. **Elementary Discourse Units (EDUs):**
   - The minimal, non-overlapping clause-level building blocks of discourse (leaves of the RST tree).
   - Example from Paragraph 1:
     - `[EDU 0]`: *"I don't believe"* (`Satellite`, `Attribution`)
     - `[EDU 1]`: *"that endorsing the Nuclear Freeze Initiative is the right step for California Common Cause."* (`Nucleus`, `span`)
2. **Nuclearity (`NS`, `SN`, `NN`):**
   - Every internal node in the binary RST tree joins a `left` child span and a `right` child span with a nuclearity code:
     - **`NS` (Nucleus–Satellite):** Left child is the **Nucleus** (core message); Right child is the **Satellite** (supporting detail).
     - **`SN` (Satellite–Nucleus):** Left child is the **Satellite** (e.g., an introductory `Background`, `Contrast` concession, or `Attribution` clause); Right child is the **Nucleus**.
     - **`NN` (Nucleus–Nucleus / Multinuclear):** Both children are equally central **Nuclei** (e.g., `Joint`, `Contrast`, `Temporal`, `same-unit`).
3. **Marcu's (2000) Nuclearity Promotion Principle (`promoted_depth`):**
   - In Daniel Marcu's classic book *The Theory and Practice of Discourse Parsing and Summarization (2000)*, each internal node in an RST tree promotes the salient EDU(s) of its **Nucleus** child(ren).
   - Imagine walking down the tree from the `ROOT` (depth 0) to a leaf EDU $e$:
     - If **every single step** along the path from the `ROOT` to $e$ is a `Nucleus` transition (`satellite_steps == 0`), then $e$ is promoted all the way to the `ROOT` (**`promoted_depth = 0`**). This is the **Central Nucleus** of the entire paragraph!
     - If the path to $e$ has its **last (deepest) `Satellite` transition** at step index $k_{\text{last\_sat}}$ (and every step below that is `Nucleus`), then $e$ is promoted up to the subtree rooted at depth:
       $$\text{promoted\_depth}(e) = k_{\text{last\_sat}} + 1$$
     - **Why is `promoted_depth` better than raw leaf `depth`?**
       Because a very important sentence might have 3 or 4 internal clauses (making its leaf `depth = 4` or `5`), even though that entire multi-clause subtree is promoted to depth `0` or `1` right at the top of the paragraph!
       For example, in **Paragraph 5** (*Scottsdale model house*), Sentence 4 (*"Then, as my wife entered the dining room, one agent pointed to a massive chandelier and asked, 'What would you call that in England?'"*) has leaves at depth 4–6, **but** its `promoted_depth` is **`1`** (it is the main Nucleus of the Root's right branch!), whereas Sentence 2 (*"We say 'to-mah-to'..."*) is buried under two `Elaboration` satellites at **`promoted_depth = 5`**.

---

### 3.2 Walkthrough of Every Function in `rst_summarization.py`

#### Block 1: Loading & Sentence Splitting (`load_paragraphs`, `split_into_sentences`)
- **`load_paragraphs(filepath)`**:
  - **Input:** Path to `paragraph.txt`.
  - **Output:** List of 10 dicts `[{'id': 1, 'text': '...'}, ...]`.
- **`split_into_sentences(paragraph_text)`**:
  - **Input:** Raw paragraph string.
  - **Output:** List of sentence dicts `[{'sent_idx': 0, 'text': '...', 'start': 0, 'end': 106}, ...]`.
  - **Why we wrote a custom character loop instead of a naive `.split('.')`:**
    1. Paragraph 5 contains `"Scottsdale, Ariz., model house"`—a period followed immediately by a comma.
    2. Paragraph 7 contains `"affect U.S. cities."`—an abbreviation `"U.S."` inside a sentence.
    3. Paragraphs 6 and 9 contain multi-clause quoted speech (`"Yes," she replied, to their surprise, "and I find it hard sometimes to smile at Jesus. He can be very demanding."` and `...recalled her instructor's words: "If you ever go into a spin in a Cessna 150, just let go of the controls. It's built to fly on its own."`).
    Our character loop checks an `abbreviations` set (`{"u.s.", "ariz.", ...}`), whether a period is followed by a comma or lowercase letter, and whether a double quotation mark `"` is still unclosed (`count('"') % 2 != 0`), ensuring all 40 sentences across the 10 paragraphs split cleanly with exact `[start, end)` character offsets.

#### Block 2: Problem 1 — Running `isanlp_rst` & Displaying Trees (`problem_1`)
- **`parse_paragraphs_with_isanlp(paragraphs, cache_path="rst_trees_cache.json", force_run=False)`**:
  - **Input:** List of paragraphs.
  - **Output:** Dictionary mapping paragraph ID (`"1"`..`"10"`) to the serialized binary RST tree dictionary.
- **`format_rst_tree_ascii(node, role_from_parent, rel_from_parent, indent)`**:
  - **Input:** Root or internal node of a parsed RST tree.
  - **Output:** Indented list of strings representing the full hierarchical tree.
  - **Logic:** Inspects `node["nuclearity"]`:
    - If `"NS"`, left child is `Nucleus (rel=span)` and right child is `Satellite (rel=node['relation'])`.
    - If `"SN"`, left child is `Satellite (rel=node['relation'])` and right child is `Nucleus (rel=span)`.
    - If `"NN"`, both children are `Nucleus (rel=node['relation'])`.

#### Block 3: Problem 2 — Extracting Structured RST Features (`problem_2`)
- **`extract_edu_records(node, ...)`**:
  - **Input:** Parsed RST tree node.
  - **Output:** Flat list of dictionaries—one per leaf EDU—containing:
    - `immediate_role` (`"Nucleus"` or `"Satellite"`) and `immediate_relation`
    - `promoted_nucleus_relations`: all rhetorical relations along the continuous Nucleus promotion chain (`path_relations[promoted_depth:]`, excluding the syntactic continuation pseudo-relation `same-unit`)
    - `depth` (number of edges from Root) and `promoted_depth` (Marcu promotion depth)
    - `nucleus_steps`, `satellite_steps`, and nuclearity purity `nucleus_ratio = 1.0 / (1.0 + satellite_steps)`
    - `is_central_nucleus = (satellite_steps == 0)`
- **`align_edus_to_sentences(sentences, edu_records)`**:
  - **Input:** Sentence spans and EDU records for a paragraph.
  - **Output:** List of sentence-level structured records (`sentence_records`).
  - **Logic:** Assigns each EDU to the sentence containing its character midpoint `(edu["start"] + edu["end"]) / 2.0`, and aggregates:
    - `has_central_nucleus` (`True` if any EDU in the sentence has `is_central_nucleus == True`)
    - `min_depth` and `min_promoted_depth` (shallowest tree depth and promotion depth among the sentence's EDUs)
    - `max_nucleus_ratio` (highest root-to-leaf nuclearity purity in the sentence)
    - `dominant_role` (`"Nucleus"` if `has_central_nucleus`, `nucleus_edu_count >= satellite_edu_count`, `min_depth == 1`, or the sentence opens with a top-level promoted Nucleus clause `promoted_depth <= 1`; else `"Satellite"`)
    - `nucleus_relations` and `satellite_relations` (promoted relations carried by Nucleus vs. Satellite EDUs in that sentence).

#### Block 4: Problem 3 — Rule-Based RST Sentence Scoring (`problem_3`)
- **`score_sentence_with_rst_rules(srec, total_sentences)`**:
  - Scores each sentence using **5 transparent linguistic rules**:
    $$\text{Score}(S) = R_1 + R_2 + R_3 + R_4 + R_5$$
    1. **$R_1$ — Central Nucleus Promotion (`+3.00`):** Added if `srec["has_central_nucleus"] == True` (`PromDepth = 0`).
    2. **$R_2$ — Marcu Promotion Level & Tree Depth (`+3.0 / (1 + min_promoted_depth) + 1.5 / min_depth`):** Rewards sentences promoted near the root (`PromDepth = 0` gets `+3.00`; `PromDepth = 1` gets `+1.50`; `PromDepth = 5` gets `+0.50`) and shallower tree nodes.
    3. **$R_3$ — Path Nuclearity Purity (`+3.0 * max_nucleus_ratio`):** Rewards sentences whose EDUs have zero or few Satellite demotions along the path from the root ($1 / (1 + \text{satellite\_steps})$).
    4. **$R_4$ — Core Rhetorical Relation Bonus (`+sum(RELATION_BONUS_WEIGHTS) / sqrt(num_edus)`):** Rewards sentences whose promoted Nucleus EDUs participate in high-value informative relations (*Result* `2.0`, *Summary* `2.0`, *Explanation* `1.6`, *Contrast* `1.5`, *Joint* `1.3`, *Manner-Means* `1.1`, *Condition/Temporal* `1.0`, *Elaboration* `0.8`). Dividing by $\sqrt{\text{num\_edus}}$ prevents a long sentence with many minor clauses from unfairly beating a concise topic sentence.
    5. **$R_5$ — Satellite Pruning & Short Fragment Penalty:** If `dominant_role == "Satellite"`, subtracts `-0.8` plus relation penalties (*Background* `-1.2`, *Attribution* `-0.8`, *Elaboration* `-0.6`) normalized by `num_edus`. Also applies `-2.0` if the sentence has `< 6` words (filtering out isolated 3–4 word dialogue replies like `"Smile at your husbands."` or `"Ostentatious," my wife replied.`).

#### Block 5: Problem 4 — Evaluation Against Gold Reference & ChatGPT (`problem_4`)
- Computes two complementary sets of metrics across all 10 paragraphs (`40` total sentences):
  1. **Binary Sentence Selection Metrics (Accuracy, Precision, Recall, F1):**
     - Compares the set of selected sentence indices against `gold_key_sentences` (the central thesis sentences from Mann & Thompson's 1988 rhetorical analyses):
       $$\text{Accuracy} = \frac{TP + TN}{40}, \quad \text{Precision} = \frac{TP}{TP + FP}, \quad \text{Recall} = \frac{TP}{TP + FN}, \quad F_1 = \frac{2 \cdot \text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$
  2. **Content-Word Token Overlap F1 (`compute_token_overlap_prf`):**
     - Removes basic English stopwords and computes unigram content-word overlap Precision, Recall, and F1 (ROUGE-1 F1) between:
       - `RST Summary vs. Gold Reference Content` (**`81.24%`**)
       - `RST Summary vs. ChatGPT Summary` (**`40.07%`**)

#### Block 6: Extra Credit — Learning Weights via Logistic Regression (`extra_credit`)
- **`extract_logreg_features(srec)`**:
  - Converts each sentence into a 16-dimensional feature vector $x_i \in \mathbb{R}^{16}$:
    - 4 global structural features: `is_central_nucleus`, `inv_promoted_depth`, `inv_min_depth`, `max_nucleus_ratio`
    - 7 Nucleus relation densities (`N_Explanation`, `N_Contrast`, `N_Joint`, `N_Elaboration`, `N_Manner_Means`, `N_Condition`, `N_Temporal`)
    - 5 Satellite relation densities (`S_Elaboration`, `S_Background`, `S_Attribution`, `S_Explanation`, `S_Condition_Enablement`)
- **`SimpleLogisticRegression`**:
  - Models the probability that sentence $i$ belongs in the summary as:
    $$P(y_i = 1 \mid x_i) = \sigma(w^\top x_i + b) = \frac{1}{1 + e^{-(w^\top x_i + b)}}$$
  - Trained via batch gradient descent with L2 regularization ($\lambda = 0.02$, $\eta = 0.25$) to minimize binary cross-entropy loss.

---

## 4. Results Interpretation Guide

### 4.1 Summary of Quantitative Results
1. **Rule-Based RST Summarizer (Problem 3 & 4):**
   - **Sentence Selection Accuracy:** **`85.00%`** (`34 / 40` sentences correctly classified)
   - **Sentence Selection Precision / Recall / F1:** **`84.21%`** (`TP = 16, FP = 3, FN = 3`)
   - **Content-Word Token F1 (vs. Gold Key Content):** **`81.24%`**
   - **Exact 100% Paragraph Matches:** Matched the exact gold summary sentences on **7 out of 10 paragraphs** (Paragraphs 1, 2, 3, 5, 7, 8, and 9), achieved partial match (`60%` Acc / `50%` F1) on Paragraphs 6 and 10, and matched the primary topic sentence on **9 out of 10 paragraphs**.
2. **ChatGPT 2–3 Sentence Baseline (Problem 4):**
   - **Sentence Alignment Accuracy:** **`75.00%`** (`30 / 40`)
   - **Sentence Alignment Precision / Recall / F1:** Precision = `65.52%`, Recall = **`100.00%`**, F1 = **`79.17%`**
   - **Why ChatGPT has 100% Recall but lower Precision (`65.52%`):** Because ChatGPT generates 2–3 abstractive sentences that synthesize details from 3 source sentences per paragraph, it covers every gold sentence (`FN = 0`), but also pulls in secondary elaboration clauses (`FP = 10`).
3. **Learned Logistic Regression Model (Extra Credit):**
   - **Full-Dataset Fit (Top-$K$ Selection):** **Accuracy = `85.00%` (`34/40`)**, **F1-Score = `84.21%`**
   - **Leave-One-Paragraph-Out Cross-Validation (Unseen Paragraphs):** **Accuracy = `75.00%` (`30/40`)**, **F1-Score = `73.68%`**.

### 4.2 How to Interpret the Learned Logistic Regression Weights
Look at the learned weights printed by `extra_credit()`:
- **Most Positive Weights (Promote Summary Inclusion):**
  1. `inv_min_depth` (`+1.0888`)
  2. `inv_promoted_depth` (`+1.0334`)
  3. `N_Temporal` (`+0.6741`)
  4. `is_central_nucleus` (`+0.6345`)
  5. `max_nucleus_ratio` (`+0.4980`)
  6. `N_Elaboration` (`+0.3180`)
  7. `N_Joint` (`+0.2525`)
  8. `N_Manner_Means` (`+0.1320`)
  9. `N_Explanation` (`+0.1210`)
- **Most Negative Weights (Suppress Summary Inclusion):**
  - `N_Contrast` (`-0.4158`)
  - `S_Condition_Enablement` (`-0.3203`)
  - `S_Explanation` (`-0.1131`)
  - `S_Elaboration` (`-0.0575`)
- **Key Insight for Your Report / Viva:**
  Compare **`N_Explanation` (`+0.1210`)** vs. **`S_Explanation` (`-0.1131`)**, and **`N_Elaboration` (`+0.3180`)** vs. **`S_Elaboration` (`-0.0575`)**.
  The same rhetorical relation (`Explanation` or `Elaboration`) has a **positive weight when the sentence is the Nucleus** and a **negative weight when the sentence is the Satellite**! This empirically proves Mann & Thompson's (1988) core claim: in an asymmetric relation, the Nucleus states the central thesis (which must be kept in a summary), while the Satellite provides supporting justification or detail (which should be pruned).

---

## 5. High-Probability Viva Questions & Answers

1. **Q: Why did your Rule-Based RST Summarizer get 0% Sentence F1 on Paragraph 4 (the jobless line paragraph)?**
   - **Answer:** Paragraph 4 only has 2 sentences, so our 1-to-2 sentence summarizer selects `k = 1` sentence. In Mann & Thompson's human analysis, Sentence 2 (*"Every rule has exceptions, but the tragic and too-common tableaux... illustrates a lack of jobs, not laziness"*) is the main claim. However, the pretrained `isanlp_rst` parser labeled Sentence 1 as the Root `Nucleus` (`PromDepth = 0`) and attached Sentence 2 as an `Elaboration (NS)` satellite (`PromDepth = 1`). Because our rules trust the parser's nuclearity, they picked Sentence 1 (`Score = 10.30`) over Sentence 2 (`Score = 4.90`).

2. **Q: In Paragraph 5 (the Scottsdale model house joke), why did the rule-based system select Sentence 1 and Sentence 4 instead of Sentence 5 (`"Ostentatious," my wife replied.`)?**
   - **Answer:** Two reasons:
     1. In the RST tree, Sentence 4 (*"Then, as my wife entered the dining room, one agent pointed to a massive chandelier and asked, 'What would you call that in England?'"*) is promoted to **`PromDepth = 1`** (the main Nucleus of the Root's right branch), whereas Sentence 5 is attached below Sentence 4 as an `Elaboration` satellite at **`PromDepth = 5`** (leaf depth 6).
     2. Sentence 5 is only 4 words long (`"Ostentatious," my wife replied.`), so without Sentence 4's question, Sentence 5 makes no sense on its own!

3. **Q: How could you improve this extractive RST summarizer into an even stronger system?**
   - **Answer:**
     1. **Sub-Sentence EDU Compression:** Instead of extracting full sentences, delete Satellite EDUs *inside* a selected sentence (such as `[EDU 0]: "I don't believe"` or `[EDU 8]: "Rather, I think"` in Paragraph 1) to create tighter, compressed summaries.
     2. **Hybrid Discourse + Lexical Salience:** Combine our learned Logistic Regression RST score with entity/TF-IDF weights so meta-discourse root sentences (like Paragraph 10 Sentence 1: *"This paper is part of an effort to relate various accounts"*) do not beat entity-rich sentences (like Paragraph 10 Sentence 3).
     3. **Anaphora Resolution:** Replace dangling pronouns like *"It"* or *"She"* with their antecedent noun phrase when extracting non-initial sentences.

