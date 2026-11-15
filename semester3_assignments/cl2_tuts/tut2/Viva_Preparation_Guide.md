# Viva & Study Preparation Guide: FrameNet with NLTK (Tutorial 2)

---

## 1. Concept & Problem Walkthrough ("What & Why Before How")

### What is FrameNet and Why Do We Use It?
In earlier tutorials (like WordNet), we grouped words into **synsets** (sets of synonyms) connected by taxonomic relations like *hypernyms* (`is-a`) and *meronyms* (`part-of`). However, WordNet doesn't capture **who does what to whom** in an event or situation.

**Frame Semantics** (introduced by Charles Fillmore) says that you cannot understand the meaning of a word without understanding the entire background situation—or **Frame**—it evokes.
- **Example**: You cannot understand the word *"buy"* or *"sell"* without understanding a **Commercial Transaction** situation involving a *Buyer*, a *Seller*, *Goods*, and *Money*.
- **Frame**: A schematic representation of a situation, object, or event (e.g., `Noise_makers`, `Commercial_transaction`, `Self_motion`).
- **Frame Elements (FEs)**: The semantic roles/participants in that frame (e.g., `Noise_maker`, `Sound`, `Speaker`).
- **Lexical Unit (LU)**: A pairing of a word (lemma + part of speech, like `guitar.n` or `make.v`) with a single specific Frame. If a word has multiple meanings that evoke different situations, it is **polysemous** and belongs to multiple Lexical Units (one per frame).

---

### Step-by-Step Code Walkthrough

Our solution is cleanly divided into 4 focused files:

1. **`main.py`**:
   - Imports `nltk` and `from nltk.corpus import framenet15 as fn`, and runs Exercises 3.1, 3.2, and 3.3 sequentially.
   - *Important Technical Detail*: In older NLTK versions (when the PDF was written), `from nltk.corpus import framenet as fn` loaded FrameNet v1.5 (1,019 frames). In modern NLTK 3.x, `nltk.corpus.framenet` points to FrameNet v1.7 (1,221 frames), while `nltk.corpus.framenet15` points to FrameNet v1.5 (1,019 frames). Using `framenet15` ensures our counts match the handout's `1019` frames and `9` lexical units for polysemous verbs!

2. **`exercise_3_1.py`**:
   - **`exercise_3_1(fn_corpus)`**: Fetches the `Noise_makers` frame via `fn_corpus.frame("Noise_makers")`, accesses its `.lexUnit` dictionary, and prints all 10 lexical units (`alarm.n`, `bell.n`, `cello.n`, `drum.n`, `guitar.n`, `piano.n`, `rattle.n`, `saxophone.n`, `siren.n`, `xylophone.n`).

3. **`exercise_3_2.py`**:
   - **`get_frame_lu_counts(fn_corpus)`**: Loops through every frame in `fn_corpus.frames()`, computes `len(frame.lexUnit)`, stores `(frame.name, frame.ID, num_lus)` tuples, and sorts them in descending order by `num_lus`.
   - **`exercise_3_2(fn_corpus)`**: Prints the top 2 frames tied at **177 lexical units** each: `Emotion_directed` and `Stimulus_focus`.

4. **`exercise_3_3.py`**:
   - **`count_verb_polysemy(fn_corpus)`**: Loops over all lexical units in `fn_corpus.lus()`, checks if `lu.name.endswith(".v")`, and counts how many LUs each verb lemma+POS appears in using a simple Python dictionary `verb_lu_counts`.
   - **`exercise_3_3(fn_corpus)`**: Finds `max_count` (`9`) and prints the 3 most polysemous verbs (`make.v`, `rise.v`, `swing.v`) along with all 9 frames each verb evokes.

---

## 2. Key Viva Pointers ("What to Show the TA")

1. **Why we imported `framenet15 as fn` (`main.py`, Line 2)**:
   - Show the TA that the PDF handout says *"With `len(fn.frames())` we can see that there are 1019 different frames in FrameNet"* and instructs `nltk.download("framenet_v15")`. In modern NLTK, `nltk.corpus.framenet15` is the reader for `framenet_v15`.
2. **How `.lexUnit` works (`exercise_3_1.py`, Line 14 & `exercise_3_2.py`, Line 9)**:
   - Every Frame object in NLTK's FrameNet corpus has a `.lexUnit` attribute, which is a Python `dict` mapping the lexical unit name string (e.g., `'guitar.n'`) to its Lexical Unit object. Calling `len(frame.lexUnit)` gives the exact number of LUs in that frame.
3. **Why `Emotion_directed` and `Stimulus_focus` tie at 177 LUs (`exercise_3_2.py`, Line 21)**:
   - Both frames have exactly 177 lexical units in FrameNet 1.5! `Emotion_directed` covers adjectives/nouns describing how an Experiencer feels toward a Stimulus (`angry.a`, `happy.a`), while `Stimulus_focus` covers adjectives describing the Stimulus that triggers the emotion (`annoying.a`, `exciting.a`).
4. **How Verb Polysemy is Calculated (`exercise_3_3.py`, Lines 1–19)**:
   - Each entry in `fn.lus()` is a distinct pairing of `(word.pos, Frame)`. If `make.v` appears 9 times in `fn.lus()`, it means `make.v` evokes 9 different frames (`Causation`, `Building`, `Arriving`, `Cooking_creation`, `Intentionally_create`, `Self_motion`, `Manufacturing`, `Cause_change`, `Earnings_and_losses`).

