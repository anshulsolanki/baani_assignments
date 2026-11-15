# Language and Society Project — Phase 2: Non-Verbal & Multimodal Discourse Analysis

* **Student Name:** Baani Solanki (`2025114016`)
* **Program:** 2nd-Year B.Tech CSE / CLD
* **Course:** Language and Society
* **Phase:** Phase 2 — Non-Verbal, Paralinguistic & Kinesic Layer (Building on Phase 1 Verbal Analysis)

---

## 1. Project Overview

In **Phase 1**, we analysed the **verbal layer** (lexical choices, agency/passivisation, presuppositions, metaphors, and syntactic framing) across **6 news creators/outlets** covering two major socio-political events in India:
1. **Event 1:** Ram Mandir Donation & Land Deal Controversy (Ayodhya)
2. **Event 2:** Students' Protest Regarding the NEET-UG 2024 Paper Leak & Grace-Marks Crisis

In **Phase 2**, we add a **multimodal and paralinguistic layer** to examine how meaning, ideology, and institutional alignment are performed *beyond words*. Following `lns_project_updated_guidelines.pdf` and `NonVerbal_AnalysisForm.pdf`, every creator's coverage is analysed across **five core non-verbal dimensions**:
1. **Pauses, Silences & Abrupt Stops:** Micro-pauses `(.)`, timed dramatic silences `(1.5)`, defensive stammers/self-repairs (`—`), and forced silences (`[overlap]` shouting and studio mic-fading).
2. **Trailing Sentences & Unfinished Utterances (`...`):** Aposiopesis—leaving an accusation or presupposition unspoken so the audience supplies the biased conclusion without the speaker taking explicit legal/editorial responsibility.
3. **Intonation, Pitch, Volume & Prosody:** Marked rising pitch `↑` (incredulity, mockery, challenge), falling pitch `↓` (finality, authority), loud stress (`WORD` / `_word_`), and hushed/reverential or conspiratorial delivery (`°word°`).
4. **Coughs, Sighs & Non-Lexical Vocalisations:** Audible sighs `[sigh]`, mocking scoffs `[scoff]`, ironic chuckles `[chuckle]`, throat-clearing `[cough]` when pivoting away from awkward facts, and sharp breath intakes `[gasp]`.
5. **Hand Gestures, Facial Expressions & Posture (Kinesics):** Physical air-quotes `{{gesture: air-quotes}}`, accusatory finger-pointing/wagging, desk-thumping, open-palm appeals, sequential finger-counting, eye-rolls, smirks, and visual props (e.g., an injured DCP's bandaged hand vs. a student protester's bruised wrist).

---

## 2. Directory Structure

```text
phase 2/
├── README.md                                      # Project overview, matrix, and execution guide
├── Understanding_Guide.md                         # Theoretical background & 6-creator comparative synthesis
├── Viva_Guide.md                                  # Mandatory Viva preparation guide (pointers + 15 Q&As)
├── lns_project_updated_guidelines.pdf             # Official Phase 2 guidelines & notation key
├── NonVerbal_AnalysisForm.pdf                     # Official blank Non-Verbal Analysis Worksheet
├── analysis_forms/                                # Completed worksheets (Markdown, PDF, and Overleaf LaTeX)
│   ├── 01_Sarthak_Goswami_NonVerbal_Analysis.md
│   ├── 01_Sarthak_Goswami_NonVerbal_Analysis.pdf
│   ├── 02_Dhruv_Rathee_NonVerbal_Analysis.md
│   ├── 02_Dhruv_Rathee_NonVerbal_Analysis.pdf
│   ├── 03_Mohak_Mangal_NonVerbal_Analysis.md
│   ├── 03_Mohak_Mangal_NonVerbal_Analysis.pdf
│   ├── 04_Aaj_Tak_NonVerbal_Analysis.md
│   ├── 04_Aaj_Tak_NonVerbal_Analysis.pdf
│   ├── 05_Republic_TV_NonVerbal_Analysis.md
│   ├── 05_Republic_TV_NonVerbal_Analysis.pdf
│   ├── 06_The_Wire_NonVerbal_Analysis.md
│   ├── 06_The_Wire_NonVerbal_Analysis.pdf
│   └── latex/                                     # Overleaf-ready .tex files (individual + combined)
│       ├── 01_Sarthak_Goswami_NonVerbal_Analysis.tex
│       ├── 02_Dhruv_Rathee_NonVerbal_Analysis.tex
│       ├── 03_Mohak_Mangal_NonVerbal_Analysis.tex
│       ├── 04_Aaj_Tak_NonVerbal_Analysis.tex
│       ├── 05_Republic_TV_NonVerbal_Analysis.tex
│       ├── 06_The_Wire_NonVerbal_Analysis.tex
│       └── All_6_Creators_Combined_NonVerbal_Analysis.tex
├── scripts/
│   ├── render_pdfs.py                             # Renders Markdown worksheets into styled A4 PDFs
│   └── generate_latex.py                          # Generates Overleaf-compatible LaTeX (.tex) files
└── tests/
    └── test_lns_phase2.py                         # Automated test suite verifying all deliverables & rules
```

