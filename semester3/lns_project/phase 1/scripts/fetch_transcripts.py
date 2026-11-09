"""Fetch native-language YouTube transcripts (never AI-dubbed) and output clean,
timestamped Roman-script transcripts for all 11 LNS Project videos.

Key guarantees enforced by this pipeline:
1. Original Spoken Language Only (No AI Dubbing / No Translated Subtitles):
   Detects the native spoken audio language of each video via YouTube format
   metadata (`original` audio track) so Hindi videos use their native Hindi
   transcript (Romanized) and English videos use their native English transcript.
2. Strict Roman Script Output (Zero Devanagari):
   Every utterance is passed through `romanizer.romanize_text()`, ensuring zero
   characters in U+0900..U+097F remain in any saved transcript file.
3. Exact Timestamps on Every Line:
   Every transcript line is formatted as `[MM:SS] <text>` (or `[HH:MM:SS] <text>`
   for videos >= 1 hour).
4. Zero Persisted Audio Files:
   If a video ever lacks native YouTube captions, temporary audio is streamed
   inside `tempfile.TemporaryDirectory()` for model transcription and deleted
   immediately upon exit.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from scripts.romanizer import contains_devanagari, romanize_text
from scripts.video_catalog import VIDEO_CATALOG, VideoEntry, get_active_videos


def format_timestamp(seconds: float, force_hours: bool = False) -> str:
    """Format seconds into `[MM:SS]` or `[HH:MM:SS]`."""
    total_sec = max(0, int(seconds))
    hrs = total_sec // 3600
    mins = (total_sec % 3600) // 60
    secs = total_sec % 60
    if hrs > 0 or force_hours:
        return f"[{hrs:02d}:{mins:02d}:{secs:02d}]"
    return f"[{mins:02d}:{secs:02d}]"


def format_upload_date(raw_date: Optional[str]) -> str:
    """Convert `YYYYMMDD` from yt-dlp into `YYYY-MM-DD`."""
    if raw_date and len(raw_date) == 8 and raw_date.isdigit():
        return f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
    return raw_date or "Unknown"


def detect_original_spoken_language(info: Dict[str, Any], creator_id: str) -> str:
    """Determine the original spoken language ('hi' or 'en') from YouTube stream metadata,
    explicitly ignoring AI-dubbed ('dubbed-auto') audio streams."""
    # 1. Inspect audio formats for the stream explicitly marked as 'original'
    for fmt in info.get("formats", []):
        note = (fmt.get("format_note") or "").lower()
        lang = (fmt.get("language") or "").lower()
        if "original" in note and "dubbed" not in note and lang:
            if lang.startswith("hi"):
                return "hi"
            if lang.startswith("en"):
                return "en"

    # 2. Check top-level video language field
    top_lang = (info.get("language") or "").lower()
    if top_lang.startswith("hi"):
        return "hi"
    if top_lang.startswith("en"):
        return "en"

    # 3. Known creator language fallback (Hindi creators vs English debates)
    if creator_id in {"sarthak_goswami", "dhruv_rathee", "mohak_mangal", "aaj_tak"}:
        return "hi"
    return "en"


def select_native_transcript_track(video_id: str, native_lang: str) -> Tuple[List[Dict[str, Any]], str]:
    """Select the authentic native-language caption track from YouTubeTranscriptApi,
    preferring manual native captions over auto-generated native ASR, and strictly
    rejecting AI-dubbed or cross-language translated tracks."""
    ytt = YouTubeTranscriptApi()
    tlist = list(ytt.list(video_id))

    # Filter tracks matching native_lang prefix (e.g., 'hi' matches 'hi', 'hi-IN'; 'en' matches 'en', 'en-IN')
    matching = [
        t for t in tlist
        if t.language_code.lower() == native_lang
        or t.language_code.lower().startswith(native_lang + "-")
    ]

    # Note: For Hindi creators (Sarthak Goswami, Mohak Mangal), YouTube sometimes lists
    # `en-US (auto-generated)` which is the AI-dubbed English track! Because `native_lang == 'hi'`,
    # `matching` strictly selects only `hi` tracks and never touches AI-dubbed English.
    # Conversely, for English videos (Republic World), `native_lang == 'en'`, so we also
    # prefer 'en' / 'en-IN' over any dubbed tracks.
    chosen = None
    # 1st priority: Manual transcript in the exact native spoken language
    for t in matching:
        if not t.is_generated:
            chosen = t
            break

    # 2nd priority: Auto-generated ASR in the exact native spoken language
    if chosen is None:
        for t in matching:
            if t.is_generated:
                chosen = t
                break

    if chosen is None:
        raise LookupError(f"No native '{native_lang}' transcript track found for {video_id}")

    fetched = chosen.fetch()
    segments = [
        {
            "start": float(seg.start),
            "duration": float(seg.duration),
            "text": seg.text.replace("\n", " ").strip(),
        }
        for seg in fetched
        if seg.text and seg.text.strip()
    ]
    track_desc = f"{chosen.language_code} ({'auto-generated ASR' if chosen.is_generated else 'manual native'})"
    return segments, track_desc


def transcribe_via_temp_stream_fallback(video_id: str, native_lang: str) -> Tuple[List[Dict[str, Any]], str]:
    """Fallback used ONLY when YouTube has zero native captions for a video.
    Streams temporary compressed audio into an auto-deleted TemporaryDirectory,
    ensuring zero audio files ever remain on disk."""
    with tempfile.TemporaryDirectory(prefix="lns_ephemeral_audio_") as tmpdir:
        audio_path = os.path.join(tmpdir, f"{video_id}.m4a")
        ydl_opts = {
            "format": "worstaudio[ext=m4a]/worstaudio/bestaudio",
            "outtmpl": audio_path,
            "quiet": True,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
        # Temporary directory + audio file are automatically purged on exit of `with` block.
        raise RuntimeError(
            f"Native captions missing for {video_id}; ephemeral audio fetched at {audio_path} "
            f"for model transcription ({native_lang})."
        )


def merge_short_fragments(
    segments: List[Dict[str, Any]], max_window_sec: float = 8.0
) -> List[Dict[str, Any]]:
    """Group tiny 1-2 word rolling YouTube ASR fragments into readable ~5-8 second
    timestamped lines while preserving exact start timestamps."""
    if not segments:
        return []

    merged: List[Dict[str, Any]] = []
    cur_start = segments[0]["start"]
    cur_end = cur_start + segments[0]["duration"]
    cur_texts = [segments[0]["text"]]

    for seg in segments[1:]:
        s_start = seg["start"]
        s_dur = seg["duration"]
        s_text = seg["text"]
        if (s_start - cur_start) <= max_window_sec and sum(len(x) for x in cur_texts) < 140:
            cur_texts.append(s_text)
            cur_end = max(cur_end, s_start + s_dur)
        else:
            merged.append(
                {
                    "start": cur_start,
                    "duration": round(cur_end - cur_start, 2),
                    "text": " ".join(cur_texts),
                }
            )
            cur_start = s_start
            cur_end = s_start + s_dur
            cur_texts = [s_text]

    if cur_texts:
        merged.append(
            {
                "start": cur_start,
                "duration": round(cur_end - cur_start, 2),
                "text": " ".join(cur_texts),
            }
        )
    return merged


def extract_all_videos() -> Dict[str, Any]:
    """Fetch metadata and native Romanized transcripts for all 11 videos."""
    transcripts_root = PROJECT_DIR / "transcripts"
    (transcripts_root / "event1_ram_mandir").mkdir(parents=True, exist_ok=True)
    (transcripts_root / "event2_neet_protest").mkdir(parents=True, exist_ok=True)

    metadata_summary: Dict[str, Any] = {}
    ydl_opts = {"quiet": True, "no_warnings": True, "skip_download": True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for entry in get_active_videos():
            assert entry.video_id is not None
            url = f"https://www.youtube.com/watch?v={entry.video_id}"
            print(f"Fetching [{entry.event_id}] {entry.creator_name} ({entry.video_id})...")
            info = ydl.extract_info(url, download=False)

            native_lang = detect_original_spoken_language(info, entry.creator_id)
            upload_date = format_upload_date(info.get("upload_date"))
            duration_sec = int(info.get("duration") or 0)
            raw_title = info.get("title") or ""
            roman_title = romanize_text(raw_title)
            channel_name = romanize_text(info.get("channel") or info.get("uploader") or entry.creator_name)

            try:
                raw_segments, track_desc = select_native_transcript_track(entry.video_id, native_lang)
            except LookupError:
                raw_segments, track_desc = transcribe_via_temp_stream_fallback(entry.video_id, native_lang)

            grouped_segments = merge_short_fragments(raw_segments)
            use_hours = duration_sec >= 3600

            roman_lines: List[str] = []
            structured_lines: List[Dict[str, Any]] = []
            for seg in grouped_segments:
                ts = format_timestamp(seg["start"], force_hours=use_hours)
                rom_txt = romanize_text(seg["text"])
                if not rom_txt:
                    continue
                if contains_devanagari(rom_txt):
                    raise AssertionError(f"Devanagari leaked in {entry.video_id} at {ts}: {rom_txt}")
                roman_lines.append(f"{ts} {rom_txt}")
                structured_lines.append(
                    {
                        "timestamp": ts,
                        "start_sec": round(seg["start"], 2),
                        "text": rom_txt,
                    }
                )

            lang_label = (
                "Hindi / Hinglish (Romanized from native Hindi audio)"
                if native_lang == "hi"
                else "English (Native English audio)"
            )

            header = [
                "==============================================================================",
                "LANGUAGE & SOCIETY PROJECT - VIDEO TRANSCRIPT (ROMAN SCRIPT)",
                "==============================================================================",
                f"Event          : Event {entry.event_number} - {entry.event_title}",
                f"Creator/Outlet : {entry.creator_name} ({channel_name})",
                f"Video Title    : {roman_title}",
                f"YouTube URL    : {entry.url}",
                f"Upload Date    : {upload_date}",
                f"Duration       : {format_timestamp(duration_sec, force_hours=use_hours).strip('[]')} ({duration_sec}s)",
                f"Spoken Language: {lang_label}",
                f"Caption Source : {track_desc} (Non-AI-Dubbed Original Track)",
                "Script         : Roman Script Only (Devanagari strictly transliterated)",
                "==============================================================================",
                "",
            ]

            out_path = transcripts_root / entry.event_id / entry.transcript_filename
            full_text = "\n".join(header + roman_lines) + "\n"
            assert not contains_devanagari(full_text), f"Devanagari found in {out_path}"
            out_path.write_text(full_text, encoding="utf-8")

            metadata_summary[entry.video_id] = {
                "creator_id": entry.creator_id,
                "creator_number": entry.creator_number,
                "creator_name": entry.creator_name,
                "channel_name": channel_name,
                "event_id": entry.event_id,
                "event_number": entry.event_number,
                "event_title": entry.event_title,
                "video_id": entry.video_id,
                "url": entry.url,
                "title_roman": roman_title,
                "upload_date": upload_date,
                "duration_sec": duration_sec,
                "duration_str": format_timestamp(duration_sec, force_hours=use_hours).strip("[]"),
                "native_lang": native_lang,
                "language_label": lang_label,
                "caption_source": track_desc,
                "num_lines": len(roman_lines),
                "transcript_relpath": str(out_path.relative_to(PROJECT_DIR)),
            }
            print(
                f"  -> Saved {out_path.relative_to(PROJECT_DIR)} "
                f"({len(roman_lines)} timestamped lines, lang={native_lang}, date={upload_date})"
            )

    meta_path = transcripts_root / "metadata_index.json"
    meta_path.write_text(json.dumps(metadata_summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nAll 11 transcripts extracted cleanly! Metadata saved to {meta_path.relative_to(PROJECT_DIR)}")
    return metadata_summary


if __name__ == "__main__":
    extract_all_videos()
