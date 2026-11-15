import re
import json
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import wordnet as wn
from data_loader import map_pos_to_wordnet

# extracting the single sentence containing the target word
def extract_local_sentence(tokens, target_idx):
    start = target_idx
    while start > 0 and tokens[start - 1] not in (".", "!", "?", ";"):
        start -= 1

    end = target_idx
    while end < len(tokens) and tokens[end] not in (".", "!", "?", ";"):
        end += 1

    local_tokens = []
    for i in range(start, end):
        if i != target_idx:
            local_tokens.append(tokens[i])
    return local_tokens

#preprocessing nad pos tg=agging
def part2_problem_1(wsd_instances):
    preprocessed = []
    for item in wsd_instances:
        raw_text = item["raw_text"]

        # Sentence-level and word-level tokenization
        sentences = sent_tokenize(raw_text)
        word_tokens = word_tokenize(raw_text)

        # POS tag the aligned tokens so target_index points to the exact tag
        pos_tags = nltk.pos_tag(item["tokens"])
        local_sent_tokens = extract_local_sentence(item["tokens"], item["target_index"])

        new_item = dict(item)
        new_item["sentences"] = sentences
        new_item["word_tokens"] = word_tokens
        new_item["pos_tags"] = pos_tags
        new_item["local_sentence_tokens"] = local_sent_tokens
        preprocessed.append(new_item)

    return preprocessed

#possible sneses with definition and gloss and usage eg in a json file
def part2_problem_2(train_instances, output_json_path):
    first_10_senses = {}

    for idx, item in enumerate(train_instances[:10]):
        sent_key = f"Sentence_{idx + 1}"
        content_words = []

        for word, pos_tag in item["pos_tags"]:
            clean_word = re.sub(r"[^a-zA-Z]", "", word).lower()
            wn_pos = map_pos_to_wordnet(pos_tag)
            if not clean_word or wn_pos is None:
                continue

            synsets = wn.synsets(clean_word, pos=wn_pos)
            if not synsets:
                continue

            sense_list = []
            for syn in synsets:
                sense_list.append({"sense": syn.name(), "gloss": syn.definition(),"examples": syn.examples(),})

            content_words.append({"word": word,"pos": pos_tag,"senses": sense_list,})

        first_10_senses[sent_key] = {"target_word": item["target_word"],"sentence_text": item["raw_text"],"content_words": content_words,}

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(first_10_senses, f, indent=2)

    return first_10_senses

#calculating precision, recall and f1 score
def compute_wsd_metrics(predictions, gold_labels):
    correct = 0
    attempted = 0
    total = len(gold_labels)

    for pred, gold in zip(predictions, gold_labels):
        if pred is not None:
            attempted += 1
            if pred == gold:
                correct += 1

    precision = (correct / attempted) if attempted > 0 else 0.0
    recall = (correct / total) if total > 0 else 0.0
    if precision + recall > 0:
        f1 = (2.0 * precision * recall) / (precision + recall)
    else:
        f1 = 0.0

    return {"precision": precision * 100.0, "recall": recall * 100.0,"f1": f1 * 100.0,}
