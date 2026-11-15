# Understanding & Viva Preparation Guide: Tutorial 3 (NLTK PropBank, VerbNet & BRAT)

**Student**: Baani  
**Course**: Computational Linguistics 2 (CL-2)  
**Folder**: `baani_assignments/semester3_assignments/cl2_tuts/tut3`

---

## 1. Concept & Problem Walkthrough ("What & Why Before How")

### 1.1 What Are We Trying to Do and Why?
When we parse a sentence syntactically (e.g., into `NP` and `VP`), the syntax tree tells us the *grammatical* subject and object, but it does **not** directly tell us *who did what to whom*. For example:
- *"States submitted strategies to the department."* (`states` = subject)
- *"Strategies were submitted by states to the department."* (`strategies` = subject)

Even though the surface syntax changed, the underlying **semantic roles** stayed identical: `states` is the giver/submitter (`ARG0` / `Agent`), `strategies` is the thing submitted (`ARG1` / `Theme`), and `to the department` is the recipient (`ARG2` / `Recipient`).

**Semantic Role Labelling (SRL)** is the task of automatically identifying predicates (usually verbs) and labelling their arguments with semantic roles. In this tutorial, we combine three classic lexical and annotation resources using Python and NLTK:

1. **PropBank (Proposition Bank)**:
   - Adds a semantic layer directly on top of the Penn Treebank syntactic parse trees.
   - Instead of trying to invent universal role names that work across all verbs, PropBank defines **verb-specific numbered arguments** (`ARG0` to `ARG5`) for each coarse-grained verb sense (**roleset**, such as `pass.01` = *"bill becomes law"* vs. `pass.02` = *"overtake"*).
   - Across almost all transitive verbs, **`ARG0`** is the **Proto-Agent** (the actor, causer, experiencer, or speaker) and **`ARG1`** is the **Proto-Patient / Theme** (the entity undergoing the action or change). **`ARG2`–`ARG5`** are verb-specific (recipient, beneficiary, instrument, attribute, start/end point).
   - Any adjunct/modifier that can attach to almost any verb receives an **`ARGM-*`** tag:
     - `ARGM-TMP`: Time (*"Last June"*, *"By this September"*, *"2001"*)
     - `ARGM-LOC`: Location (*"at the state level"*, *"at the local level"*)
     - `ARGM-PRP`: Purpose (*"to determine whether or not each child is learning"*)
     - `ARGM-MOD`: Modal auxiliary (*"must"*, *"will"*)
     - `ARGM-ADV`: Adverbial modifier (*"ultimately"*, *"also"*)
     - `ARGM-DIS`: Discourse connective (*"But"*)
     - `ARGM-EXT`: Extent / degree (*"highly"*)

2. **VerbNet**:
   - Based on Beth Levin's (1993) taxonomy of English verbs, which groups verbs into hierarchical **VerbNet classes** (e.g., `admire-31.2`, `give-13.1`, `put-9.1-2`, `say-37.7`) based on shared **diathesis alternations** (syntactic frames they can appear in).
   - Unlike PropBank's numbered `ARG0`/`ARG1`, VerbNet uses explicit **thematic roles** (`Agent`, `Experiencer`, `Theme`, `Topic`, `Recipient`, `Destination`, `Product`, `Beneficiary`) with **selectional restrictions** (such as `[+animate]`, `[+organization]`, `[+concrete]`).
   - Each VerbNet frame links a **syntactic frame** (e.g., `NP[Agent] VERB NP[Topic] PREP[to] NP[Recipient]`) to a neo-Davidsonian **logical semantic representation** (e.g., `transfer_info(during(E), Agent, Recipient, Topic) ; cause(Agent, E)`).

3. **BRAT (Browser-based Rapid Annotation Tool)**:
   - Standard tool for annotating and visualizing text spans and predicate-argument structures.
   - Uses a two-file **Standoff Format** per document:
     - `.txt`: The raw plain-text sentence.
     - `.ann`: Character-offset annotations (`T1\tPredicate start end\tword`, `T2\tARG0 start end\tspan`, and `E1\tPredicate:T1 ARG0:T2 ARG1:T3 ...`).

---

## 2. Step-by-Step Code Architecture & Function Mapping

Following strict multi-file modularity, the codebase is split into 5 clean module files orchestrated by `main.py`:

