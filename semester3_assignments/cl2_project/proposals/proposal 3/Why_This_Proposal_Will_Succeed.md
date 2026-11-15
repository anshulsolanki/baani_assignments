# Why Proposal 3 Will Succeed: Direct Alignment with the Professor's Feedback

**Project Title:** *Linguistically Guided Extractive Medical Summarization: From RST, Syntactic Parsing, and Semantic Representations to Feature-Driven Logistic Regression and Clinical Utility Evaluation*  
**Team:** Yashaswi Priya (`2025114007`) & Baani Solanki (`2025114016`)

---

## 1. It Executes the Exact 4-Step Blueprint Given by the Professor

In `baani-cl2_proj_proposal-professor-comments.pdf`, the professor did not ask you to abandon the medical domain (`BioLaySumm2025-PLOS` and `BioLaySumm2025-eLife`). Instead, the professor gave you the exact recipe to turn medical summarization into a **Computational Linguistics 2** project:

> **Professor's Note (Sections 3 & 4):**  
> *"Implement a summarization method rule-based on features, fine-tune it using linguistic summarization...*  
> *`RULE BASED SUMMARIZATION -> THEN RULES TO FEATURES FOR LOGI REG -> GUIDE A MODEL USING THESE FEATURES -> fine-tune model using best-performing features`"*

### How Our Proposal Operationalizes Every Arrow (`->`) in That Blueprint:

1. **`RULE BASED SUMMARIZATION` (`Stage 1`):**  
   We design a modular, rule-based extractive summarizer incorporating the exact five methods listed in Section 6 of the professor's comments:
   - **`TF-IDF`:** Lexical salience of domain-specific medical terms.
   - **`TextRank`:** Graph-based sentence centrality via lexical/synset overlap (Mihalcea & Tarau, 2004).
   - **`RST` (Rhetorical Structure Theory):** Elementary Discourse Unit (EDU) segmentation and Nucleus ($w_N > 1$) vs. Satellite ($w_S < 1$) weighting using biomedical discourse markers (*Conclusion/Result, Contrast, Cause, Concession* — Marcu, 2000).
   - **`Use a Parser` (Syntactic CFG Parser + Anaphora):** Using NLTK's POS + Context-Free Grammar (`RegexpParser`) parser to verify main-clause `[Subject-NP + Finite-VP + Object-NP]` completeness, prune parenthetical citation noise, and resolve dangling initial pronouns (*it, they, this*) via **Anaphora Resolution**.
   - **`Meaning or Semantic Representation`:** Extracting structured **Predicate–Argument Semantic Triples** (`<Intervention/Agent, Clinical-Predicate, Symptom/Disease>`), mapping words to **Symptom / Disease / Treatment** concepts, and tracking **syntactic negation scope** (*no, not, without*) and **numeric evidence**.

2. **`THEN RULES TO FEATURES FOR LOGI REG` (`Stage 2`):**  
   Each of the 15 linguistic and statistical rules is converted into a normalized feature $f_k(s_i)$ in a 15-dimensional sentence feature vector $\mathbf{x}_i \in \mathbb{R}^{15}$. Using **Greedy Oracle ROUGE Labeling** against the gold `BioLaySumm2025` summaries, each training sentence receives a binary target label $y_i \in \{0, 1\}$.

3. **`GUIDE A MODEL USING THESE FEATURES` (`Stage 3`):**  
   We train a custom from-scratch **L2-Regularized Logistic Regression classifier** $P(y_i = 1 \mid \mathbf{x}_i) = \sigma(\mathbf{w}^\top \mathbf{x}_i + b)$ (alongside Kupiec et al.'s 1995 **Naive Bayes** sentence classifier) to rank and extract the most informative sentences.

4. **`FINE-TUNE MODEL USING BEST-PERFORMING FEATURES` (`Stage 4`):**  
   By inspecting the learned Logistic Regression weights $|w_j|$ and running systematic feature-group ablations (`Statistical/Graph` vs. `RST Discourse` vs. `Syntactic Parser` vs. `Semantic Representation`), we identify the highest-performing linguistic features, prune redundant/noisy features, and fine-tune the final model—paired with an **Anaphora & RST Coherence Post-Processor**.

---

## 2. How We Integrated `"SYMPTOMS TO DISEASE CLASSIFICATION"` to Replace Human Evaluation

In the preliminary draft (`baani-cl2_proj_proposal_preliminary.pdf`), one major issue was relying on **Human Evaluation** (which is impractical for medical texts). At the bottom of `baani-cl2_proj_proposal-professor-comments.pdf`, the note **`SYMPTOMS TO DISEASE CLASSIFICATION`** was added.

We integrated **Symptoms-to-Disease Classification** in a way that strengthens the entire project:
- **As an Extrinsic Clinical Utility Metric (Replacing Human Evaluation):**  
  How do we prove objectively that a medical summary preserved the article's core diagnostic meaning? We train a non-neural **Symptoms-to-Disease / Biomedical Condition Classifier** (Naive Bayes & Logistic Regression) and test how accurately it predicts the target disease/condition using **only the generated summary**!
- **Combined with `ROUGE-1/2/L` and the `Python Rule-Based Keyword & Numeric Regex Checker`**, this gives you a **3-tier automatic evaluation** that requires zero human annotators while directly testing clinical meaning preservation.

---

## 3. Why Proposal 3 Is the Best Option to Show the Professor Who Reviewed Your First Draft

If you are submitting back to the **same professor** who gave you the comments in `baani-cl2_proj_proposal-professor-comments.pdf`:
- Professors love seeing that a team **listened carefully to their exact suggestions** and turned their rough whiteboard/meeting notes into a structured, mathematically clear, well-referenced research plan.
- Every single phrase from `baani-cl2_proj_proposal-professor-comments.pdf` (`Rule-based summarization -> Rules to features for Logistic Regression -> Fine-tune using best features`, `TF-IDF`, `TextRank`, `RST`, `use a parser`, `meaning or semantic representation`, `ROUGE-1/2/L`, `Python rule-based keyword & numeric regex checker`, and `Symptoms to Disease Classification`) appears explicitly in **[`CL2_Project_Proposal_1Page.pdf`](file:///Users/solankianshul/Documents/projects/temp_work/baani_work/assignments/semester3/cl2_project/proposal%203/CL2_Project_Proposal_1Page.pdf)** and **[`CL2_Project_Proposal_Detailed.md`](file:///Users/solankianshul/Documents/projects/temp_work/baani_work/assignments/semester3/cl2_project/proposal%203/CL2_Project_Proposal_Detailed.md)**.
