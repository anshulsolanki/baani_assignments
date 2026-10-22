# CL2 Project Proposal — Viva & Proposal Defense Guide (For Baani & Yashaswi)

This guide prepares you to present and defend your new Computational Linguistics 2 project proposal to **Prof. Parameswari Krishnamurthy**, **Prof. Rajakrishnan Rajkumar**, and your TAs.

---

## 1. 30-Second Elevator Pitch (What to Say First)

> *"In our project, we are tackling a classic failure mode of Bag-of-Words sentiment analysis using three core concepts from Computational Linguistics 2: **Compositional Semantics**, **Pronominal Anaphora Resolution**, and **Rhetorical Structure Theory (RST)**.*
>
> *When a review says, 'Although the cinematography was breathtaking, the plot was predictable and boring,' a Bag-of-Words classifier sees two positive words and two negative words and gets confused. Using **RST**, we segment sentences into Elementary Discourse Units (EDUs) and use discourse connectives like 'although', 'however', and 'despite' to weight the **Nucleus** clause higher than the **Satellite** clause. Second, using **Anaphora Resolution and Binding Theory**, we resolve pronouns (`he, she, it, they`) across sentences so we know whether an opinion word actually modifies a central topic of the review. Third, we apply **Compositional Semantic Shifters**—syntactic negation scope, intensifiers, and irrealis modals—over the MPQA and Hu–Liu polarity lexicons. Finally, we train **Naive Bayes** and **Logistic Regression** classifiers across an ablation study (`M0` to `M4`) on the Cornell Movie Review dataset to measure the exact contribution of each linguistic layer."*

---

## 2. Key Pointers: Why This Proposal Directly Fixes Every Issue from Proposal 1

1. **No Neural Networks / No Pre-trained LLMs:**
   - Proposal 1 used HuggingFace transformers and Qwen-2.5. Our new proposal uses **100% classical statistical models (Naive Bayes & Logistic Regression)** and **explicit linguistic rules**.
2. **Deep Linguistic Knowledge (Semantics + Discourse + Pragmatics):**
   - **Lexical & Compositional Semantics:** Prior polarity lexicons (MPQA, Hu–Liu) + syntactic negation scope + intensifiers/downtoners + irrealis modals (Taboada et al., 2011).
   - **Discourse (RST):** Elementary Discourse Unit (EDU) segmentation + Nucleus vs. Satellite weighting across *Concession*, *Contrast*, *Cause*, and *Condition* relations (Mann & Thompson, 1988; Bhatia et al., 2015).
   - **Syntax–Pragmatics Interface (Anaphora & Binding Theory):** Pronominal anaphora resolution (`he, she, it, they`) to track entity salience across sentence boundaries (Jakob & Gurevych, 2010).
3. **Zero Human Evaluation Required:**
   - Proposal 1 needed human doctors/annotators to judge medical summaries. Here, evaluation is **100% objective and automatic** using gold sentiment labels on the **Cornell Movie Review Dataset (Pang & Lee, 2004)** via Precision, Recall, Macro-F1, Confusion Matrices, and an Ablation Study (`M0` $\to$ `M4`).
4. **Realistic & Manageable Scope ("Small/Medium Bone" Research):**
   - Instead of trying to build a full-tree open-domain discourse parser from scratch, we focus on **connective-anchored intra-sentential and adjacent-sentence EDUs** (~45 explicit discourse connectives), where Nucleus/Satellite directionality is well-defined and reliable.

---

## 3. Likely Proposal Viva Questions & Model Answers

### Q1: Why did you choose Movie Reviews (`nltk.corpus.movie_reviews`) as your dataset instead of short tweets?
**Answer:**  
Short tweets are often single clauses with slang, where discourse structure and cross-sentence anaphora barely appear. Full-length movie reviews (Pang & Lee, 2004) are multi-paragraph texts where reviewers constantly compare pros and cons using **concessive and contrastive RST relations** (*"While the acting was great, the script failed"*) and refer back to the film, director, and actors using **pronouns (`it, he, she, they`)** across sentences. This makes movie reviews the ideal testbed for RST + Anaphora + Compositional Semantics.

---

### Q2: How will you segment sentences into Elementary Discourse Units (EDUs) without using a neural RST parser?
**Answer:**  
We use a two-step rule-based syntactic approach in NLTK:
1. First, we run POS tagging and a Context-Free Grammar (`RegexpParser`) chunker to identify clause boundaries (`S`, `SBAR`, `VP`) and punctuation delimiters (commas, semicolons, dashes).
2. Second, we match explicit **discourse connectives** (~45 markers grouped into *Concession*, *Contrast*, *Cause*, and *Condition*). When a connective like *"although"* introduces a subordinate clause (`[Although S1], [S2]`), `S1` is segmented as the **Satellite EDU** and the main clause `S2` is segmented as the **Nucleus EDU**.

---

### Q3: In Rhetorical Structure Theory (RST), what is the difference between a Nucleus and a Satellite, and how do you weight them?
**Answer:**  
In Mann & Thompson's (1988) RST framework, the **Nucleus** embodies the writer's central claim or essential information (if you delete the Nucleus, the text loses its point), whereas the **Satellite** provides supporting background, condition, or a conceded counterpoint.
- For **Concession** (*"Although $S_1$, $N_2$"*) and **Antithesis/Contrast** (*"$S_1$, however $N_2$"*), the clause expressing the author's final judgment is the **Nucleus**.
- In our feature representation and lexicon scorer, sentiment words inside a **Nucleus EDU** are multiplied by a weight $w_N > 1.0$ (e.g., $1.5$), while sentiment words inside a **Concessive Satellite EDU** are downweighted by $w_S < 1.0$ (e.g., $0.4$), tuned on the development split.

