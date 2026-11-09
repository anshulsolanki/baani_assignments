"""Linguistically grounded Devanagari-to-Roman (Readable Hinglish) Transliterator.

Why a custom linguistic transliterator instead of raw ITRANS / IAST?
1. Raw ITRANS outputs awkward Sanskrit-style mixed case and undeleted schwas
   (e.g., `rAma maMdira meM sarakAra` instead of `Ram Mandir mein sarkar`).
2. Academic IAST outputs non-ASCII diacritics (`rāma mandira mēṁ`).
3. For Hinglish / Hindi political news discourse analysis in Roman script,
   readers expect natural, readable ASCII Romanization with:
   - Indo-Aryan word-final schwa deletion (`राम` -> `Ram`, `मंदिर` -> `mandir`),
   - Medial schwa deletion before long-vowel syllables (`सरकार` -> `sarkar`, `जनता` -> `janta`),
   - Homorganic nasal assimilation for anusvara (`मंदिर` -> `n`, `संबित` -> `m`),
   - Natural Hinglish spellings for high-frequency words & named entities,
   - A strict guarantee of ZERO Devanagari characters (`\\u0900`-`\\u097F`) in output.
"""

import re
import unicodedata
from typing import Dict, List, Tuple

DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")

# Pre-composed Nukta consonants decomposed in NFD or written as 2 codepoints
NUKTA_PAIRS: Dict[str, str] = {
    "\u0915\u093c": "\u0958",  # क़
    "\u0916\u093c": "\u0959",  # ख़
    "\u0917\u093c": "\u095a",  # ग़
    "\u091c\u093c": "\u095b",  # ज़
    "\u0921\u093c": "\u095c",  # ड़
    "\u0922\u093c": "\u095d",  # ढ़
    "\u092b\u093c": "\u095e",  # फ़
    "\u092f\u093c": "\u095f",  # य़
}

INDEPENDENT_VOWELS: Dict[str, str] = {
    "अ": "a",
    "आ": "aa",
    "इ": "i",
    "ई": "ee",
    "उ": "u",
    "ऊ": "oo",
    "ऋ": "ri",
    "ॠ": "ri",
    "ऌ": "li",
    "ऍ": "e",
    "ऎ": "e",
    "ए": "e",
    "ऐ": "ai",
    "ऑ": "o",
    "ऒ": "o",
    "ओ": "o",
    "औ": "au",
}

VOWEL_MATRAS: Dict[str, str] = {
    "ा": "a",   # Word-internal/final 'aa' vs 'a' handled contextually below
    "ि": "i",
    "ी": "i",
    "ु": "u",
    "ू": "oo",
    "ृ": "ri",
    "ॄ": "ri",
    "ॅ": "e",
    "ॆ": "e",
    "े": "e",
    "ै": "ai",
    "ॉ": "o",
    "ॊ": "o",
    "ो": "o",
    "ौ": "au",
}

LONG_MATRAS = {"ा", "ी", "ू", "े", "ै", "ो", "ौ", "ॉ"}

CONSONANTS: Dict[str, str] = {
    "क": "k",
    "ख": "kh",
    "ग": "g",
    "घ": "gh",
    "ङ": "ng",
    "च": "ch",
    "छ": "chh",
    "ज": "j",
    "झ": "jh",
    "ञ": "ny",
    "ट": "t",
    "ठ": "th",
    "ड": "d",
    "ढ": "dh",
    "ण": "n",
    "त": "t",
    "थ": "th",
    "द": "d",
    "ध": "dh",
    "न": "n",
    "ऩ": "n",
    "प": "p",
    "फ": "ph",
    "ब": "b",
    "भ": "bh",
    "म": "m",
    "य": "y",
    "र": "r",
    "ऱ": "r",
    "ल": "l",
    "ळ": "l",
    "ऴ": "l",
    "व": "v",
    "श": "sh",
    "ष": "sh",
    "स": "s",
    "ह": "h",
    # Nukta precomposed consonants
    "\u0958": "q",   # क़
    "\u0959": "kh",  # ख़
    "\u095a": "gh",  # ग़
    "\u095b": "z",   # ज़
    "\u095c": "d",   # ड़ (e.g., बड़ा -> bada, करोड़ -> karod)
    "\u095d": "dh",  # ढ़ (e.g., पढ़ना -> padhna)
    "\u095e": "f",   # फ़
    "\u095f": "y",   # य़
}

