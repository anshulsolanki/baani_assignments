"""Comprehensive Automated Test Suite for the LNS News Discourse Analysis Project.

Covers:
1. Unit tests for `video_catalog.py` (6 creators, 2 events, 11 active videos + 1 skipped).
2. Unit tests for `romanizer.py` (Devanagari -> Roman script, Hindi schwa deletion,
   nuktas, conjuncts, mixed English/Hinglish preservation, 0-Devanagari guarantee).
3. Unit tests for timestamp formatting (`[MM:SS]` and `[HH:MM:SS]`).
4. End-to-end validation of all 11 extracted transcripts:
   - Existence & non-emptiness
   - Strictly ZERO Devanagari characters (`\\u0900`..`\\u097F`)
   - Valid `[MM:SS]` / `[HH:MM:SS]` timestamp on every transcript line
   - Native non-AI-dubbed source verification
   - Strictly ZERO leftover audio/video media files anywhere in the project
5. End-to-end validation of all 6 Creator Analysis Worksheets (`.md` + `.pdf`):
   - Existence & valid PDF headers
   - Strictly ZERO Devanagari characters
   - Complete coverage of Event 1 (8 questions), Event 2 (9 questions), 5 shared
     discourse features, Short Summaries, Blank Excerpt Records, and End-of-Event
     Summaries
   - Mandatory `[MM:SS]` timestamps cited alongside observations & quotes
6. Validation of the 4 project documentation files (`Viva_Guide.md`,
   `Implementation_Details.md`, `Understanding_Guide.md`, `README.md`).
"""

import json
import re
import sys
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from scripts.fetch_transcripts import format_timestamp, format_upload_date
from scripts.romanizer import (
    contains_devanagari,
    romanize_text,
    transliterate_devanagari_word,
)
from scripts.video_catalog import (
    CREATORS,
    EVENTS,
    VIDEO_CATALOG,
    get_active_videos,
    get_entries_for_creator,
)

TIMESTAMP_LINE_RE = re.compile(r"^\[(\d{2}:)?\d{2}:\d{2}\]\s+\S+")
INLINE_TIMESTAMP_RE = re.compile(r"\[(\d{1,2}:)?\d{2}:\d{2}(?:\s*[-–]\s*(\d{1,2}:)?\d{2}:\d{2})?\]")
AUDIO_VIDEO_EXTENSIONS = {".mp3", ".m4a", ".wav", ".webm", ".opus", ".mp4", ".ogg", ".flac", ".aac"}

EXPECTED_CREATOR_FILES = [
    ("sarthak_goswami", "01_Sarthak_Goswami_Analysis", True),
    ("dhruv_rathee", "02_Dhruv_Rathee_Analysis", True),
    ("mohak_mangal", "03_Mohak_Mangal_Analysis", False),  # Event 1 skipped per instructions
    ("aaj_tak", "04_Aaj_Tak_Analysis", True),
    ("republic_tv", "05_Republic_TV_Analysis", True),
    ("the_wire", "06_The_Wire_Analysis", True),
]


# ==============================================================================
# 1. Unit Tests: Video Catalog
# ==============================================================================
class TestVideoCatalog:
    def test_six_creators_and_two_events(self):
        assert len(CREATORS) == 6
        assert set(EVENTS.keys()) == {1, 2}
        assert len(VIDEO_CATALOG) == 12  # 6 creators x 2 events

    def test_eleven_active_videos_and_mohak_skipped_event1(self):
        active = get_active_videos()
        assert len(active) == 11
        ev1 = [v for v in active if v.event_number == 1]
        ev2 = [v for v in active if v.event_number == 2]
        assert len(ev1) == 5
        assert len(ev2) == 6

        mohak_entries = get_entries_for_creator("mohak_mangal")
        assert len(mohak_entries) == 2
        assert mohak_entries[0].is_skipped is True
        assert mohak_entries[1].is_skipped is False
        assert mohak_entries[1].video_id == "v-RikSqb0Vw"

    def test_all_active_video_ids_are_unique(self):
        ids = [v.video_id for v in get_active_videos()]
        assert len(ids) == len(set(ids)) == 11