---

### Q4: Some discourse words like *"while"* or *"since"* are ambiguous (polysemous). How will your system handle that?
**Answer:**  
That is one of our main linguistic challenges!
- *"While"* can be **Temporal** (*"While walking home, he saw..."*) or **Concessive** (*"While the acting is impressive, the plot is weak"*).
- *"Since"* can be **Temporal** (*"since 1998"*) or **Causal** (*"since the script was rushed"*).
- We disambiguate them using **POS and syntactic subcategorization rules**:
  - If `while` is followed immediately by a gerund (`VBG`) or time expression, it is tagged as **Temporal** (neutral weight $1.0$).
  - If `while` introduces a finite clause (`NP + finite VP`) whose lexicon polarity opposes the main clause, it is tagged as **Concessive** (Satellite weight $w_S$).
  - Similarly, `since` followed by a temporal NP (`CD` year / date) is Temporal, whereas `since` followed by a finite clause (`S`) is Causal.

---

### Q5: How does Anaphora Resolution help Document-Level Sentiment Classification?
**Answer:**  
In a multi-sentence review, a reviewer often mentions background entities (e.g., a prequel, a book, or a minor character) alongside the main film/director, and then uses pronouns (`it, he, she, they`) in subsequent sentences:
- Example: *"The film is based on a 1990 novel. It was a literary triumph, but this adaptation ruins the pacing."*
- Without anaphora resolution, `"literary triumph"` adds strong positive score to the review.
- By running our **Pronominal Anaphora Resolver** (using Binding Theory intra-sentential filters + Hobbs' / feature-based antecedent selection over a 2-sentence window), we link each pronoun to its antecedent NP. We track the **entity frequency (discourse salience)** of each NP across the document so sentiment predicates modifying the central topic receive higher weight than remarks about peripheral entities.

---

### Q6: What are "Compositional Semantic Shifters" and why isn't simple lexicon lookup enough?
**Answer:**  
Simple lexicon lookup assigns fixed prior polarity to isolated words (e.g., *good* = $+1$, *great* = $+2$). However, natural language meaning is **compositional** (Frege's Principle):
1. **Syntactic Negation Scope:** Words like *not, never, neither, barely, without* invert or shift polarity—not just of the very next word, but across their **syntactic clause scope** (e.g., *"does not ever manage to be convincing"*). We propagate negation from the cue word up to the next clause/punctuation boundary.
2. **Intensifiers & Downtoners:** Degree adverbs scale valence multiplicatively (*"utterly brilliant"* $\to \times 1.8$; *"somewhat flawed"* $\to \times 0.5$).
3. **Irrealis / Presuppositional Modals:** Counterfactual modals (*would, could, should, might*) and expectation verbs (*hoped, expected*) indicate that the positive/negative state did **not** actually happen in reality (e.g., *"It could have been a masterpiece"* is actually negative/disappointed!). We dampen or invert polarity inside irrealis modal scopes.

---

### Q7: Why are you comparing Naive Bayes and Logistic Regression across an Ablation Study (`M0` to `M4`)?
**Answer:**  
- **Naive Bayes** is a **generative** model that assumes conditional independence between features given the class label. When we add correlated linguistic features (like unigrams + lexicon counts + negated unigrams + RST-weighted scores), Naive Bayes double-counts correlated evidence.
- **Logistic Regression** is a **discriminative** linear classifier optimized via gradient descent with L2 regularization, which naturally handles correlated, overlapping linguistic features by adjusting feature weights.
- Running a step-by-step **Ablation Study (`M0` $\to$ `M1` $\to$ `M2` $\to$ `M3` $\to$ `M4`)** lets us prove objectively how much each linguistic module (Lexicons, Compositional Shifters, Anaphora Salience, and RST Nuclearity) improves F1 score.

---

### Q8: What is the "Hard Contrastive-Discourse Subset" mentioned in your proposal?
**Answer:**  
In the full 2,000-review dataset, some reviews are straightforwardly 100% positive or 100% negative in every sentence—even a simple Bag-of-Words model gets those right. To clearly highlight the power of semantics and discourse, we also evaluate all models on a **Hard Contrastive Subset** of test reviews that contain high density of concessive/contrastive connectives (*although, however, but, despite, whereas*) and multiple third-person pronouns. On this subset, Bag-of-Words struggles, whereas our RST + Anaphora + Compositional model is designed to excel.

---

### Q9: How is the work divided between Yashaswi and Baani so that both contribute equally?
**Answer:**  
We split both the **linguistic engineering** and the **statistical classifiers** 50/50 into separate Python modules:
- **Yashaswi (`2025114007`)** builds the **Lexical & Compositional Semantics pipeline** (`lexicon_semantics.py`, `compositional_rules.py` — MPQA/Hu–Liu integration, syntactic negation scope, intensifiers/downtoners, irrealis modals) and implements the **Naive Bayes classifier & SO-CAL rule-based scorer** (`naive_bayes_model.py`).
- **Baani (`2025114016`)** builds the **RST Discourse & Anaphora Salience pipeline** (`rst_discourse.py`, `anaphora_salience.py` — EDU segmentation, connective classification, Nucleus/Satellite weighting, pronoun resolution) and implements the **L2 Logistic Regression classifier** (`logistic_regression_model.py`).
- Both collaborate on running the `M0`–`M4` ablation study, confusion matrices, and writing the final report, with independent commits pushed regularly across the timeline.
