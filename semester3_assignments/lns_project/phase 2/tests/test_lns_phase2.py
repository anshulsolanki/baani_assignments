"""
test_lns_phase2.py - Automated verification tests for Phase 2 (Non-Verbal Analysis).

Author: Baani Solanki (2025114016)
Course: Language and Society (Phase 2 - Non-Verbal & Multimodal Discourse Analysis)
"""

import os
import re
import unittest

PHASE2_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORMS_DIR = os.path.join(PHASE2_DIR, "analysis_forms")
LATEX_DIR = os.path.join(FORMS_DIR, "latex")

EXPECTED_CREATORS = [
    "01_Sarthak_Goswami_NonVerbal_Analysis",
    "02_Dhruv_Rathee_NonVerbal_Analysis",
    "03_Mohak_Mangal_NonVerbal_Analysis",
    "04_Aaj_Tak_NonVerbal_Analysis",
    "05_Republic_TV_NonVerbal_Analysis",
    "06_The_Wire_NonVerbal_Analysis",
]

REQUIRED_SECTIONS = [
    "Guidelines: Five non-verbal & paralinguistic features to look for in every event",
    "Quick Multimodal Transcription Notation Key",
    "Methodological Reminder:",
    "Event 1. Ram Mandir donation controversy (Non-Verbal & Paralinguistic Layer)",
    "Event-specific non-verbal questions (Event 1)",
    "Apply the five non-verbal features (Event 1)",
    "Short summary (Event 1 Non-Verbal Synthesis)",
    "Event 2. Students' protest regarding NEET paper leak (Non-Verbal & Paralinguistic Layer)",
    "Event-specific non-verbal questions (Event 2)",
    "Apply the five non-verbal features (Event 2)",
    "Short summary (Event 2 Non-Verbal Synthesis)",
]

DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")
TIMESTAMP_RE = re.compile(r"\[\d{2}:\d{2}\]")


class TestPhase2NonVerbal(unittest.TestCase):
    """Test suite verifying all Phase 2 deliverables and guidelines compliance."""

    def test_all_six_markdown_worksheets_exist(self):
        """Verify all 6 creator Markdown worksheets exist and are substantial."""
        for base in EXPECTED_CREATORS:
            md_path = os.path.join(FORMS_DIR, base + ".md")
            self.assertTrue(os.path.isfile(md_path), f"Missing Markdown file: {md_path}")
            self.assertGreater(os.path.getsize(md_path), 10000, f"File too small: {md_path}")

    def test_all_six_pdf_worksheets_exist_and_valid(self):
        """Verify all 6 rendered PDFs exist, start with %PDF, and exceed 15 KB."""
        for base in EXPECTED_CREATORS:
            pdf_path = os.path.join(FORMS_DIR, base + ".pdf")
            self.assertTrue(os.path.isfile(pdf_path), f"Missing PDF file: {pdf_path}")
            self.assertGreater(os.path.getsize(pdf_path), 15000, f"PDF too small: {pdf_path}")
            with open(pdf_path, "rb") as f:
                header = f.read(4)
            self.assertEqual(header, b"%PDF", f"Invalid PDF header in {pdf_path}")

    def test_all_latex_files_exist(self):
        """Verify individual and combined Overleaf LaTeX (.tex) files exist."""
        for base in EXPECTED_CREATORS:
            tex_path = os.path.join(LATEX_DIR, base + ".tex")
            self.assertTrue(os.path.isfile(tex_path), f"Missing LaTeX file: {tex_path}")
        combined = os.path.join(LATEX_DIR, "All_6_Creators_Combined_NonVerbal_Analysis.tex")
        self.assertTrue(os.path.isfile(combined), "Missing combined LaTeX file")

    def test_zero_devanagari_characters_anywhere(self):
        """Ensure 100% Roman-script compliance (zero Devanagari characters)."""
        for root, _, files in os.walk(PHASE2_DIR):
            for fname in files:
                if fname.endswith((".md", ".py", ".tex")):
                    fpath = os.path.join(root, fname)
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                    match = DEVANAGARI_RE.search(content)
                    self.assertIsNone(
                        match,
                        f"Found forbidden Devanagari character in {fpath}: {match}",
                    )

    def test_required_form_sections_and_multimodal_notation(self):
        """Verify every worksheet has all form headings, timestamps, and notation."""
        for base in EXPECTED_CREATORS:
            md_path = os.path.join(FORMS_DIR, base + ".md")
            with open(md_path, "r", encoding="utf-8") as f:
                text = f.read()

            for section in REQUIRED_SECTIONS:
                self.assertIn(section, text, f"Missing '{section}' in {base}.md")

            timestamps = TIMESTAMP_RE.findall(text)
            self.assertGreaterEqual(
                len(timestamps), 15, f"Too few timestamps in {base}.md"
            )

            for symbol in ["(.)", "...", "↑", "↓", "[sigh]", "{{gesture:"]:
                self.assertIn(symbol, text, f"Missing symbol '{symbol}' in {base}.md")

    def test_mohak_mangal_event1_marked_skipped(self):
        """Verify Mohak Mangal Event 1 is explicitly marked Skipped per guidelines."""
        mohak_path = os.path.join(FORMS_DIR, "03_Mohak_Mangal_NonVerbal_Analysis.md")
        with open(mohak_path, "r", encoding="utf-8") as f:
            text = f.read()
        self.assertIn("Skipped", text)

    def test_zero_audio_or_video_files(self):
        """Ensure no raw audio/video media files are stored in the repository."""
        forbidden_exts = (".mp4", ".mkv", ".webm", ".mp3", ".wav", ".m4a")
        for root, _, files in os.walk(PHASE2_DIR):
            for fname in files:
                self.assertFalse(
                    fname.lower().endswith(forbidden_exts),
                    f"Forbidden media file found: {os.path.join(root, fname)}",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