> **Note on Transcripts:** All observations and `[MM:SS]` timestamps are grounded in the normalized Roman-script transcripts stored in `../phase 1/transcripts/`. In compliance with course rules, **zero Devanagari characters** and **zero raw audio/video files** are stored in the repository.

---

## 3. Dataset & Video Coverage Matrix

| # | Creator / Outlet | Format / Baseline Style | Event 1: Ram Mandir Controversy | Event 2: NEET Paper Leak Protest | Worksheet File |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | **Sarthak Goswami** (*Sunday Show*) | Solo YouTube Infotainment (~160 WPM, brisk irony, eyebrow raises) | [lb7gZnyZH0c](https://youtu.be/lb7gZnyZH0c) (`[00:00]`–`[05:38]`) | [EM1GeZufO6E](https://youtu.be/EM1GeZufO6E) (`[00:00]`–`[18:45]`) | `01_Sarthak_Goswami_NonVerbal_Analysis.pdf` |
| **02** | **Dhruv Rathee** | Solo YouTube Documentary (~140 WPM, prosecutorial finger-counting, spatial gestures) | [oeH0fOSJuX8](https://youtu.be/oeH0fOSJuX8) (`[00:00]`–`[15:42]`) | [l-6Pm-112io](https://youtu.be/l-6Pm-112io) (`[00:00]`–`[21:15]`) | `02_Dhruv_Rathee_NonVerbal_Analysis.pdf` |
| **03** | **Mohak Mangal** (*Soch*) | Solo YouTube Policy Explainer (~125 WPM, calm seminar tone, data graphs) | *Skipped per guidelines* (only historical video exists) | [v-RikSqb0Vw](https://youtu.be/v-RikSqb0Vw) (`[00:00]`–`[20:12]`) | `03_Mohak_Mangal_NonVerbal_Analysis.pdf` |
| **04** | **Aaj Tak** (*Anjana Om Kashyap*) | Mainstream Hindi TV Bulletin & Live Multi-Panel Debate | [B4L1pz0o4dc](https://youtu.be/B4L1pz0o4dc) (`[00:00]`–`[08:12]`) | [JXLIs0WtJAM](https://www.youtube.com/live/JXLIs0WtJAM) (`[00:00]`–`[32:40]`) | `04_Aaj_Tak_NonVerbal_Analysis.pdf` |
| **05** | **Republic TV** (*Arnab Goswami & Hindi Bureau*) | High-Decibel Nationalist TV Bulletin & 8-Window Debate (~180 WPM) | [0H-bruoEkaY](https://youtu.be/0H-bruoEkaY) (`[00:00]`–`[09:45]`) | [HTvb6E_1Qdc](https://youtu.be/HTvb6E_1Qdc) (`[00:00]`–`[36:20]`) | `05_Republic_TV_NonVerbal_Analysis.pdf` |
| **06** | **The Wire** | Independent Editorial Commentary & Street Ground Report (~120 WPM) | [7rUL8fGgRJA](https://youtu.be/7rUL8fGgRJA) (`[00:00]`–`[14:28]`) | [pYaTVvHeGoM](https://youtu.be/pYaTVvHeGoM) (`[00:00]`–`[16:50]`) | `06_The_Wire_NonVerbal_Analysis.pdf` |

---

## 4. Reproducibility & Verification Commands

To regenerate all LaTeX files and PDFs from the Markdown source worksheets and run the verification test suite:

```bash
cd "semester3/lns_project/phase 2"

# 1. Generate Overleaf LaTeX (.tex) files
python3 scripts/generate_latex.py

# 2. Render black-and-white academic PDFs
python3 scripts/render_pdfs.py

# 3. Run the automated verification test suite
python3 tests/test_lns_phase2.py
```