LABIAL_CONSONANTS = {"प", "फ", "\u095e", "ब", "भ", "म"}

DEVANAGARI_DIGITS: Dict[str, str] = {
    "०": "0",
    "१": "1",
    "२": "2",
    "३": "3",
    "४": "4",
    "५": "5",
    "६": "6",
    "७": "7",
    "८": "8",
    "९": "9",
}

PUNCTUATION_MAP: Dict[str, str] = {
    "।": ".",
    "॥": ".",
    "॰": ".",
    "ॐ": "Om",
    "ऽ": "",
}

VIRAMA = "्"
ANUSVARA = "ं"
CHANDRABINDU = "ँ"
VISARGA = "ः"
NUKTA = "़"

# High-frequency Hinglish function words, political terms, and named entities
LEXICAL_OVERRIDES: Dict[str, str] = {
    # Function words & auxiliaries
    "मैं": "main",
    "में": "mein",
    "मे": "mein",
    "है": "hai",
    "हैं": "hain",
    "हूँ": "hoon",
    "हूं": "hoon",
    "हो": "ho",
    "था": "tha",
    "थी": "thi",
    "थे": "the",
    "थीं": "thin",
    "नहीं": "nahin",
    "नही": "nahin",
    "यह": "yeh",
    "ये": "ye",
    "वह": "woh",
    "वो": "wo",
    "इस": "is",
    "उस": "us",
    "एक": "ek",
    "और": "aur",
    "या": "ya",
    "कि": "ki",
    "की": "ki",
    "के": "ke",
    "का": "ka",
    "को": "ko",
    "से": "se",
    "पर": "par",
    "पे": "pe",
    "ने": "ne",
    "तो": "toh",
    "भी": "bhi",
    "ही": "hi",
    "जो": "jo",
    "जब": "jab",
    "तब": "tab",
    "अब": "ab",
    "कब": "kab",
    "क्या": "kya",
    "क्यों": "kyon",
    "क्योंकि": "kyunki",
    "कैसे": "kaise",
    "कहाँ": "kahan",
    "कहां": "kahan",
    "यहाँ": "yahan",
    "यहां": "yahan",
    "वहाँ": "wahan",
    "वहां": "wahan",
    "लेकिन": "lekin",
    "मगर": "magar",
    "अगर": "agar",
    "कोई": "koi",
    "कुछ": "kuch",
    "सब": "sab",
    "सभी": "sabhi",
    "बहुत": "bahut",
    "ज्यादा": "zyada",
    "ज़्यादा": "zyada",
    "सिर्फ": "sirf",
    "सिर्फ़": "sirf",
    "फिर": "phir",
    "फ़िर": "phir",
    "खुद": "khud",
    "ख़ुद": "khud",
    "साथ": "saath",
    "आज": "aaj",
    "कल": "kal",
    "बात": "baat",
    "लोग": "log",
    "लोगों": "logon",
    "तरह": "tarah",
    "वजह": "wajah",
    # Domain-specific named entities & English loanwords in Hindi transcripts
    "राम": "Ram",
    "मंदिर": "Mandir",
    "अयोध्या": "Ayodhya",
    "ट्रस्ट": "Trust",
    "चंदा": "chanda",
    "चंदे": "chande",
    "दान": "daan",
    "घोटाला": "ghotala",
    "घोटाले": "ghotale",
    "स्कैम": "scam",
    "भ्रष्टाचार": "bhrashtachar",
    "मोदी": "Modi",
    "योगी": "Yogi",
    "राहुल": "Rahul",
    "गांधी": "Gandhi",
    "धर्मेंद्र": "Dharmendra",
    "प्रधान": "Pradhan",
    "अर्णब": "Arnab",
    "गोस्वामी": "Goswami",
    "सार्थक": "Sarthak",
    "ध्रुव": "Dhruv",
    "राठी": "Rathee",
    "मोहक": "Mohak",
    "मंगल": "Mangal",
    "अंजना": "Anjana",
    "कश्यप": "Kashyap",
    "बीजेपी": "BJP",
    "भाजपा": "BJP",
    "कांग्रेस": "Congress",
    "आरएसएस": "RSS",
    "संघ": "Sangh",
    "विपक्ष": "vipaksh",
    "सरकार": "sarkar",
    "नीट": "NEET",
    "एनटीए": "NTA",
    "सीजेपी": "CJP",
    "पेपर": "paper",
    "लीक": "leak",
    "छात्र": "chhatra",
    "छात्रों": "chhatron",
    "स्टूडेंट": "student",
    "स्टूडेंट्स": "students",
    "प्रोटेस्ट": "protest",
    "प्रदर्शन": "pradarshan",
    "प्रदर्शनकारी": "pradarshankari",
    "प्रदर्शनकारियों": "pradarshankariyon",
    "आंदोलन": "aandolan",
    "आंदोलनकारी": "aandolankari",
    "जंतर": "Jantar",
    "मंतर": "Mantar",
    "पुलिस": "police",
    "सुप्रीम": "Supreme",
    "कोर्ट": "Court",
    "मीडिया": "media",
    "वीडियो": "video",
    "इंडिया": "India",
    "भारत": "Bharat",
    "हिंदू": "Hindu",
    "हिन्दू": "Hindu",
    "धर्म": "dharma",
    "आस्था": "aastha",
    "करोड़": "crore",
    "लाख": "lakh",
    "रुपये": "rupaye",
    "रुपए": "rupaye",
    "पैसा": "paisa",
    "पैसे": "paise",
    "सवाल": "sawal",
    "जवाब": "jawab",
    "आरोप": "aarop",
    "सबूत": "saboot",
    "जांच": "jaanch",
    "जाँच": "jaanch",
    "रिपोर्ट": "report",
    "न्यूज़": "news",
    "न्यूज": "news",
    "चैनल": "channel",
    "लाइव": "live",
    "इस्तीफा": "isteefa",
    "इस्तीफ़ा": "isteefa",
}