# ==============================================================================
# 2. Unit Tests: Devanagari-to-Roman Transliterator
# ==============================================================================
class TestRomanizer:
    def test_zero_devanagari_on_complex_hindi_inputs(self):
        samples = [
            "राम मंदिर को किसने 'लूटा'?",
            "पीएम आवास के बाहर धरने पर बैठे राहुल गांधी!",
            "छात्रों का प्रदर्शन और पुलिस की कार्रवाई।",
            "क़ानून, ख़बर, ग़लत, ज़मीन, बड़ा, पढ़ाई, फ़ैसला — २०२६ में १०० करोड़ रुपये॥",
            "अ आ इ ई उ ऊ ऋ ए ऐ ओ औ अं अः क ख ग घ ङ च छ ज झ ञ ट ठ ड ढ ण त थ द ध न प फ ब भ म य र ल व श ष स ह",
        ]
        for s in samples:
            assert contains_devanagari(s) is True
            rom = romanize_text(s)
            assert rom != ""
            assert contains_devanagari(rom) is False, f"Devanagari leaked in: {rom}"

    def test_natural_schwa_deletion_and_key_terms(self):
        assert romanize_text("राम मंदिर को किसने 'लूटा'?") == "Ram Mandir ko kisne 'loota'?"
        assert transliterate_devanagari_word("सरकार") == "sarkar"
        assert transliterate_devanagari_word("छात्र") == "chhatra"
        assert transliterate_devanagari_word("प्रदर्शन") == "pradarshan"
        assert transliterate_devanagari_word("जनता") == "janta"
        assert transliterate_devanagari_word("नाम") == "naam"

    def test_mixed_english_and_timestamps_untouched(self):
        mixed = "[04:15] BJP aur Congress ke beech NEET paper leak par debate"
        assert romanize_text(mixed) == mixed


# ==============================================================================
# 3. Unit Tests: Timestamp & Date Formatting
# ==============================================================================
class TestFormattingHelpers:
    def test_format_timestamp(self):
        assert format_timestamp(0) == "[00:00]"
        assert format_timestamp(65.9) == "[01:05]"
        assert format_timestamp(3599) == "[59:59]"
        assert format_timestamp(3661) == "[01:01:01]"
        assert format_timestamp(75, force_hours=True) == "[00:01:15]"

    def test_format_upload_date(self):
        assert format_upload_date("20260721") == "2026-07-21"
        assert format_upload_date(None) == "Unknown"


# ==============================================================================
# 4. End-to-End Tests: Extracted Transcripts & Zero-Audio Policy
# ==============================================================================
class TestExtractedTranscripts:
    def test_all_11_transcript_files_exist_and_non_empty(self):
        for entry in get_active_videos():
            path = PROJECT_DIR / "transcripts" / entry.event_id / entry.transcript_filename
            assert path.is_file(), f"Missing transcript file: {path}"
            content = path.read_text(encoding="utf-8")
            assert len(content) > 500, f"Transcript suspiciously short: {path}"

    def test_zero_devanagari_across_all_11_transcripts_and_metadata(self):
        for entry in get_active_videos():
            path = PROJECT_DIR / "transcripts" / entry.event_id / entry.transcript_filename
            content = path.read_text(encoding="utf-8")
            assert not contains_devanagari(content), f"Devanagari characters found in {path}"

        meta_path = PROJECT_DIR / "transcripts" / "metadata_index.json"
        assert meta_path.is_file()
        meta_text = meta_path.read_text(encoding="utf-8")
        assert not contains_devanagari(meta_text), "Devanagari found in metadata_index.json"

    def test_every_transcript_utterance_line_has_valid_timestamp(self):
        for entry in get_active_videos():
            path = PROJECT_DIR / "transcripts" / entry.event_id / entry.transcript_filename
            lines = path.read_text(encoding="utf-8").splitlines()
            # Body starts after the second '====...' separator line
            sep_indices = [i for i, ln in enumerate(lines) if ln.startswith("====")]
            assert len(sep_indices) >= 3, f"Header delimiters missing in {path}"
            body_lines = [ln.strip() for ln in lines[sep_indices[2] + 1 :] if ln.strip()]
            assert len(body_lines) >= 15, f"Too few transcript lines in {path}"
            for ln in body_lines:
                assert TIMESTAMP_LINE_RE.match(ln), f"Line missing [MM:SS] timestamp in {path}: {ln[:80]}"

    def test_native_non_ai_dubbed_caption_tracks_used(self):
        meta_path = PROJECT_DIR / "transcripts" / "metadata_index.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        assert len(meta) == 11
        for vid, info in meta.items():
            assert "dub" not in info["caption_source"].lower()
            assert info["native_lang"] in {"hi", "en"}
            tpath = PROJECT_DIR / info["transcript_relpath"]
            header_text = "\n".join(tpath.read_text(encoding="utf-8").splitlines()[:14])
            assert "Non-AI-Dubbed Original Track" in header_text
            if info["creator_id"] in {"sarthak_goswami", "dhruv_rathee", "mohak_mangal", "aaj_tak"}:
                assert info["native_lang"] == "hi", f"Expected native Hindi track for {vid}"
            else:
                assert info["native_lang"] == "en", f"Expected native English track for {vid}"

    def test_zero_audio_or_video_files_stored_anywhere(self):
        offending = [
            p for p in PROJECT_DIR.rglob("*")
            if p.is_file() and ".venv" not in p.parts and p.suffix.lower() in AUDIO_VIDEO_EXTENSIONS
        ]
        assert offending == [], f"Found prohibited audio/video files on disk: {offending}"