| File | Lines | Responsibility & Key Functions |
| :--- | :--- | :--- |
| [main.py](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut3/main.py) | ~105 | Entry point. Calls `ensure_nltk_resources()`, runs `run_sample_propbank_demo()` (verifying the sample code from `nltk.org/howto/propbank.html`), and loops over all 10 sentences calling Operations 1–6 via `process_single_sentence()`. |
| [sentences_data.py](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut3/sentences_data.py) | ~265 | Stores `SENTENCES` (the 10 sentences from the PDF) and `SENTENCE_SRL_DATA` (the predicate-argument roleset mappings and argument spans for each sentence). |
| [step1_2_pos_and_parse.py](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut3/step1_2_pos_and_parse.py) | ~185 | **Operation 1 (`op1_pos_tag`)**: Tokenizes with `nltk.word_tokenize()` and tags with `nltk.pos_tag()`.<br/>**Operation 2 (`op2_parse_and_visualize`)**: Parses with `nltk.RegexpParser` into `NP`, `PP`, `VP`, `SBAR`, `S`, prints bracketed + ASCII trees (`TreePrettyPrinter`), and renders `trees/sentence_<id>_tree.svg` via `save_tree_svg()`. |
| [step3_4_verbs_and_propbank.py](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut3/step3_4_verbs_and_propbank.py) | ~125 | **Operation 3 (`op3_extract_verbs`)**: Extracts `VB*` tokens, lemmatizes via `WordNetLemmatizer().lemmatize(w, 'v')`, and classifies each as `Main Verb / Predicate`, `Copula Predicate`, or `Auxiliary Verb`.<br/>**Operation 4 (`op4_propbank_roles`)**: Queries `propbank.rolesets(lemma)` to print official PropBank XML role definitions and prints the sentence-level PropBank argument assignments. |
| [step5_verbnet.py](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut3/step5_verbnet.py) | ~115 | **Operation 5 (`op5_verbnet_frames`)**: Queries `verbnet.classids(lemma=lemma)`, resolves inherited thematic roles with `get_thematic_roles_with_inheritance()`, and extracts syntactic frames and logical semantic predicates via `verbnet.frames(cid)`. |
| [step6_brat_annotation.py](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut3/step6_brat_annotation.py) | ~185 | **Operation 6 (`op6_brat_annotate`)**: Computes exact 0-based character offsets with `find_span_offsets()`, writes BRAT `.txt`, `.ann`, `annotation.conf`, and `visual.conf` files, and renders BRAT role-arc SVG diagrams (`save_brat_svg()`). |
| [generate_report.py](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut3/generate_report.py) | ~315 | Compiles all outputs and SVG diagrams into [Report.md](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut3/Report.md), `Report.html`, and [Report.pdf](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut3/Report.pdf). |

---

## 3. Key Viva Pointers ("What to Show the TA")

