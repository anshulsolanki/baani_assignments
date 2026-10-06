# Complete Study Guide: Understanding Context-Free Grammars (CFGs) with NLTK

This guide walks you step-by-step through every concept, grammar rule, and line of Python code in the **Writing Context-Free Grammars using NLTK** assignment so you can understand *why* each solution works and confidently explain it in class or a viva.

---

## 1. Core Concepts: What is a Context-Free Grammar (CFG)?

A **Context-Free Grammar (CFG)** is a formal set of rules used in Computational Linguistics to describe the hierarchical structure (syntax) of sentences in a natural language.

Every CFG has **4 components**:
1. **Terminals ($\Sigma$)**: The actual words in the sentence (e.g., `'joke'`, `'woman'`, `'flying'`, `'planes'`). In NLTK, terminals are always enclosed in quotes (`'...'`) and appear at the **leaves** (bottom) of a parse tree.
2. **Non-Terminals ($V$)**: Syntactic categories or labels that group words and phrases together. They come in two flavors:
   - **Pre-terminal Part-of-Speech (POS) tags**: Categories that directly rewrite to a word (e.g., `Det` = Determiner, `N` = Noun, `V` = Verb, `P` = Preposition, `Adj` = Adjective, `Pro` = Pronoun, `Aux` = Auxiliary).
   - **Phrasal categories**: Larger constituents built from smaller categories (e.g., `S` = Sentence, `NP` = Noun Phrase, `VP` = Verb Phrase, `PP` = Prepositional Phrase).
3. **Productions / Rewrite Rules ($P$)**: Rules of the form `LHS -> RHS` saying *"an `LHS` category can be made out of `RHS`"*.
   - Example: `NP -> Det N | NP PP` is shorthand for two rules:
     - `NP -> Det N` (e.g., *"a joke"*)
     - `NP -> NP PP` (an existing Noun Phrase followed by a Prepositional Phrase forms a larger Noun Phrase)
4. **Start Symbol ($S$)**: The goal category at the **root** (top) of the tree.
   - **Important NLTK Rule**: `CFG.fromstring()` automatically treats the **left-hand side of the very first rule** as the start symbol!
   - In **Part A**, the first rule is `NP -> Det N | NP PP`, so the start symbol is `NP` (because the input is a long noun phrase, not a full sentence).
   - In **Parts B, C, and D**, the first rule is `S -> ...`, so the start symbol is `S` (Sentence).

---

## 2. How Does `nltk.parse.BottomUpChartParser` Work?

When you run:
```python
parser = nltk.parse.BottomUpChartParser(grammar)
for tree in parser.parse(sentence):
    tree.pretty_print()
```
Here is what NLTK does behind the scenes:
1. **Bottom-Up Tagging**: It starts at the individual words at the bottom (`'a'`, `'joke'`, ...) and looks up which POS rules match each word (`'a'` $\leftarrow$ `Det`, `'joke'` $\leftarrow$ `N`).
2. **Combining Adjacent Constituents**: Whenever adjacent categories match the right-hand side of a grammar rule (for instance, `Det` followed by `N` matches `NP -> Det N`), the parser records an `NP` spanning those words in a dynamic programming table called a **chart**.
3. **Finding All Complete Parses**: Because natural language is often **structurally ambiguous**, there can be multiple valid ways to combine constituents across the entire sentence. `parser.parse(sentence)` yields a separate `nltk.tree.Tree` object for **every distinct valid parse tree** whose root is the start symbol.

---

## 3. Walkthrough of Part A (5 Marks)

### Part A.1: Why Are There 5 Parse Trees? (PP-Attachment Ambiguity)

Look at the input phrase:
> **`a joke`** `[PP1 about the woman]` `[PP2 with the umbrella]` `[PP3 on the street]`

It has a base noun phrase (*"a joke"*) followed by **3 Prepositional Phrases (PPs)**, and each PP ends with a noun (`woman`, `umbrella`, `street`).

Because of the recursive rule **`NP -> NP PP`**, each new `PP` has a choice of **which preceding `NP` to attach to**:
- **When $\text{PP}_1$ (*"about the woman"*) arrives**:
  - There is only 1 preceding `NP` (*"a joke"*), so $\text{PP}_1$ must attach to *"a joke"*.
