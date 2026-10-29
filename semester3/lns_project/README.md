# Language & Society Project (`lns_project`) — Comparative News Discourse Analysis

- **Student:** Baani Solanki (`2025114016`)
- **Course:** Language & Society (Semester 3)
- **Events Analysed:**
  1. **Event 1:** *Ram Mandir Donation Controversy* (June–July 2026 — 5 videos; Mohak Mangal skipped per instructions)
  2. **Event 2:** *Students' Protest Regarding NEET Paper Leak* (June–July 2026 — 6 videos)

---

## Key Project Highlights & Compliance Summary

- **11 Timestamped Roman-Script Transcripts (`transcripts/`):** Extracted strictly from **original native-language tracks** (`hi` for Sarthak Goswami, Dhruv Rathee, Mohak Mangal, Aaj Tak; `en` for Republic TV, The Wire — **zero AI-dubbed tracks**), transliterated into natural Roman script with **zero Devanagari characters (`U+0900..U+097F`)**, and formatted with `[MM:SS]` timestamps on every utterance line (`1,848` lines total).
- **Zero Stored Audio/Video Files:** Strictly adheres to the zero-media-storage constraint—no `.mp3`, `.m4a`, `.mp4`, or other audio/video files exist anywhere in the project.
- **6 Complete Creator Analysis Worksheets (`analysis_forms/*.md` & `*.pdf`):** Covering every metadata field, all 8 Event 1 questions, all 9 Event 2 questions, the 5 shared discourse features (*Naming, Presupposition, Agency, Antagonisation, Intensification / Softening*), Short Summaries, **34 Blank Excerpt Records** with cross-outlet comparisons, and End-of-Event Summaries—with `[MM:SS]` timestamps cited alongside every single instance and quote.
- **4 Companion Guides & Automated Test Suite:**
  - `Understanding_Guide.md` — Student-friendly walkthrough written specifically for Baani.
  - `Viva_Guide.md` — Master comparison matrix, CDA/sociolinguistic theory, and 15 high-probability Viva Q&As.
  - `Implementation_Details.md` — Technical documentation of the anti-AI-dubbing extractor, Hindi schwa-deletion Romanizer, PDF renderer, and test suite.
  - `tests/test_lns_project.py` — Automated `pytest` suite verifying unit logic and all end-to-end project invariants.

---

## Corpus & Worksheet Index

| # | Creator / Outlet | Event 1 Transcript (`Ram Mandir`) | Event 2 Transcript (`NEET Protest`) | Filled Analysis Worksheet (`.md` & `.pdf`) |
| :-: | :--- | :--- | :--- | :--- |
| **1** | **Sarthak Goswami** | `01_sarthak_goswami_lb7gZnyZH0c.txt` (`45:41`) | `01_sarthak_goswami_EM1GeZufO6E.txt` (`33:04`) | `analysis_forms/01_Sarthak_Goswami_Analysis.{md,pdf}` |
| **2** | **Dhruv Rathee** | `02_dhruv_rathee_oeH0fOSJuX8.txt` (`16:25`) | `02_dhruv_rathee_l-6Pm-112io.txt` (`17:50`) | `analysis_forms/02_Dhruv_Rathee_Analysis.{md,pdf}` |
| **3** | **Mohak Mangal** | *Skipped per `lns_project_instructions.pdf`* | `03_mohak_mangal_v-RikSqb0Vw.txt` (`11:09`) | `analysis_forms/03_Mohak_Mangal_Analysis.{md,pdf}` |
| **4** | **Aaj Tak** | `04_aaj_tak_B4L1pz0o4dc.txt` (`38:30`) | `04_aaj_tak_JXLIs0WtJAM.txt` (`24:10`) | `analysis_forms/04_Aaj_Tak_Analysis.{md,pdf}` |
| **5** | **Republic TV** | `05_republic_tv_0H-bruoEkaY.txt` (`54:30`) | `05_republic_tv_HTvb6E_1Qdc.txt` (`06:41`) | `analysis_forms/05_Republic_TV_Analysis.{md,pdf}` |
| **6** | **The Wire** | `06_the_wire_7rUL8fGgRJA.txt` (`39:18`) | `06_the_wire_pYaTVvHeGoM.txt` (`32:26`) | `analysis_forms/06_The_Wire_Analysis.{md,pdf}` |

---

## Quick Verification Commands

```bash
# Render all 6 Markdown worksheets into print-ready A4 PDFs
.venv/bin/python scripts/render_pdfs.py

# Execute the full automated unit + end-to-end test suite
.venv/bin/pytest -v
```