1. **The POS Tagger Edge Case in Sentence 2 (`"sees"` tagged as `NNS`)**:
   - **Where to point**: [step1_2_pos_and_parse.py](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut3/step1_2_pos_and_parse.py#L28-L41) and [step3_4_verbs_and_propbank.py](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut3/step3_4_verbs_and_propbank.py#L19-L49).
   - **What to explain**: In Sentence 2 (*"The good teacher sees what is possible."*), NLTK's default `averaged_perceptron_tagger_eng` tags `sees` as `NNS` (plural noun, as in *"the Holy Sees"*) rather than `VBZ` (3rd-person singular verb). If we blindly filtered only `tag.startswith('VB')`, we would miss the main predicate `sees`! Our code explicitly preserves the raw tagger output for Operation 1 while catching `sees` in `prepare_tags_for_parser()` and `op3_extract_verbs()` so its PropBank roleset (`see.01`) and VerbNet classes (`see-30.1-1`, `consider-29.9-1-1`, `characterize-29.2-1`) are properly extracted.

2. **VerbNet Subclass Thematic Role Inheritance (`themroles` returning `[]` on subclasses)**:
   - **Where to point**: `get_thematic_roles_with_inheritance()` in [step5_verbnet.py](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut3/step5_verbnet.py#L11-L26).
   - **What to explain**: In NLTK's VerbNet reader, `verbnet.classids(lemma='see')` returns subclass IDs like `'see-30.1-1'`. Calling `verbnet.themroles('see-30.1-1')` directly returns an empty list `[]` because the `<THEMROLES>` block in `see-30.1.xml` is defined on the parent `<VNCLASS ID="see-30.1">` element and inherited by `<VNSUBCLASS ID="see-30.1-1">`. Our helper checks `verbnet.fileids(class_id)[0][:-4]` to fetch the parent class's thematic roles whenever the subclass inherits them.

3. **Why Some Verbs Are in PropBank but NOT in VerbNet 2.1 (`be`, `ensure`, `determine`)**:
   - **Where to point**: Sentences 2, 5, 6, 8, 10 in [step5_verbnet.py](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut3/step5_verbnet.py#L84-L86).
   - **What to explain**: PropBank annotates *every* verb in the Wall Street Journal Penn Treebank (including copula/auxiliary `be` and abstract cognitive/causal verbs like `ensure` and `determine`). VerbNet 2.1, however, only covers verbs belonging to Beth Levin's syntactic alternation classes (~3,621 lemmas). Auxiliaries/copulas (`be`) and certain non-alternating abstract verbs (`ensure`, `determine`) are not in VerbNet 2.1.

4. **Handling Contractions (`what's called` in Sentence 3)**:
   - **Where to point**: [step3_4_verbs_and_propbank.py](file:///Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut3/step3_4_verbs_and_propbank.py#L25-L36).
   - **What to explain**: NLTK tokenizes `"what's"` into `"what"` (`WP`) and `"'s"` (`VBZ`). Calling `propbank.rolesets("'s")` directly raises `ValueError: Frameset file for 's not found`. Mapping `"'s"` to its base lemma `"be"` allows us to look up `be.01`/`be.02`/`be.03` cleanly and recognize `"'s"` as the passive auxiliary supporting `"called"` (`VBN`).

---

## 4. Likely Viva Questions & Ready-to-Speak Model Answers

1. **Q1: What is the fundamental difference between PropBank and VerbNet?**
   - **Answer**: PropBank is a corpus-driven resource that defines verb-sense-specific numbered arguments (`ARG0`, `ARG1`, `ARG2`, ...) for individual verb lemmas on top of Penn Treebank trees. VerbNet is a hierarchical verb lexicon based on Levin classes that groups verbs sharing syntactic alternations and assigns class-level thematic roles (`Agent`, `Theme`, `Experiencer`, `Recipient`) along with logical semantic predicates.

2. **Q2: What do `ARG0` and `ARG1` represent in PropBank? Are `ARG2`–`ARG5` also consistent across all verbs?**
   - **Answer**: Following Dowty's Proto-Role theory, `ARG0` consistently represents the **Proto-Agent** (volitional actor, causer, experiencer) and `ARG1` consistently represents the **Proto-Patient / Theme** (entity affected, created, or perceived). In contrast, `ARG2` through `ARG5` are **verb-specific** — for `submit.01`, `ARG2` is the recipient (*"given-to"*), whereas for `call.01`, `ARG2` is the attribute/name assigned to `ARG1`.

3. **Q3: Why does PropBank assign `ARG1` and `ARG2` to the copula verb `be.01` instead of `ARG0` and `ARG1`?**
   - **Answer**: Because a copula (*"is"*, *"are"*) expresses a state or attribution rather than a volitional action. There is no Proto-Agent (`ARG0`); instead, the grammatical subject is the entity being described (`ARG1`: topic), and the predicate complement is the property attributed to it (`ARG2`: comment).

4. **Q4: In Sentence 6 (*"Inherent in the law is the vision of high standards..."*), which phrase is `ARG1` and which is `ARG2` of `is` (`be.01`)?**
   - **Answer**: Sentence 6 uses predicate inversion. *"the vision of high standards, and money to meet the standards"* is `ARG1` (the topic/subject), while *"Inherent in the law"* is `ARG2` (the fronted predicate attribute/comment).

5. **Q5: How does `PropbankTreePointer(wordnum, height)` work in NLTK's `propbank.instances()`?**
   - **Answer**: `wordnum` indexes the starting leaf token in the Penn Treebank sentence (including empty trace elements like `-NONE-`), and `height` tells us how many parent nodes to climb up from that leaf to select the full constituent subtree via `pointer.select(tree)`.

6. **Q6: What are `PropbankSplitTreePointer` and `PropbankChainTreePointer` in NLTK?**
   - **Answer**: `PropbankSplitTreePointer` represents a discontinuous argument split across multiple non-adjacent tree nodes (`*SPLIT*`), while `PropbankChainTreePointer` links a moved wh-phrase or NP to its syntactic trace (`-NONE- *T*`) in the parse tree (`*CHAIN*`).

7. **Q7: Why did `nltk.pos_tag` tag `"sees"` as `NNS` in Sentence 2?**
   - **Answer**: NLTK's `averaged_perceptron_tagger_eng` is a greedy left-to-right discriminative sequence model trained on WSJ text. After seeing `DT JJ NN` (*"The good teacher"*), a noun compound or plural noun (`NNS`) occasionally follows a singular noun in WSJ headlines/text, and `"sees"` is ambiguous (verb vs. plural of noun *"see"*, a bishopric). Without a full syntactic parser re-ranking the tags, the tagger misclassified `"sees"` as `NNS`.

8. **Q8: In Sentence 5 (*"...strategies for ensuring that all teachers are highly qualified"*), why is `all teachers` labelled `ARG1` of `qualified` (`qualify.02`) rather than `ARG0`?**
   - **Answer**: Under `qualify.02` (*"measure up to / meet requirements"*), the entity being tested or meeting the qualification is defined in the PropBank frameset as `ARG1` (*"entity being tested"*), and `"highly"` is an extent modifier (`ARGM-EXT`).

9. **Q9: How are semantic representations structured inside NLTK's `verbnet.frames(class_id)`?**
   - **Answer**: Each frame dictionary has a `"semantics"` key containing a list of predicate dictionaries. Each predicate has `"predicate_value"` (e.g., `'transfer_info'`, `'cause'`, `'exist'`), `"negated"` (`True` if `<PRED bool="!">` in XML), and `"arguments"` (such as event variables `'E'`, `'start(E)'`, `'during(E)'`, `'result(E)'`, and thematic role variables `'Agent'`, `'Theme'`). When a role is preceded by `?` (e.g., `?Recipient`), it indicates an implicit/unspecified argument in that syntactic frame.

10. **Q10: What do `start(E)`, `during(E)`, `end(E)`, and `result(E)` mean in VerbNet semantics?**
    - **Answer**: VerbNet uses a sub-event temporal calculus over event `E`. For instance, in `build-26.1-1` (*make*), `NOT exist(start(E), Product)` and `exist(result(E), Product)` formally capture that the product did not exist at the start of the event and comes into existence as the result of the event, caused by the `Agent` (`cause(Agent, E)`).

11. **Q11: What is the difference between a main predicate verb and an auxiliary verb in Operation 3?**
    - **Answer**: An auxiliary verb (such as `are` in *"People are responding"*, `is` in *"each child is learning"*, or `'s` in *"what's called"*) carries tense, aspect, or voice (`be.03` in PropBank) and has no thematic roles of its own; the lexical participle (`responding`, `learning`, `called`) is the true semantic predicate that assigns `ARG0`, `ARG1`, etc.

12. **Q12: How does the BRAT Standoff format (`.ann`) represent predicates and their semantic roles?**
    - **Answer**: Text-bound annotations (`T1`, `T2`, ...) record the role type, 0-based start/end character offsets in the `.txt` file, and the exact substring (`T2\tARG0 0 6\tPeople`). Event annotations (`E1`, `E2`, ...) bind a predicate trigger `T#` to all of its argument spans (`E1\tPredicate:T1 ARG0:T2 ARG1:T3 ARGM-LOC:T4`).

13. **Q13: Why does BRAT use standoff character offsets instead of inserting XML tags directly into the text?**
    - **Answer**: Standoff annotation keeps the original `.txt` file completely unmodified, which allows overlapping, nested, or discontinuous spans (such as in Sentence 8 where the `ARG1` of `said` contains the embedded predicates `seek`, `design`, `determine`, and `learning`) without breaking XML hierarchy rules.

14. **Q14: In Sentence 9 (*"...assess the programs they expect to make by 2005 and 2006 school year"*), how does `"the programs"` serve as an argument to two different verbs?**
    - **Answer**: `"the programs they expect to make..."` is a reduced relative clause modifying `"the programs"`. For the matrix verb `assess` (`assess.01`), the entire NP is `ARG1` (thing assessed). Inside the relative clause, `"the programs"` is also the extracted object (`ARG1`, creation) of `make` (`make.01`).

15. **Q15: What happens if you call `nltk.RegexpParser` with `loop=2` in Operation 2?**
    - **Answer**: Running 2 passes (`loop=2`) over the chunk grammar allows recursive rules like `NP: {<NP><CC><NP>}` (coordinating two noun phrases such as *"Senators and a good teacher"* or *"good laws and good plans"*) and `VP` attachment of `PP`s to combine chunks formed in the first pass into higher-level constituents in the second pass.
