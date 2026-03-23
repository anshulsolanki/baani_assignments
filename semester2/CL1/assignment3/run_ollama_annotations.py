import requests
import re
import os
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma2:2b"
PROMPTS_FILE = "/Users/baanisolanki/Documents/projects/assignments/semester2/CL1/assignment3/prompts.py"
OUTPUT_DIR = "/Users/baanisolanki/Documents/projects/assignments/semester2/CL1/assignment3"

# ─── One-shot example appended to every prompt to force CoNLL format ───────────
ENGLISH_FORMAT_EXAMPLE = """\
IMPORTANT: Your response must ONLY contain lines in this exact format. No explanations, no markdown, no asterisks, no blank lines between tokens:
TOKEN<TAB>POS<TAB>CHUNK<TAB>NER

Example output for "John went to Paris .":
John\tPROPN\tB-NP\tB-PER
went\tVERB\tB-VP\tO
to\tADP\tB-PP\tO
Paris\tPROPN\tB-NP\tB-LOC
.\tPUNCT\tO\tO

Now annotate sentence below with EXACTLY one token per line in TOKEN\\tPOS\\tCHUNK\\tNER format:
"""

HINDI_FORMAT_EXAMPLE = """\
IMPORTANT: Your response must ONLY contain lines in this exact format. No explanations, no markdown, no asterisks, no blank lines between tokens:
TOKEN<TAB>POS<TAB>CHUNK<TAB>NER

Example output for "बादशाह अकबर ने पूछा ।":
बादशाह\tNN\tB-NP\tO
अकबर\tNNP\tI-NP\tB-PER
ने\tPSP\tB-PP\tO
पूछा\tVM\tB-VP\tO
।\tPUNC\tO\tO

Now annotate sentence below with EXACTLY one token per line in TOKEN\\tPOS\\tCHUNK\\tNER format:
"""


def get_ollama_response(prompt_text, timeout=90):
    payload = {"model": MODEL, "prompt": prompt_text, "stream": False}
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
        return r.json().get("response", "")
    except Exception as e:
        print(f"  [ERROR] {e}")
        return ""


def is_valid_pos_tag(tag):
    """Rough check that a string looks like a POS tag, not noise."""
    # Allow common UD, BIS, PTB tags
    valid_prefixes = ('NOUN','VERB','PROPN','ADJ','ADV','DET','ADP','PRON',
                      'AUX','CCONJ','SCONJ','PUNCT','NUM','PART','INTJ','SYM',
                      'NN','NNP','NNS','VB','VBD','VBG','VBN','VBP','VBZ',
                      'JJ','RB','IN','DT','PRP','CC','TO','CD','WP','WRB',
                      'PSP','VM','VAUX','QF','QC','QO','RP','INJ','NEG',
                      'NST','INTF','SCONJ','ORD','QQ','PUNC','SYN','RDP',
                      'O','B-','I-')
    return any(tag.startswith(p) for p in valid_prefixes)


def parse_conll_response(text):
    """Extract clean 4-column CoNLL lines, filtering out noise."""
    result = []
    for line in text.split("\n"):
        # Strip leading/trailing whitespace
        line = line.strip()
        if not line:
            continue
        # Skip lines that look like explanations, headers, or code fences
        if line.startswith(('#', '`', '*', '-', '>', '|', '=')):
            continue
        if line.upper().startswith(('TOKEN', 'POS', 'CHUNK', 'NER', 'WORD',
                                    'EXAMPLE', 'NOTE', 'HERE', 'THE ', 'THIS')):
            continue

        # Try tab split first (ideal), then 4+ space split
        parts = line.split('\t')
        if len(parts) < 3:
            parts = re.split(r'\s{2,}', line)
        if len(parts) < 2:
            parts = line.split()

        if len(parts) >= 2:
            token = parts[0].strip()
            pos   = parts[1].strip() if len(parts) > 1 else 'O'
            chunk = parts[2].strip() if len(parts) > 2 else 'O'
            ner   = parts[3].strip() if len(parts) > 3 else 'O'

            # Basic sanity: token should be non-empty and not look like a tag
            if not token or len(token) > 50:
                continue
            # Skip obviously wrong parsings where pos looks like garbage
            if len(pos) > 20:
                continue

            # Normalize chunk/NER if they're missing
            if not chunk or chunk == '\\t':
                chunk = 'O'
            if not ner or ner == '\\t':
                ner = 'O'

            result.append(f"{token}\t{pos}\t{chunk}\t{ner}")

    return result


def extract_prompts(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    result = {}
    for i in range(1, 5):
        pattern = rf'prompt_text_{i}\s*=\s*"""(.*?)"""'
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            print(f"[WARN] Could not find prompt_text_{i}")
            continue
        text = match.group(1)

        # Split instructions from sentences
        split_markers = ["Now annotate the sentences:", "Sentences:"]
        instructions_part = text
        sentences_part = text
        for marker in split_markers:
            if marker in text:
                instructions_part, sentences_part = text.split(marker, 1)
                break

        sentence_matches = re.findall(
            r'# sentence \d+\s+(.*?)(?=\n# sentence \d+|$)',
            sentences_part, re.DOTALL
        )
        sentences = [(idx + 1, s.strip()) for idx, s in enumerate(sentence_matches) if s.strip()]

        result[i] = {"instructions": instructions_part.strip(), "sentences": sentences}
        print(f"Prompt {i}: extracted {len(sentences)} sentences.")

    return result


def load_existing_output(output_file):
    done = set()
    if not os.path.exists(output_file):
        return done
    with open(output_file, "r", encoding="utf-8") as f:
        for line in f:
            m = re.match(r'# sentence (\d+)', line)
            if m:
                done.add(int(m.group(1)))
    return done


def annotate_prompt(prompt_idx, instructions, sentences, output_file):
    is_hindi = prompt_idx in (3, 4)
    format_example = HINDI_FORMAT_EXAMPLE if is_hindi else ENGLISH_FORMAT_EXAMPLE

    done = load_existing_output(output_file)
    if done:
        print(f"  Resuming: {len(done)} sentences already annotated.")

    with open(output_file, "a", encoding="utf-8") as f:
        for sent_num, sent_text in sentences:
            if sent_num in done:
                continue
            print(f"  Sentence {sent_num}/{len(sentences)}: {sent_text[:60].strip()}...")

            full_prompt = (
                f"{instructions}\n\n"
                f"{format_example}"
                f"# sentence {sent_num}\n"
                f"{sent_text}\n"
            )

            response = get_ollama_response(full_prompt)
            parsed = parse_conll_response(response)

            f.write(f"# sentence {sent_num}\n")
            if parsed:
                f.write("\n".join(parsed) + "\n")
            else:
                # Log raw response truncated for debug
                raw_excerpt = response[:200].replace('\n', ' ')
                f.write(f"# [NO PARSEABLE OUTPUT] raw: {raw_excerpt}\n")
                print(f"  [WARN] Sentence {sent_num} unparseable.")
            f.write("\n")
            f.flush()


if __name__ == "__main__":
    data = extract_prompts(PROMPTS_FILE)

    for prompt_idx in [4]:
        if prompt_idx not in data:
            continue
        output_file = os.path.join(OUTPUT_DIR, f"output_annotation_{prompt_idx}.conll")
        print(f"\n=== Annotating Prompt {prompt_idx} -> {output_file} ===")
        annotate_prompt(
            prompt_idx,
            data[prompt_idx]["instructions"],
            data[prompt_idx]["sentences"],
            output_file
        )
        print(f"=== Done with Prompt {prompt_idx} ===")

    print("\nAll done.")