- **When $\text{PP}_2$ (*"with the umbrella"*) arrives**:
  - Who has the umbrella?
  - **Choice A**: It attaches low to **`the woman`** $\rightarrow$ *"the woman who has the umbrella"*.
  - **Choice B**: It attaches high to **`a joke about the woman`** $\rightarrow$ *"a joke (about the woman) told using the umbrella"*.
- **When $\text{PP}_3$ (*"on the street"*) arrives**:
  - What is on the street? The **umbrella**, the **woman**, or the **joke**?

In combinatorics, the number of ways to bracket a base phrase with $k$ modifiers using a binary recursive rule is given by the **$k$-th Catalan Number**:
$$C_k = \frac{1}{k+1}\binom{2k}{k}$$
For $k = 3$ prepositional phrases:
$$C_3 = \frac{1}{4}\binom{6}{3} = \frac{20}{4} = 5\text{ trees}$$

#### Intuitive Summary of All 5 Trees in `Part_A_Parse_Trees.pdf`:
1. **Tree 1**: All three PPs attach to **`a joke`** *(a joke [about the woman], [with the umbrella], [on the street])*.
2. **Tree 2**: *"with the umbrella"* attaches to **`the woman`**; *"on the street"* attaches to **`a joke...`**.
3. **Tree 3**: Both *"with the umbrella"* and *"on the street"* attach to **`the woman`**.
4. **Tree 4**: Cascade attachment: *"on the street"* attaches to **`the umbrella`**, which attaches to **`the woman`**, which attaches to **`a joke`**.
5. **Tree 5**: *"about the woman"* attaches to **`a joke`**; *"on the street"* attaches to **`the umbrella`**, and *"with [the umbrella on the street]"* attaches to **`a joke about the woman`**.

---

### Part A.2: How the Top-Down Recursive Function Works

The question asks us to:
> *"Recurse through each tree top-down fashion (starting from the root node) and print the following information: 1. Number of non-terminal nodes (nodes which aren't words) 2. Print out each word with a numerical index indicating its position in the sentence."*

#### How NLTK Represents a Tree in Python
In NLTK, a parse tree is made of nested `nltk.tree.Tree` objects:
- Every **non-terminal node** (any node that is **not** a word, such as `NP`, `PP`, `Det`, `N`, `P`) is an instance of `nltk.tree.Tree`. Iterating over `for child in node:` iterates over its child branches from left to right.
- Every **terminal leaf node** (an actual word like `'a'`, `'joke'`, `'about'`) is just a Python string (`str`), **not** a `Tree`!

#### Step-by-Step Code Explanation:
```python
def recurse_tree_top_down(node, word_index=None, is_root=True):
    if word_index is None:
        word_index = [0]

    # 1. BASE CASE: If 'node' is NOT an nltk.Tree, it is a word (leaf string)!
    # We print the word and its numerical index directly during the recursion.
    if not isinstance(node, Tree):
        idx = word_index[0]                # 0, 1, 2, ...
        print(f"       Word [{idx:2d}] (Position {idx + 1:2d}): {node}")
        word_index[0] += 1
        return 0, 0                        # A word contributes 0 non-terminal nodes

    # 2. TOP-DOWN (PRE-ORDER) STEP:
    # We count the current non-terminal node FIRST (starting at the root),
    # and then recursively visit each of its children from left to right.
    total_non_terminals = 1
    phrasal_non_terminals = 1 if node.height() > 2 else 0

    for child in node:
        child_total_nt, child_phrasal_nt = recurse_tree_top_down(
            child, word_index=word_index, is_root=False
        )
        total_non_terminals += child_total_nt
        phrasal_non_terminals += child_phrasal_nt

    if is_root:
        pos_nt = total_non_terminals - phrasal_non_terminals
        print(
            f"     Number of non-terminal nodes (nodes which aren't words): {total_non_terminals} "
            f"({phrasal_non_terminals} phrasal nodes [NP, PP] + {pos_nt} POS-tag nodes [Det, N, P])"
        )

    return total_non_terminals, phrasal_non_terminals
```

