# Tutorial 2: Frame Semantics with NLTK & FrameNet — Solutions & Report

## 1. Assignment Scope & Overview
This tutorial explores **FrameNet v1.5** (`framenet_v15` in NLTK), a lexical database grounded in Charles Fillmore's theory of **Frame Semantics**.
- **Frame**: A conceptual structure describing a type of situation, object, or event along with its participants (**Frame Elements**, or FEs). FrameNet v1.5 contains **1,019 frames**.
- **Lexical Unit (LU)**: A pairing of a word (lemma + part-of-speech tag, such as `bell.n` or `make.v`) with a specific semantic frame that it evokes.
- **Polysemy in FrameNet**: When a single word form (such as the verb `make.v`) evokes multiple distinct semantic frames, it appears as multiple distinct Lexical Units (each with a unique LU ID and associated frame).

---

## 2. Preparatory Steps
Before solving the three exercises, the handout asks us to verify the total number of frames and search for frames containing `"noise"` (case-insensitive):

```python
import nltk
nltk.download("framenet_v15")
from nltk.corpus import framenet15 as fn

len(fn.frames())          # Returns 1019
fn.frames("(?i)noise")    # Case-insensitive regex search for 'noise'
```

### Output of `fn.frames("(?i)noise")`:
There are **5 frames** whose names match `(?i)noise`:
1. `Cause_to_make_noise` (Frame ID: `801`)
2. `Communication_noise` (Frame ID: `39`)
3. `Make_noise` (Frame ID: `69`)
4. `Motion_noise` (Frame ID: `60`)
5. `Noise_makers` (Frame ID: `1017`)

---

## 3. Exercise Solutions

### Exercise 3.1: Name some lexical units from the `Noise_makers` frame.
- **How we solve it**: We retrieve the `Noise_makers` frame using `fn.frame("Noise_makers")` and access its `.lexUnit` dictionary attribute (`noise_makers_frame.lexUnit.keys()`).
- **Frame Definition**: *"The Noise_maker is an artifact used to produce sound, especially for musical effect."*
- **Complete List of Lexical Units in `Noise_makers` (10 total)**:
  1. **`alarm.n`** (LU ID: `11243`) — *a warning sound or device.*
  2. **`bell.n`** (LU ID: `10211`) — *a hollow object, typically made of metal and in the shape of a deep inverted cup, that sounds a clear musical note when struck.*
  3. **`cello.n`** (LU ID: `10217`) — *a bass instrument of the violin family, held upright on the floor between the legs of the seated player.*
  4. **`drum.n`** (LU ID: `10216`) — *a percussion instrument sounded by being struck with sticks or the hands...*
  5. **`guitar.n`** (LU ID: `10210`) — *a stringed musical instrument with a fretted fingerboard and six or twelve strings...*
  6. **`piano.n`** (LU ID: `10213`) — *a large keyboard musical instrument with a wooden case enclosing a soundboard and metal strings...*
  7. **`rattle.n`** (LU ID: `10214`) — *a thing that makes a rattling sound, in particular a baby's toy consisting of a container filled with small pellets.*
  8. **`saxophone.n`** (LU ID: `10218`) — *a member of a family of metal wind instruments with a reed like a clarinet, used especially in jazz and dance music.*
  9. **`siren.n`** (LU ID: `10212`) — *a device that makes a loud prolonged signal or warning sound.*
  10. **`xylophone.n`** (LU ID: `10215`) — *a musical instrument played by striking a row of wooden bars of graduated length with small beaters.*

---

### Exercise 3.2: What are the two frames with the most lexical units? How many lexical units do they contain?
- **How we solve it**: We iterate over all 1,019 frames in `fn.frames()`, measure the number of lexical units in each frame using `len(frame.lexUnit)`, and sort the frames in descending order by their lexical unit count.
- **Answer**:
  The top two frames are tied at **177 lexical units** each:
  1. **`Emotion_directed`** (Frame ID: `46`) — contains **177 lexical units** (e.g., `angry.a`, `afraid.a`, `delighted.a`, `furious.a`, `upset.a`).
  2. **`Stimulus_focus`** (Frame ID: `364`) — contains **177 lexical units** (e.g., `annoying.a`, `boring.a`, `charming.a`, `fascinating.a`, `terrifying.a`).

  *(For reference, the next three largest frames are `Clothing` with 164 LUs, `Self_motion` with 145 LUs, and `Experiencer_obj` with 132 LUs.)*

---

### Exercise 3.3: Can you list the most polysemous verbs? They occur in as many as 9 different lexical units!
- **How we solve it**: We iterate through all lexical units in FrameNet via `fn.lus()`, filter for verbs (lexical units whose `.name` ends with `.v`), and count how many times each verb name appears across different lexical units/frames.
- **Answer**:
  There are **3 verbs** tied as the most polysemous verbs in FrameNet v1.5, each occurring in **9 different lexical units** (and evoking 9 distinct frames):

  1. **`make.v`** (9 lexical units):
     - LU ID `4`: `Causation`
     - LU ID `4748`: `Building`
     - LU ID `4884`: `Arriving`
     - LU ID `4895`: `Cooking_creation`
     - LU ID `5436`: `Intentionally_create`
     - LU ID `6404`: `Self_motion`
     - LU ID `7526`: `Manufacturing`
     - LU ID `8705`: `Cause_change`
     - LU ID `13737`: `Earnings_and_losses`

  2. **`rise.v`** (9 lexical units):
     - LU ID `1069`: `Path_shape`
     - LU ID `1874`: `Change_position_on_a_scale`
     - LU ID `9723`: `Change_posture`
     - LU ID `11980`: `Getting_up`
     - LU ID `11982`: `Dough_rising`
     - LU ID `11986`: `Resurrection`
     - LU ID `12023`: `Sidereal_appearance`
     - LU ID `12034`: `Rising_to_a_challenge`
     - LU ID `12961`: `Motion_directional`

  3. **`swing.v`** (9 lexical units):
     - LU ID `99`: `Body_movement`
     - LU ID `1074`: `Path_shape`
     - LU ID `5046`: `Cause_to_move_in_place`
     - LU ID `10142`: `Moving_in_place`
     - LU ID `12888`: `Undergo_change`
     - LU ID `12978`: `Change_position_on_a_scale`
     - LU ID `12979`: `Change_direction`
     - LU ID `12991`: `Motion`
     - LU ID `12992`: `Self_motion`

  *(Runner-up verbs occurring in **8 lexical units** each: `call.v`, `cut.v`, `get.v`, `lose.v`, `take.v`, and `tie.v`.)*

---

## 4. Reproducibility & How to Run
From the `tut2` directory, activate your virtual environment and run `main.py`:

```bash
cd /Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut2
source /Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/anaphora-resolution/.venv/bin/activate
python3 main.py
```
