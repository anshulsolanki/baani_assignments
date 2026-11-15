import re
import csv
from nltk.corpus import wordnet as wn

# reading sentences from train.csv, ignoring the class index col (col 0) and extracting only sentence text
def load_sentences_from_csv(csv_path, max_rows=20000):
    sentences = []
    with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        next(reader, None)

        for row in reader:
            if len(row) >= 2:
                sentences.append(row[1].strip())
            if len(sentences) >= max_rows:
                break
    return sentences

# tokenizing each sentence into lowercase alphabet words
def tokenize_corpus_sentences(raw_sentences):
    tokenized_sentences = []
    for sentence in raw_sentences:
        clean_text = sentence.replace("\\", " ").lower()
        tokens = re.findall(r"[a-z]+", clean_text)
        if len(tokens) >= 2:
            tokenized_sentences.append(tokens)
    return tokenized_sentences

# mapping penn treebank pos tags to wordnet pos constants
def map_pos_to_wordnet(pos_tag):
    if not pos_tag:
        return None
    tag = str(pos_tag).upper()
    if tag.startswith("NN") or tag in ("N", "NOUN"):
        return wn.NOUN
    if tag.startswith("VB") or tag in ("V", "VERB"):
        return wn.VERB
    if tag.startswith("JJ") or tag in ("J", "A", "S", "ADJ"):
        return wn.ADJ
    if tag.startswith("RB") or tag in ("R", "ADV"):
        return wn.ADV
    return None

# loading wsd data from wsd-data/wsd_train.txt
def load_wsd_data(file_path, max_rows=2500):
    instances = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line_idx, line in enumerate(f):
            if max_rows is not None and len(instances) >= max_rows:
                break

            parts = line.strip().split("\t")
            if len(parts) != 4:
                continue

            sense_key, lemma_pos, target_idx_str, raw_text = parts
            target_idx = int(target_idx_str)
            tokens = raw_text.split()

            if "." in lemma_pos:
                lemma, pos_char = lemma_pos.split(".", 1)
            else:
                lemma, pos_char = lemma_pos, None

            wn_pos = map_pos_to_wordnet(pos_char)

            gold_synset = None
            if sense_key != "?":
                lemma_obj = wn.lemma_from_key(sense_key)
                gold_synset = lemma_obj.synset().name()

            instances.append({
                "instance_id": line_idx,
                "sense_key": sense_key,
                "gold_synset": gold_synset,
                "lemma_pos": lemma_pos,
                "lemma": lemma,
                "wn_pos": wn_pos,
                "target_index": target_idx,
                "target_word": tokens[target_idx],
                "raw_text": raw_text,
                "tokens": tokens,
            })

    return instances
