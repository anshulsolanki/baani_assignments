# Student Profile, Preferences & Collaboration Rules (Baani)

> **About This File**: This is the central configuration and guidelines document for working with **Baani**. It defines student profile details, coding style, workflow preferences, course-specific constraints, and viva preparation standards. Update this document whenever new courses, preferences, or workflow guidelines are added.

---

## 1. Student Profile & Academic Context
- **Student Name**: Baani
- **Academic Standing**: 2nd-Year Undergraduate Student
- **Program / Branch**: B.Tech in Computer Science and Engineering (CSE) / Dual Degree in Computational Linguistics (CLD)
- **Key Courses & Subject Areas**:
  - **Computational Linguistics (CL-1 & CL-2)**: CFGs, Parsing (CYK, Earley), Anaphora Resolution (Hobbs' algorithm), NLTK, Paninian grammar framework.
  - **Operating Systems and Networks (OSN)**: Systems programming in C, concurrency, multithreading, sockets, scheduling, memory management.
  - **Core CS**: Data structures, algorithms, discrete mathematics, network structures.

---

## 2. Coding Style & Persona (2nd-Year CS Student)
- **Perspective**: Always write code from the perspective of a bright, diligent 2nd-year CS student—never like an enterprise architect, senior dev, or over-engineered framework.
- **Keep Code Simple, Clean & Direct**:
  - Prefer simple, standard control flows: straightforward `for`/`while` loops, `if/else` branching, basic functions, simple dictionaries, lists, and tuples.
  - **Avoid Over-Engineering & Advanced Idioms**:
    - No nested closures with `nonlocal`.
    - No heavy or advanced decorators (`@staticmethod`, `@classmethod`, `@dataclass`, custom decorators).
    - No complex type-hint gymnastics (`Callable`, `TypeVar`, `Protocol`).
    - No metaclasses, reflection, or deeply nested multi-line comprehensions.
  - **Meaningful, Natural Variable Names**: Use clear names matching the assignment terminology (e.g., `candidates`, `score`, `best_tag`, `words`, `grammar_rules`, `transition_probs`).

---

## 3. Technical Scope & Library Policy
- **Standard Library First**:
  - **Python**: Stick to the standard library (`os`, `sys`, `math`, `random`, `collections`, `csv`, `re`, `itertools`, `json`).
  - **C**: Stick to standard C libraries (`stdio.h`, `stdlib.h`, `string.h`, `unistd.h`, `pthread.h`, `sys/types.h`, `sys/socket.h`).
- **Course-Approved Libraries Only**:
  - Only import course-approved third-party libraries explicitly mentioned in the assignment sheet (e.g., `nltk` for NLP/CL assignments).
  - **Do NOT use unauthorized packages**: Avoid `pandas`, `scipy`, `torch`, `spacy`, `transformers`, `seaborn`, etc., unless a specific question or bonus/extra-credit explicitly requires them (e.g., `scikit-learn` for comparative analysis).
- **From-Scratch Implementations**:
  - Whenever an assignment requires implementing an algorithm (e.g., Logistic Regression, HMM, Viterbi, CYK parsing, Hobbs' Algorithm), build the math and algorithmic logic **from scratch** with transparent loops and arithmetic so every step can be explained during evaluation.

---

## 4. Code Structure & Modularization (1-to-1 Mapping)
- **Direct 1-to-1 Problem Mapping**:
  - Follow the exact numbering from the assignment prompt (`Problem 1`, `Problem 2`, `Problem 3`, ...).
  - Above each problem function, include a clear docstring summarizing what the problem asks and any specific rubric requirements.
  - Define dedicated functions for each problem (`problem_1()`, `problem_2()`, ...) and invoke them sequentially in `main()`:
    ```python
    def main():
        # Load and prepare shared data
        ...
        print("=== Problem 1 ===")
        problem_1(...)

        print("\n=== Problem 2 ===")
        problem_2(...)
    ```
- **Modular, Focused Helper Functions**:
  - Avoid giant monolithic blocks of code.
  - Keep each function focused and concise (**20–45 lines max**), maintaining at most 2–3 levels of indentation.
  - Separate data loading, core computation, and output formatting cleanly.

---

## 5. Workflow: Read First, Clarify Before Coding
- **Step 1 — Thorough Review**: Carefully read the entire assignment handout, specification, dataset description, deliverables checklist, and any referenced textbook chapters or lecture notes.
- **Step 2 — Clarify Ambiguities**: Check for missing datasets, ambiguous conventions, edge cases, or platform constraints (e.g., Linux vs. macOS) before generating solutions.
- **Step 3 — Complete Requirement Verification**:
  - Ensure every sub-part of every problem is addressed (e.g., *"analyze qualitatively and quantitatively"*, *"suggest potential improvements"*).
  - Verify that both console output and written report/deliverables answer all rubric criteria.

---

## 6. Mandatory Viva & Study Preparation Guide (`.md`)
For every assignment, alongside code and written reports, a dedicated markdown guide (e.g., `Viva_Preparation_Guide.md` or `Understanding_and_Viva_Guide.md`) **must** be created containing:
1. **Concept & Problem Walkthrough**:
   - Plain-English theoretical background behind the assignment.
   - Step-by-step explanation of the implementation with direct mappings to functions in the code.
2. **Key Viva Pointers ("What to Show the TA")**:
   - Exact line numbers and functions to highlight when explaining how the solution works.
   - Clear explanations of experimental numbers/results and *why* one model/method outperformed another.
3. **Likely Viva Questions & Model Answers**:
   - 10–15 realistic viva questions an instructor or TA could ask (covering conceptual theory, edge cases, algorithmic complexity, hyperparameters, and hypothetical "what if you changed X?" questions).
   - Concise, confident, ready-to-speak model answers.

---

## 7. Submission Deliverables & Quality Standards
- **Reports**: Clearly formatted, addressing both quantitative metrics (accuracy, F1-score, execution time) and qualitative error analysis with sample outputs.
- **Reproducibility**: Include exact commands to run the code, seed values for random processes, and straightforward execution instructions.
- **Packaging**: When a zip or tarball is required, ensure directory structures strictly follow the assignment instructions without unnecessary hidden or cache files (`.DS_Store`, `__pycache__`).

---

## 8. Preferences & Changelog
*(This section tracks custom preferences and updates over time)*

| Date | Category | Update / Preference Added |
| :--- | :--- | :--- |
| **2026-10-18** | Persona & Style | Initial assignment guidelines and 2nd-year CS student persona established. |
| **2026-11-08** | Profile & Routine | Consolidated comprehensive `GEMINI.md` profile covering course history (CL1/CL2, OSN), modularization rules, from-scratch policy, and viva preparation requirements. |
