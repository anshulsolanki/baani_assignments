"""Canonical catalog of creators, events, and YouTube videos for the LNS Project.

All 11 video links come directly from `lns_project_instructions.pdf`.
Mohak Mangal has no video for Event 1 (Ram Mandir donation controversy) per the
project instructions and is explicitly recorded as skipped.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class VideoEntry:
    creator_id: str
    creator_number: int
    creator_name: str
    event_id: str
    event_number: int
    event_title: str
    video_id: Optional[str]
    url: Optional[str]
    skipped_reason: Optional[str] = None

    @property
    def is_skipped(self) -> bool:
        return self.video_id is None

    @property
    def transcript_filename(self) -> Optional[str]:
        if self.is_skipped:
            return None
        return f"{self.creator_number:02d}_{self.creator_id}_{self.video_id}.txt"


CREATORS = [
    (1, "sarthak_goswami", "Sarthak Goswami"),
    (2, "dhruv_rathee", "Dhruv Rathee"),
    (3, "mohak_mangal", "Mohak Mangal"),
    (4, "aaj_tak", "Aaj Tak"),
    (5, "republic_tv", "Republic TV"),
    (6, "the_wire", "The Wire"),
]

EVENTS = {
    1: ("event1_ram_mandir", "Ram Mandir donation controversy"),
    2: ("event2_neet_protest", "Students' protest regarding NEET paper leak"),
}

VIDEO_CATALOG: List[VideoEntry] = [
    # --- Event 1: Ram Mandir donation controversy ---
    VideoEntry(
        creator_id="sarthak_goswami",
        creator_number=1,
        creator_name="Sarthak Goswami",
        event_id="event1_ram_mandir",
        event_number=1,
        event_title="Ram Mandir donation controversy",
        video_id="lb7gZnyZH0c",
        url="https://youtu.be/lb7gZnyZH0c?si=QvgBq0ACOhcx0pdO",
    ),
    VideoEntry(
        creator_id="dhruv_rathee",
        creator_number=2,
        creator_name="Dhruv Rathee",
        event_id="event1_ram_mandir",
        event_number=1,
        event_title="Ram Mandir donation controversy",
        video_id="oeH0fOSJuX8",
        url="https://youtu.be/oeH0fOSJuX8?si=tGAGQeFY_MRU32Az",
    ),
    VideoEntry(
        creator_id="mohak_mangal",
        creator_number=3,
        creator_name="Mohak Mangal",
        event_id="event1_ram_mandir",
        event_number=1,
        event_title="Ram Mandir donation controversy",
        video_id=None,
        url=None,
        skipped_reason="No video relevant to scam; there is video regarding history, so skipping.",
    ),
    VideoEntry(
        creator_id="aaj_tak",
        creator_number=4,
        creator_name="Aaj Tak",
        event_id="event1_ram_mandir",
        event_number=1,
        event_title="Ram Mandir donation controversy",
        video_id="B4L1pz0o4dc",
        url="https://youtu.be/B4L1pz0o4dc?si=BRvYR4hn3KalxM_t",
    ),
    VideoEntry(
        creator_id="republic_tv",
        creator_number=5,
        creator_name="Republic TV",
        event_id="event1_ram_mandir",
        event_number=1,
        event_title="Ram Mandir donation controversy",
        video_id="0H-bruoEkaY",
        url="https://youtu.be/0H-bruoEkaY?si=T9EqDVN39KNILYKg",
    ),
    VideoEntry(
        creator_id="the_wire",
        creator_number=6,
        creator_name="The Wire",
        event_id="event1_ram_mandir",
        event_number=1,
        event_title="Ram Mandir donation controversy",
        video_id="7rUL8fGgRJA",
        url="https://youtu.be/7rUL8fGgRJA?si=9HV3jAYEipsTwvAI",
    ),
    # --- Event 2: Students' protest regarding NEET paper leak ---
    VideoEntry(
        creator_id="sarthak_goswami",
        creator_number=1,
        creator_name="Sarthak Goswami",
        event_id="event2_neet_protest",
        event_number=2,
        event_title="Students' protest regarding NEET paper leak",
        video_id="EM1GeZufO6E",
        url="https://youtu.be/EM1GeZufO6E?si=PgvQ7GHqNjZJIZET",
    ),
    VideoEntry(
        creator_id="dhruv_rathee",
        creator_number=2,
        creator_name="Dhruv Rathee",
        event_id="event2_neet_protest",
        event_number=2,
        event_title="Students' protest regarding NEET paper leak",
        video_id="l-6Pm-112io",
        url="https://youtu.be/l-6Pm-112io?si=TXnmzWqiJKF-qXev",
    ),
    VideoEntry(
        creator_id="mohak_mangal",
        creator_number=3,
        creator_name="Mohak Mangal",
        event_id="event2_neet_protest",
        event_number=2,
        event_title="Students' protest regarding NEET paper leak",
        video_id="v-RikSqb0Vw",
        url="https://youtu.be/v-RikSqb0Vw?si=T4KGrNSGutHG4YYO",
    ),
    VideoEntry(
        creator_id="aaj_tak",
        creator_number=4,
        creator_name="Aaj Tak",
        event_id="event2_neet_protest",
        event_number=2,
        event_title="Students' protest regarding NEET paper leak",
        video_id="JXLIs0WtJAM",
        url="https://www.youtube.com/live/JXLIs0WtJAM?si=3_7gAW9j4KDBWCUo",
    ),
    VideoEntry(
        creator_id="republic_tv",
        creator_number=5,
        creator_name="Republic TV",
        event_id="event2_neet_protest",
        event_number=2,
        event_title="Students' protest regarding NEET paper leak",
        video_id="HTvb6E_1Qdc",
        url="https://youtu.be/HTvb6E_1Qdc?si=7aFf_zysFjpvX8af",
    ),
    VideoEntry(
        creator_id="the_wire",
        creator_number=6,
        creator_name="The Wire",
        event_id="event2_neet_protest",
        event_number=2,
        event_title="Students' protest regarding NEET paper leak",
        video_id="pYaTVvHeGoM",
        url="https://youtu.be/pYaTVvHeGoM?si=TPLfYLT3eB6UHh5o",
    ),
]


def get_active_videos() -> List[VideoEntry]:
    """Return the 11 active videos that require transcript extraction and analysis."""
    return [entry for entry in VIDEO_CATALOG if not entry.is_skipped]


def get_entries_for_creator(creator_id: str) -> List[VideoEntry]:
    """Return Event 1 and Event 2 entries for a given creator."""
    return [entry for entry in VIDEO_CATALOG if entry.creator_id == creator_id]