def _normalize_nuktas(word: str) -> str:
    """Normalize decomposed consonant+nukta sequences into single codepoints."""
    norm = unicodedata.normalize("NFC", word)
    for pair, single in NUKTA_PAIRS.items():
        norm = norm.replace(pair, single)
    return norm


def transliterate_devanagari_word(word: str) -> str:
    """Transliterate a single Devanagari token into natural ASCII Roman Hindi."""
    norm_word = _normalize_nuktas(word)
    if norm_word in LEXICAL_OVERRIDES:
        return LEXICAL_OVERRIDES[norm_word]

    # Parse token into structured units so we can apply Hindi schwa-deletion cleanly
    # Unit tuple: (kind, base_roman, vowel_roman, has_explicit_matra, raw_char)
    units: List[Tuple[str, str, str, bool, str]] = []
    i = 0
    n = len(norm_word)

    while i < n:
        ch = norm_word[i]

        if ch in DEVANAGARI_DIGITS:
            units.append(("OTHER", DEVANAGARI_DIGITS[ch], "", False, ch))
            i += 1
        elif ch in PUNCTUATION_MAP:
            units.append(("OTHER", PUNCTUATION_MAP[ch], "", False, ch))
            i += 1
        elif ch in INDEPENDENT_VOWELS:
            v_rom = INDEPENDENT_VOWELS[ch]
            # Check trailing anusvara/chandrabindu on independent vowel (e.g., आँ -> aan)
            if i + 1 < n and norm_word[i + 1] in (ANUSVARA, CHANDRABINDU):
                next_c = norm_word[i + 2] if i + 2 < n else ""
                nasal = "m" if next_c in LABIAL_CONSONANTS else "n"
                units.append(("VOWEL", v_rom + nasal, "", True, ch))
                i += 2
            else:
                units.append(("VOWEL", v_rom, "", True, ch))
                i += 1
        elif ch in CONSONANTS:
            c_rom = CONSONANTS[ch]
            i += 1
            # Consume stray nukta if uncombined
            if i < n and norm_word[i] == NUKTA:
                i += 1

            if i < n and norm_word[i] == VIRAMA:
                # Conjunct consonant with explicit virama -> no inherent schwa
                i += 1
                units.append(("CONS_HALF", c_rom, "", False, ch))
            elif i < n and norm_word[i] in VOWEL_MATRAS:
                matra = norm_word[i]
                # Use 'aa' for ा in single-syllable closed words like नाम -> naam, काम -> kaam
                v_rom = VOWEL_MATRAS[matra]
                i += 1
                nasal = ""
                if i < n and norm_word[i] in (ANUSVARA, CHANDRABINDU):
                    next_c = norm_word[i + 1] if i + 1 < n else ""
                    if norm_word[i] == CHANDRABINDU:
                        nasal = "n"
                    else:
                        nasal = "m" if next_c in LABIAL_CONSONANTS else "n"
                    i += 1
                units.append(("CONS_MATRA", c_rom, v_rom + nasal, True, matra))
            else:
                # Consonant with inherent schwa 'a'
                nasal = ""
                if i < n and norm_word[i] in (ANUSVARA, CHANDRABINDU):
                    next_c = norm_word[i + 1] if i + 1 < n else ""
                    nasal = "m" if next_c in LABIAL_CONSONANTS else "n"
                    i += 1
                    # Nasalized inherent vowel is NEVER deleted (e.g., मंदिर -> mandir, बंद -> band)
                    units.append(("CONS_MATRA", c_rom, "a" + nasal, True, ch))
                else:
                    units.append(("CONS_SCHWA", c_rom, "a", False, ch))
        elif ch in (ANUSVARA, CHANDRABINDU):
            next_c = norm_word[i + 1] if i + 1 < n else ""
            nasal = "m" if next_c in LABIAL_CONSONANTS else "n"
            units.append(("OTHER", nasal, "", False, ch))
            i += 1
        elif ch == VISARGA:
            units.append(("OTHER", "h", "", False, ch))
            i += 1
        elif ch in (VIRAMA, NUKTA):
            i += 1
        else:
            # Any other character: strip if inside Devanagari block
            if not DEVANAGARI_RE.match(ch):
                units.append(("OTHER", ch, "", False, ch))
            i += 1

    # Apply Hindi Schwa Deletion Rules on CONS_SCHWA units
    num_units = len(units)
    syllable_Bearing = [u for u in units if u[0] in ("VOWEL", "CONS_MATRA", "CONS_SCHWA")]
    total_syllables = len(syllable_Bearing)

    # Upgrade 'ा' to 'aa' in monosyllabic CVC words (e.g., नाम -> naam, साल -> saal, आम -> aam)
    if total_syllables == 2 and num_units == 2:
        if units[0][0] == "CONS_MATRA" and units[0][4] == "ा" and units[0][2] == "a" and units[1][0] == "CONS_SCHWA":
            units[0] = ("CONS_MATRA", units[0][1], "aa", True, "ा")

    output_parts: List[str] = []
    for idx, (kind, base_rom, v_rom, has_matra, raw_ch) in enumerate(units):
        if kind != "CONS_SCHWA":
            output_parts.append(base_rom + v_rom)
            continue

        # Decide whether inherent schwa 'a' is kept or deleted:
        keep_schwa = True

        # Rule 1: Word-final consonant drops inherent schwa in Modern Hindi
        # EXCEPT: single-consonant words (e.g., न -> na) OR preceded by a half-consonant
        # where cluster needs release vowel (e.g., छात्र -> chhatra, सत्य -> satya)
        is_word_final = all(u[0] == "OTHER" for u in units[idx + 1 :])
        if is_word_final and total_syllables > 1:
            prev_is_half = idx > 0 and units[idx - 1][0] == "CONS_HALF"
            if prev_is_half and raw_ch in ("र", "य", "व"):
                keep_schwa = True
            else:
                keep_schwa = False

        # Rule 2: Word-medial schwa deletion (`VCaCV` -> `VCCV`)
        # If preceded by a full vowel/syllable (not word-initial, not preceded by half-consonant)
        # AND followed by a consonant carrying an explicit vowel matra (e.g., जनता -> janta, करना -> karna)
        elif idx > 0 and idx + 1 < num_units:
            prev_kind = units[idx - 1][0]
            next_kind = units[idx + 1][0]
            next_raw = units[idx + 1][4]
            if (
                prev_kind in ("VOWEL", "CONS_MATRA", "CONS_SCHWA")
                and next_kind == "CONS_MATRA"
                and next_raw in LONG_MATRAS
            ):
                # Avoid creating unpronounceable 3-consonant clusters if previous schwa already dropped
                keep_schwa = False

        output_parts.append(base_rom + ("a" if keep_schwa else ""))

    result = "".join(output_parts)
    # Final safety guard: ensure zero Devanagari characters survive
    result = DEVANAGARI_RE.sub("", result)
    return result


