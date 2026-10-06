# Assignment Report: Writing Context-Free Grammars using NLTK

---

## Part A (5 Marks)

### Question A.1: Visualizing the 5 Parse Trees Emitted by the NLTK Parser

#### Grammar & Input Sentence
```python
import nltk
from nltk import Nonterminal, nonterminals, Production, CFG

grammar = CFG.fromstring("""
NP -> Det N | NP PP
PP -> P NP
Det -> 'the' | 'a' | 'an'
N -> 'joke' | 'woman' | 'umbrella' | 'street'
P -> 'about' | 'with' | 'on'
""")

parser = nltk.parse.BottomUpChartParser(grammar)
sentence = [
    'a', 'joke', 'about', 'the', 'woman',
    'with', 'the', 'umbrella', 'on', 'the', 'street'
]
```

#### Why the Parser Emits Exactly 5 Parse Trees (PP-Attachment Ambiguity)
The noun phrase contains a base `NP` (*"a joke"*) followed by **three Prepositional Phrases (PPs)**:
- $\text{PP}_1$: *"about the woman"*
- $\text{PP}_2$: *"with the umbrella"*
- $\text{PP}_3$: *"on the street"*

Because the recursive rule `NP -> NP PP` allows any `PP` to attach to any preceding `NP` along the right spine of the tree, $k = 3$ prepositional phrases yield the $3\text{rd}$ Catalan number of distinct binary attachment structures:
$$C_3 = \frac{1}{3+1}\binom{6}{3} = 5\text{ parses}$$

| Tree # | Bracketed Constituency Structure | Semantic Interpretation |
| :---: | :--- | :--- |
| **Tree 1** | `[[[[a joke] [about the woman]] [with the umbrella]] [on the street]]` | All 3 PPs modify **the joke**: the joke is *about the woman*, is told *with the umbrella*, and takes place *on the street*. |
| **Tree 2** | `[[[a joke] [about [[the woman] [with the umbrella]]]] [on the street]]` | *"with the umbrella"* modifies **the woman**; *"about [the woman with the umbrella]"* and *"on the street"* modify **the joke**. |
| **Tree 3** | `[[a joke] [about [[[the woman] [with the umbrella]] [on the street]]]]` | Both *"with the umbrella"* and *"on the street"* modify **the woman**; the joke is about that woman. |
| **Tree 4** | `[[a joke] [about [[the woman] [with [[the umbrella] [on the street]]]]]]` | Right-branching cascade: *"on the street"* modifies **the umbrella**, which modifies **the woman**, which modifies **the joke**. |
| **Tree 5** | `[[[a joke] [about the woman]] [with [[the umbrella] [on the street]]]]` | *"about the woman"* modifies **the joke**; *"on the street"* modifies **the umbrella**; *"with [the umbrella on the street]"* modifies **the joke**. |

*(Full-page vector visualizations of all 5 trees are provided in `Part_A_Parse_Trees.pdf` and embedded below.)*

---

### Question A.2: Top-Down Recursive Traversal of Each Tree

