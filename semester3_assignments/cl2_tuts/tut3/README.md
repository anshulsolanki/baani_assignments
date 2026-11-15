# CL-2 Tutorial 3: NLTK PropBank & VerbNet Activity

## Files
- `main.py`: Main entry point that runs the 6 steps on each of the 10 sentences.
- `pos_and_parse.py`: Step 1 (`nltk.pos_tag`) and Step 2 (`nltk.RegexpParser` + `tree.pretty_print()`).
- `propbank_and_verbnet.py`: Step 3 (verb extraction & lemmatization), Step 4 (`propbank.rolesets`), and Step 5 (`verbnet.classids` & `verbnet.pprint_frames`).
- `brat_roles.py`: Step 6 (semantic role annotations `ARG0`, `ARG1`, etc. for BRAT).
- `Report.pdf` / `Report.md`: PDF report containing the output of the operations.
- `Understanding_and_Viva_Guide.md`: Viva preparation notes.

## How to Run on Mac
```bash
cd /Users/baanisolanki/baani_assignments/baani_assignments/semester3_assignments/cl2_tuts/tut3
source ../../anaphora-resolution/.venv/bin/activate
python main.py
```