# ==============================================================================
# 5. End-to-End Tests: 6 Filled Creator Analysis Worksheets (.md + .pdf)
# ==============================================================================
class TestAnalysisWorksheets:
    def test_all_6_creator_forms_exist_in_markdown_and_pdf(self):
        forms_dir = PROJECT_DIR / "analysis_forms"
        assert forms_dir.is_dir(), "analysis_forms/ directory missing"
        for _, basename, _ in EXPECTED_CREATOR_FILES:
            md_path = forms_dir / f"{basename}.md"
            pdf_path = forms_dir / f"{basename}.pdf"
            assert md_path.is_file(), f"Missing Markdown worksheet: {md_path}"
            assert pdf_path.is_file(), f"Missing PDF worksheet: {pdf_path}"
            assert md_path.stat().st_size > 4000, f"Markdown worksheet too short: {md_path}"
            pdf_bytes = pdf_path.read_bytes()
            assert pdf_bytes.startswith(b"%PDF-"), f"Invalid PDF header in {pdf_path}"
            assert len(pdf_bytes) > 15000, f"PDF suspiciously small: {pdf_path}"

    def test_zero_devanagari_in_all_creator_forms(self):
        forms_dir = PROJECT_DIR / "analysis_forms"
        for _, basename, _ in EXPECTED_CREATOR_FILES:
            md_path = forms_dir / f"{basename}.md"
            text = md_path.read_text(encoding="utf-8")
            assert not contains_devanagari(text), f"Devanagari characters found in {md_path}"

    def test_worksheet_sections_and_mandatory_timestamps(self):
        forms_dir = PROJECT_DIR / "analysis_forms"
        required_features = [
            "Naming",
            "Presupposition",
            "Agency",
            "Antagonisation",
            "Intensification",
        ]
        for creator_id, basename, has_event1 in EXPECTED_CREATOR_FILES:
            md_path = forms_dir / f"{basename}.md"
            text = md_path.read_text(encoding="utf-8")

            # Check Event 1 & Event 2 headers
            assert "Event 1" in text or "Event1" in text
            assert "Event 2" in text or "Event2" in text

            # Check shared features present
            for feat in required_features:
                assert feat in text, f"Feature '{feat}' missing in {basename}.md"

            # Check Blank Excerpt Record & End-of-event summary sections
            assert "Blank Excerpt Record" in text or "Blank excerpt record" in text
            assert "End-of-Event Summary" in text or "End-of-event summary" in text

            # Check abundant inline [MM:SS] timestamps alongside instances
            ts_matches = INLINE_TIMESTAMP_RE.findall(text)
            min_ts = 25 if has_event1 else 14
            assert len(ts_matches) >= min_ts, (
                f"Expected at least {min_ts} timestamp citations in {basename}.md, found {len(ts_matches)}"
            )

    def test_strict_alignment_with_analysis_form_pdf_template(self):
        """Verify all 6 worksheets contain every section, prompt, metadata label,
        table header, and reminder from `analysis_form.pdf` (Pages 1–6)."""
        forms_dir = PROJECT_DIR / "analysis_forms"
        required_verbatim_strings = [
            "Qualitative analysis of political news discourse",
            "## Guidelines: Five features to look for in every event",
            "| Feature | What to look for | Illustrative example | Questions to answer |",
            "Reminder: A label or implication is not automatically false or manipulative. Examine the surrounding context and evidence.",
            "## Event1. Ram Mandir donation controversy",
            "**Focus:** How is the controversy framed—as financial accountability, religious sentiment, political motivation, or something else? Be precise about the specific allegation or episode covered.",
            "## Event2. Students' protest regarding NEET paper leak",
            "**Focus:** How does coverage construct the legitimacy of student protest and responsibility for the underlying problem?",
            "- **Outlet:**",
            "- **Date:**",
            "- **Video title:**",
            "- **Timestamp(s):**",
            "- **Analyst:**",
            "- **Language:**",
            "### Event-specific questions",
            "### Apply the five shared features",
            "| Feature | Exact wording + timestamp | What it does in context |",
            "| **5. Intensification / softening** |",
            "### Short summary",
            "- **What interpretation of the event does this video encourage?**",
            "- **Whose perspective is foregrounded, challenged, or missing?**",
            "- **What evidence supports your interpretation? What complicates it?**",
            "## Common form: Blank excerpt record",
            "Copy or print this page whenever you find a passage worth analysing. Keep the exact wording and enough context to interpret it.",
            "- **Exact transcript excerpt:**",
            "- **Feature(s):**",
            "- **Who is speaking? Is this the outlet's wording or a quotation?**",
            "- **What does the wording imply, foreground, soften, or leave unstated?**",
            "- **What context or evidence supports or complicates this interpretation?**",
            "- **How does another outlet describe the same event or actor?**",
            "- **My interpretation, with reasons:**",
            "## Common form: End-of-event summary",
            "- **The main way this outlet framed the event was:**",
            "- **The strongest linguistic evidence was (quote + timestamp):**",
            "- **The shared feature(s) most clearly illustrated were:**",
            "- **An alternative interpretation of the same evidence is:**",
            "- **What I cannot conclude from this transcript alone:**",
            "Research reminder: interpret wording in context, distinguish allegations from established facts, and support claims with exact excerpts. Mixed or contradictory evidence is worth recording.",
        ]
        for _, basename, _ in EXPECTED_CREATOR_FILES:
            md_path = forms_dir / f"{basename}.md"
            text = md_path.read_text(encoding="utf-8")
            for expected in required_verbatim_strings:
                assert expected in text, (
                    f"Missing exact analysis_form.pdf template element '{expected}' in {basename}.md"
                )
            # Also ensure no 3-space nested bullets remain that would collapse in python-markdown
            collapsed_bullets = re.findall(r"(?m)^ {3}-\s+", text)
            assert collapsed_bullets == [], f"Found 3-space nested bullets in {basename}.md"


# ==============================================================================
# 6. Documentation & Study Guides Tests
# ==============================================================================
class TestDocumentationDeliverables:
    @pytest.mark.parametrize(
        "doc_name",
        [
            "Viva_Guide.md",
            "Implementation_Details.md",
            "Understanding_Guide.md",
            "README.md",
        ],
    )
    def test_documentation_file_exists_and_is_comprehensive(self, doc_name: str):
        path = PROJECT_DIR / doc_name
        assert path.is_file(), f"Missing required documentation file: {doc_name}"
        content = path.read_text(encoding="utf-8")
        assert len(content) > 2500, f"Documentation file {doc_name} is too brief"