#### Recursive Top-Down Function
```python
from nltk.tree import Tree

def recurse_tree_top_down(node, word_index=None, is_root=True):
    """
    Recurses through an NLTK parse tree in top-down (pre-order) fashion starting
    from the root node and prints:
      1. Number of non-terminal nodes (nodes which aren't words)
      2. Each word with a numerical index indicating its position in the sentence.
    """
    if word_index is None:
        word_index = [0]

    # Base Case: Leaf node (a terminal word string, not an nltk.Tree)
    if not isinstance(node, Tree):
        idx = word_index[0]
        print(f"       Word [{idx:2d}] (Position {idx + 1:2d}): {node}")
        word_index[0] += 1
        return 0, 0

    # Top-Down Step: Count current non-terminal node first (root -> children)
    total_non_terminals = 1
    phrasal_non_terminals = 1 if node.height() > 2 else 0

    if is_root:
        print("  -> Top-down recursive traversal starting from root node:")
        print("     Words with numerical index indicating position in the sentence:")

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

#### Output for Each of the 5 Parse Trees
Every tree emitted for this 11-word sentence has the exact same number of non-terminal nodes and word positions (because every tree uses 4 base `NP -> Det N` rules, 3 `PP -> P NP` rules, 3 `NP -> NP PP` rules, and 11 POS-tag rules `Det`/`N`/`P`):

- **1. Number of non-terminal nodes (nodes which aren't words):** **`21`** across each of Trees 1–5
  - Breakdown: **`10`** internal phrasal non-terminal nodes (`7 NP` + `3 PP`) + **`11`** pre-terminal POS-tag nodes (`4 Det` + `4 N` + `3 P`) = **`21` total non-word nodes**.
- **2. Words with numerical index indicating position in the sentence** (identical across Trees 1–5):

```text
Index  0 (Position  1): a
Index  1 (Position  2): joke
Index  2 (Position  3): about
Index  3 (Position  4): the
Index  4 (Position  5): woman
Index  5 (Position  6): with
Index  6 (Position  7): the
Index  7 (Position  8): umbrella
Index  8 (Position  9): on
Index  9 (Position 10): the
Index 10 (Position 11): street
```

---

## Part B (5 Marks)

### Question: Capture the Structural Ambiguity in *"They are flying planes"*

#### Linguistic Analysis & Design Constraints
The sentence *"They are flying planes"* exhibits both **lexical** and **structural** ambiguity:
1. **Progressive Action Reading (*"They [e.g., pilots] are piloting planes"*):**
   - *"are"* is an auxiliary verb (`Aux -> 'are'`).
   - *"flying"* is a transitive verb (`V -> 'flying'`) that combines with the immediately following noun phrase *"planes"* (`NP -> N -> 'planes'`) via `VP -> V NP` to form an inner `VP` (`[VP [V flying] [NP planes]]`).
   - The auxiliary *"are"* combines with that inner `VP` via `VP -> Aux VP`.
2. **Copular / Predicative NP Reading (*"Those objects in the sky are planes that fly"*):**
   - *"are"* is a main copular verb (`V -> 'are'`).
   - *"flying"* is an adjective/participle (`Adj -> 'flying'`) modifying *"planes"* (`N -> 'planes'`) to form the noun phrase `[NP [Adj flying] [N planes]]`.
   - The verb *"are"* combines with the immediately following `NP` via `VP -> V NP`.

Both required facts are respected:
- **(i) An NP is substitutable with a pronoun given the right context:** Captured by `NP -> Pro` (`Pro -> 'They' | 'they'`).
- **(ii) A verb and an immediately following NP can combine to form a VP:** Captured by `VP -> V NP`.

#### Part B Grammar
```python
grammar_b = CFG.fromstring("""
S -> NP VP
VP -> Aux VP | V NP
NP -> Pro | N | Adj N
Pro -> 'They' | 'they'
Aux -> 'are'
V -> 'are' | 'flying'
Adj -> 'flying'
N -> 'planes'
""")
```

#### Emitted Parse Trees (2 Parses)
```text
Parse 1 (Progressive Action):              Parse 2 (Copular Description):
          S                                          S
  ________|____                              ________|____
 |             VP                           |             VP
 |     ________|_____                       |     ________|_____
 |    |              VP                     NP   |              NP
 |    |         _____|____                  |    |         _____|____
 NP   |        |          NP               Pro   V       Adj         N
 |    |        |          |                 |    |        |          |
Pro  Aux       V          N                They are     flying     planes
 |    |        |          |
They are     flying     planes
```

---

## Part C (5 Marks)

### Question: Extend the Grammar for *"Flying planes can be dangerous"*

#### Linguistic Analysis & Use of the Hint
In *"Flying planes can be dangerous"*, the subject *"Flying planes"* has two distinct syntactic structures:
1. **Non-Finite Verb Phrase Subject (*"The activity of flying planes can be dangerous"*):**
   - *"Flying"* (`V_nf`) combines with its object `[NP [N planes]]` to form a non-finite verb phrase: `VP_nf -> V_nf NP`.
   - Following the **Hint** (*"A non-finite VP can serve as the subject of an English sentence... It is OK to use a unary rewrite rule with a right-hand-side element that is a phrasal category"*), we introduce the unary rewrite rule:
     ```
     NP -> VP_nf
     ```
     which allows the non-finite `VP_nf` to occupy the subject `NP` position in `S -> NP VP`.
2. **Modified Noun Phrase Subject (*"Aircraft that are flying can be dangerous"*):**
   - *"Flying"* (`Adj`) modifies the noun *"planes"* (`N`) directly via `NP -> Adj N`.

Meanwhile, the predicate *"can be dangerous"* is formed by the modal auxiliary `Modal -> 'can'` combining with `[VP [V be] [AdjP [Adj dangerous]]]` via `VP -> Modal VP` and `VP -> V AdjP`.

#### Part C Extended Grammar
```python
grammar_c = CFG.fromstring("""
S -> NP VP
VP -> Aux VP_nf | Modal VP | V NP | V AdjP
VP_nf -> V_nf NP
NP -> Pro | N | Adj N | VP_nf
AdjP -> Adj
Pro -> 'They' | 'they'
Aux -> 'are'
Modal -> 'can'
V -> 'are' | 'be'
V_nf -> 'flying' | 'Flying'
Adj -> 'flying' | 'Flying' | 'dangerous'
N -> 'planes'
""")
```

#### Emitted Parse Trees (2 Parses)
```text
Parse 1 (Non-Finite VP Subject):                  Parse 2 (Modified Noun Phrase Subject):
                      S                                               S
          ____________|____                               ___________|____
         NP                VP                            |                VP
         |             ____|___                          |            ____|___
       VP_nf          |        VP                        |           |        VP
   ______|_____       |     ___|______                   |           |     ___|______
  |            NP     |    |         AdjP                NP          |    |         AdjP
  |            |      |    |          |             _____|____       |    |          |
 V_nf          N    Modal  V         Adj          Adj         N    Modal  V         Adj
  |            |      |    |          |            |          |      |    |          |