TOKEN_SPLIT_RE = re.compile(r"([\u0900-\u097F]+)")


ACRONYM_NORMALIZATIONS: Tuple[Tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\besaaaeeti\b", re.IGNORECASE), "SIT"),
    (re.compile(r"\bephaaaeeaar\b", re.IGNORECASE), "FIR"),
    (re.compile(r"\besbiaaee\b", re.IGNORECASE), "SBI"),
    (re.compile(r"\bsisitivi\b", re.IGNORECASE), "CCTV"),
    (re.compile(r"\bsibiaaee\b", re.IGNORECASE), "CBI"),
    (re.compile(r"\bbiechpi\b", re.IGNORECASE), "VHP"),
    (re.compile(r"\bviechpi\b", re.IGNORECASE), "VHP"),
    (re.compile(r"\bpiem\b"), "PM"),
    (re.compile(r"\bsiem\b"), "CM"),
    (re.compile(r"\byoopi\b"), "UP"),
)

NON_LATIN_SCRIPT_RE = re.compile(r"[\u0600-\u06FF\u0900-\u0DFF]")


def romanize_text(text: str) -> str:
    """Convert any Devanagari text into clean ASCII Roman script while preserving
    existing English words, numbers, punctuation, and timestamps untouched."""
    if not text:
        return ""

    # Replace dandas even when adjacent to spaces/English
    cleaned = text.replace("।", ".").replace("॥", ".")
    # Strip any stray non-Latin ASR noise outside Devanagari (e.g. Arabic script glitches)
    cleaned = re.sub(r"[\u0600-\u06FF]", "", cleaned)
    parts = TOKEN_SPLIT_RE.split(cleaned)
    out: List[str] = []
    for part in parts:
        if not part:
            continue
        if DEVANAGARI_RE.search(part):
            out.append(transliterate_devanagari_word(part))
        else:
            out.append(part)

    joined = "".join(out)
    for pattern, replacement in ACRONYM_NORMALIZATIONS:
        joined = pattern.sub(replacement, joined)
    # Strip any residual Indic/Arabic script marks if present, normalize whitespace
    joined = NON_LATIN_SCRIPT_RE.sub("", joined)
    joined = re.sub(r"[ \t]+", " ", joined).strip()
    return joined


def contains_devanagari(text: str) -> bool:
    """Return True if any Unicode character in the Devanagari block (U+0900..U+097F) is present."""
    return bool(DEVANAGARI_RE.search(text))