---

## 3. Likely Viva Questions & Ready-to-Speak Model Answers

### Q1: What is a "Frame" in FrameNet, and how is it different from a WordNet "Synset"?
- **Answer**: A WordNet synset only groups strict synonyms together (words that can substitute for each other, like *car* and *automobile*). A FrameNet **Frame** represents an entire conceptual scenario or event (like `Commercial_transaction` or `Cooking_creation`). Words that belong to the same frame don't have to be synonyms—for example, *buy*, *sell*, *pay*, and *cost* evoke commercial frames from different perspectives, and in `Noise_makers`, *guitar.n*, *drum.n*, and *siren.n* are completely different instruments/devices that all share the scenario of being artifacts made to produce sound.

### Q2: What is a Lexical Unit (LU) in FrameNet?
- **Answer**: A Lexical Unit is a pairing of a word (specifically a lemma + part-of-speech suffix, like `spin.v` or `bell.n`) with a single semantic sense—meaning a single Frame. If a word evokes 4 different frames (like `spin.v`), it corresponds to 4 distinct Lexical Units in FrameNet, each with its own unique `ID`.

### Q3: What does `(?i)` do in `fn.frames("(?i)noise")`?
- **Answer**: `fn.frames()` takes a regular expression pattern to filter frame names. The inline regex flag `(?i)` turns on **case-insensitive matching**, so it matches both `"Noise_makers"` (capital `N`) and `"Make_noise"` (lowercase `n`).

### Q4: Why do we escape the dot in `fn.lus(r"absorb\.v")`?
- **Answer**: Because `fn.lus()` interprets its argument as a regular expression. In regex, an unescaped dot `.` matches *any* character, whereas `\.` matches a literal period separating the lemma `absorb` from its part-of-speech tag `v`.

### Q5: In Exercise 3.1, what part of speech are all the lexical units in `Noise_makers`? Why?
- **Answer**: All 10 lexical units in `Noise_makers` (`alarm.n`, `bell.n`, `cello.n`, `drum.n`, `guitar.n`, `piano.n`, `rattle.n`, `saxophone.n`, `siren.n`, `xylophone.n`) are **nouns** (`.n`), because the frame represents physical artifacts/objects used to produce sound, rather than the action of making sound (which is in the `Make_noise` or `Cause_to_make_noise` frames).

### Q6: What is the difference between `Emotion_directed` and `Stimulus_focus` (the two top frames in Exercise 3.2)?
- **Answer**: Both have 177 lexical units and deal with emotions, but from opposite perspectives:
  - `Emotion_directed` focuses on the **Experiencer** feeling an emotion directed at something (e.g., *afraid.a*, *furious.a*, *proud.a*).
  - `Stimulus_focus` focuses on the **Stimulus** that causes that emotion in someone else (e.g., *frightening.a*, *infuriating.a*, *impressive.a*).

### Q7: How does FrameNet represent polysemy?
- **Answer**: In FrameNet, a word is polysemous if the same lemma+POS (like `make.v`) belongs to multiple Lexical Units, meaning it evokes multiple different semantic frames depending on context (e.g., *"make dinner"* evokes `Cooking_creation`, *"make money"* evokes `Earnings_and_losses`, and *"make a house"* evokes `Building`).

### Q8: Which verbs are the most polysemous in FrameNet v1.5?
- **Answer**: Three verbs are tied at the maximum of **9 lexical units** each: **`make.v`**, **`rise.v`**, and **`swing.v`**.

### Q9: What if the TA asks: "Can you find the most polysemous nouns or adjectives instead of verbs?"
- **Answer**: In `exercise_3_3.py`, inside `count_verb_polysemy()`, we simply change `if lu.name.endswith(".v"):` to `if lu.name.endswith(".n"):` for nouns or `if lu.name.endswith(".a"):` for adjectives.

### Q10: Why did we check `lu.name.endswith(".v")` instead of `lu.POS == "V"`? Is there any difference?
- **Answer**: They give the exact same top polysemous verbs (`make.v`, `rise.v`, `swing.v` with 9 LUs). Across all 11,800+ LUs in FrameNet 1.5, there is only 1 minor annotation quirk (`ID=14178`, `come together.v`, which has `.v` in its name and `POS='A'`), and it only occurs once so it doesn't affect polysemy rankings at all. Checking `.endswith(".v")` directly matches the `.v` naming convention taught in the handout (`absorb\.v`, `spin\.v`).

### Q11: What is the time complexity of our solutions for Exercise 3.2 and Exercise 3.3?
- **Answer**:
  - **Exercise 3.2**: Let $F$ be the number of frames ($1,019$). Getting `len(frame.lexUnit)` is $O(1)$ per frame, and sorting takes $O(F \log F)$.
  - **Exercise 3.3**: Let $L$ be the total number of lexical units in FrameNet ($11,829$ in v1.5). Counting frequencies with a hash map (`dict`) takes $O(L)$ time, and finding the maximum takes $O(V)$ where $V$ is the number of unique verbs.