Flying       planes  can   be     dangerous      Flying     planes  can   be     dangerous
```

---

## Part D (5 Marks)

### Question: Disambiguation When Changing *"can be"* to *"is"* or *"are"*

#### 1. Why is the Ambiguity Eliminated?
The ambiguity in *"Flying planes can be dangerous"* arises because the modal auxiliary **"can"** (`can be`) is **uninflected for grammatical number**—it accepts both singular and plural subjects indiscriminately.

When *"can be"* is replaced by **"is"** or **"are"**, **Subject-Verb Number Agreement** forces a single interpretation:
- **Case 1: *"Flying planes is dangerous"* (Singular Agreement $\rightarrow$ Non-Finite VP Subject Only):**
  - The verb **"is"** (`V_sg`) is 3rd-person **singular** and requires a grammatically **singular subject** (`NP_sg`).
  - When *"Flying planes"* is a non-finite verb phrase (`VP_nf -> V_nf NP_pl`, denoting the *activity* of flying planes), clausal/gerundive subjects in English are always grammatically **singular** (just like *"To err **is** human"*).
  - The plural noun *"planes"* is embedded inside `VP_nf` as the direct object of *"Flying"*, not the head of the subject phrase, so it does not trigger plural verb agreement.
- **Case 2: *"Flying planes are dangerous"* (Plural Agreement $\rightarrow$ Modified Plural NP Subject Only):**
  - The verb **"are"** (`V_pl`) is **plural** and requires a **plural subject** (`NP_pl`).
  - When *"Flying"* is an adjective modifying the plural head noun *"planes"* (`NP_pl -> Adj N_pl`, denoting *aircraft that fly*), the head of the noun phrase is plural, which agrees exclusively with **"are"**.

#### 2. Modified Grammar Capturing Number Agreement Disambiguation
We split `NP`, `VP`, `Aux`, and `V` by grammatical number (`_sg` for singular, `_pl` for plural):
- `S -> NP_sg VP_sg | NP_pl VP_pl` enforces subject-verb number agreement at the sentence level.
- `NP_sg -> VP_nf` captures the fact that a non-finite VP subject is singular.
- `NP_pl -> Pro_pl | N_pl | Adj N_pl` captures plural noun phrases (*"They"*, *"planes"*, *"flying planes"*).
- `VP_sg -> Modal VP_inf` and `VP_pl -> Modal VP_inf` capture why *"can be"* remains ambiguous across both singular and plural subjects.

```python
grammar_d = CFG.fromstring("""
S -> NP_sg VP_sg | NP_pl VP_pl
NP_sg -> VP_nf
NP_pl -> Pro_pl | N_pl | Adj N_pl
VP_nf -> V_nf NP_pl
VP_sg -> V_sg AdjP | V_sg NP_sg | Aux_sg VP_nf | Modal VP_inf
VP_pl -> V_pl AdjP | V_pl NP_pl | Aux_pl VP_nf | Modal VP_inf
VP_inf -> V_inf AdjP
AdjP -> Adj
Pro_pl -> 'They' | 'they'
Aux_sg -> 'is'
Aux_pl -> 'are'
V_sg -> 'is'
V_pl -> 'are'
V_inf -> 'be'
V_nf -> 'flying' | 'Flying'
Modal -> 'can'
Adj -> 'flying' | 'Flying' | 'dangerous'
N_pl -> 'planes'
""")
```

#### 3. Verification Output from NLTK Parser
1. **`"Flying planes is dangerous"` $\rightarrow$ 1 Parse Only (Singular Non-Finite VP Subject):**
```text
                     S
          ___________|_________
       NP_sg                   |
         |                     |
       VP_nf                 VP_sg
   ______|_____           _____|_______
  |          NP_pl       |            AdjP
  |            |         |             |
 V_nf         N_pl      V_sg          Adj
  |            |         |             |
Flying       planes      is        dangerous
```

2. **`"Flying planes are dangerous"` $\rightarrow$ 1 Parse Only (Plural Modified NP Subject):**
```text
                     S
          ___________|_________
         |                   VP_pl
         |                _____|_______
       NP_pl             |            AdjP
   ______|_____          |             |
 Adj          N_pl      V_pl          Adj
  |            |         |             |
Flying       planes     are        dangerous
```

3. **Backward Compatibility Verification:**
   - `"Flying planes can be dangerous"` $\rightarrow$ Still emits **2 parses** (via `NP_sg VP_sg` and `NP_pl VP_pl`).
   - `"They are flying planes"` $\rightarrow$ Still emits **2 parses** (via `Aux_pl VP_nf` and `V_pl NP_pl`).