#### Why is the non-terminal count equal to `21` for all 5 trees?
Even though the 5 trees attach the PPs at different heights, every single tree uses the exact same building blocks:
- **11 POS-tag nodes** (1 above each of the 11 words: `4 Det + 4 N + 3 P = 11`)
- **4 base `NP` nodes** (`NP -> Det N` for *a joke*, *the woman*, *the umbrella*, *the street*)
- **3 `PP` nodes** (`PP -> P NP` for *about...*, *with...*, *on...*)
- **3 combined `NP` nodes** (`NP -> NP PP` to attach each of the 3 PPs)
- **Total non-word nodes** = $11 + 4 + 3 + 3 = \mathbf{21}$ non-terminal nodes (10 phrasal + 11 POS tags)!

---

## 4. Walkthrough of Part B (5 Marks)

### Understanding the Ambiguity in *"They are flying planes"*
Think about two real-life situations where someone says *"They are flying planes"*:
1. **Meaning 1 (Pilots in action)**: Pointing at pilots in the cockpit: *"What are they doing? They are flying planes."*
   - Here, **`are`** is a helping/auxiliary verb (`Aux`), **`flying`** is an action verb (`V`), and **`planes`** is the object (`NP`) of `flying`.
   - Grouping: `[NP They] [VP are [VP flying [NP planes]]]`
2. **Meaning 2 (Describing objects in the sky)**: Pointing at specks in the sky: *"What are those things? They are flying planes (not birds)."*
   - Here, **`are`** is a main linking/copular verb (`V`), and **`flying planes`** is a single Noun Phrase (`NP`) where **`flying`** is an adjective (`Adj`) describing what kind of **`planes`** (`N`) they are.
   - Grouping: `[NP They] [VP are [NP flying planes]]`

### How Our Grammar Satisfies Both Required Facts:
- **Fact (i): *"an NP should be substitutable with a pronoun given the right context"***
  - Instead of writing `S -> Pro VP`, we write `S -> NP VP` and `NP -> Pro` (`Pro -> 'They'`). That way, any `NP` can be replaced by a pronoun!
- **Fact (ii): *"a verb and an immediately following NP can combine to form a VP"***
  - We include the rule `VP -> V NP`.
  - In **Meaning 1**, `V` (`'flying'`) + `NP` (`'planes'`) combine via `VP -> V NP` to form `[VP flying planes]`, and then `Aux` (`'are'`) combines with that `VP` via `VP -> Aux VP`.
  - In **Meaning 2**, `V` (`'are'`) + `NP` (`'flying planes'`) combine directly via `VP -> V NP`!

---

## 5. Walkthrough of Part C (5 Marks)

### Understanding *"Flying planes can be dangerous"*
Here, the ambiguity moves into the **subject** of the sentence (*"Flying planes"*):
1. **Meaning 1 (The activity is dangerous)**: *"Piloting aircraft (`[VP_nf Flying [NP planes]]`) can be dangerous."*
   - Here, `"Flying"` is a non-finite (gerund) verb (`V_nf`) taking `[NP planes]` as its direct object to form a **non-finite Verb Phrase** (`VP_nf -> V_nf NP`).
2. **Meaning 2 (The aircraft themselves are dangerous)**: *"Planes that are in flight (`[NP [Adj Flying] [N planes]]`) can be dangerous."*
   - Here, `"Flying"` is an adjective (`Adj`) modifying the noun `"planes"` (`N`) inside a normal Noun Phrase (`NP -> Adj N`).

### Why Did the Assignment Give That Specific Hint?
> **Hint:** *"A non-finite VP can serve as the subject of an English sentence, such as in the sentences To err is human. It is OK to use a unary rewrite rule with a right-hand-side element that is a phrasal category."*

- A **unary rewrite rule** is a rule with only **one** symbol on the right-hand side (`X -> Y`).
- Normally, a sentence starts with `S -> NP VP`, so the subject position expects an `NP`.
- To allow a non-finite verb phrase (`VP_nf`, a phrasal category) to sit in the subject `NP` slot, we add the unary rule:
  ```text
  NP -> VP_nf
  ```
- Why did the professor specify **non-finite** `VP` (`VP_nf`) instead of just `VP`?
  - Because if you wrote `NP -> VP` and `VP -> V NP` using the same `VP` symbol, a finite verb phrase like *"are flying planes"* could pretend to be a subject, and `NP -> VP -> V NP` could cycle! Separating non-finite `VP_nf` (`flying planes`) from finite `VP` (`can be dangerous`) is both linguistically accurate and prevents parser loops.

---

## 6. Walkthrough of Part D (5 Marks)

### Why Does Changing *"can be"* to *"is"* or *"are"* Eliminate the Ambiguity?
It all comes down to **Subject-Verb Number Agreement**:
1. **Why *"can be"* was ambiguous**:
   - Modal verbs in English (*can, could, may, might, must, should, will, would*) **never change form for singular vs. plural**. You say *"He **can be**..."* (singular) and *"They **can be**..."* (plural). So `"can be dangerous"` happily accepts **both** the singular activity subject and the plural noun phrase subject!
2. **Why *"Flying planes is dangerous"* has ONLY 1 meaning**:
   - **`is`** is strictly **singular** (`V_sg`).
   - When `"Flying planes"` is a non-finite VP (`VP_nf`) meaning *"the act of flying planes"*, an action/clause acting as a subject is always **singular** in English (just like *"To err **is** human"* or *"Swimming in oceans **is** fun"*).
   - Notice that even though `"planes"` is a plural word, in `[VP_nf Flying [NP_pl planes]]` the word `"planes"` is just the object inside the verb phrase—the whole activity itself is singular (`NP_sg -> VP_nf`).
   - Therefore, `"is"` **only** matches the `VP_nf` reading!
3. **Why *"Flying planes are dangerous"* has ONLY 1 meaning**:
   - **`are`** is strictly **plural** (`V_pl`).
   - When `"Flying"` is an adjective modifying the plural head noun `"planes"` (`NP_pl -> Adj N_pl`), the whole Noun Phrase refers to multiple airplanes and is **plural** (`NP_pl`).
   - Therefore, `"are"` **only** matches the `Adj + N_pl` reading!

### How We Encode Number Agreement in a CFG:
In Context-Free Grammars, agreement is encoded by splitting categories into **singular (`_sg`)** and **plural (`_pl`)** subtypes:
- `S -> NP_sg VP_sg | NP_pl VP_pl` (A singular subject MUST pair with a singular VP; a plural subject MUST pair with a plural VP!)
- `NP_sg -> VP_nf` (A non-finite VP subject is singular)
- `NP_pl -> Pro_pl | N_pl | Adj N_pl` (Plural pronouns and plural nouns are plural)
- `VP_sg -> V_sg AdjP | ... | Modal VP_inf` (`V_sg -> 'is'`)
- `VP_pl -> V_pl AdjP | ... | Modal VP_inf` (`V_pl -> 'are'`)

When NLTK parses:
- `"Flying planes is dangerous"` $\rightarrow$ **1 parse** (`NP_sg` + `VP_sg`)
- `"Flying planes are dangerous"` $\rightarrow$ **1 parse** (`NP_pl` + `VP_pl`)
- `"Flying planes can be dangerous"` $\rightarrow$ **2 parses** (because `Modal VP_inf` is valid in both `VP_sg` and `VP_pl`!)
- `"They are flying planes"` $\rightarrow$ **2 parses** (still works seamlessly!)

---

## 7. Quick Viva / Quiz Q&A for Your Daughter

1. **Q: Why does NLTK's `CFG.fromstring()` know whether to start with `NP` (in Part A) or `S` (in Parts B–D)?**
   - **A:** NLTK always takes the left-hand side of the **first production rule** listed in the grammar string as the start symbol.
2. **Q: If we added a 4th prepositional phrase to the sentence in Part A, how many parse trees would the parser emit?**
   - **A:** The 4th Catalan number: $C_4 = \frac{1}{4+1}\binom{8}{4} = 14$ parse trees!
3. **Q: In Part A.2, why does every one of the 5 parse trees have the exact same number of non-terminal nodes (21)?**
   - **A:** Because all 5 trees parse the same 11 words using 11 POS tags, 4 base `Det N` noun phrases, 3 `P NP` prepositional phrases, and 3 `NP PP` attachments ($11 + 4 + 3 + 3 = 21$). Only the *attachment points* change, not the number of rules applied.
4. **Q: In *"Flying planes is dangerous"*, why doesn't the plural word *"planes"* make the verb *"are"*?**
   - **A:** Because in the gerundive reading (`[VP_nf Flying [NP_pl planes]]`), *"planes"* is the direct object of the verb *"Flying"*, not the head of the subject. The subject is the entire non-finite VP clause, and clausal subjects in English are always grammatically singular.
