import re
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from data_loader import map_pos_to_wordnet
from part2_preprocessing import compute_wsd_metrics

# problem 3: most frequent sense baseline

# getting most frequent wordnet sense (first synset) for a word
def predict_mfs_sense(item):
    synsets = wn.synsets(item["lemma"], pos=item["wn_pos"])
    if not synsets:
        synsets = wn.synsets(item["target_word"].lower())
    if synsets:
        return synsets[0].name()
    return None

# extractin the most frequent sense from wordnet for each trainging instance and calculating recision, recall, f1 score
def part2_problem_3(train_instances):
    predictions = []
    gold_labels = []

    for item in train_instances:
        pred = predict_mfs_sense(item)
        predictions.append(pred)
        gold_labels.append(item["gold_synset"])

    metrics = compute_wsd_metrics(predictions, gold_labels)
    return metrics, predictions

# problem 4: simplified lesk algorithm

# splitiing strin into set of lowercase alpahbets words
def get_words_from_text(text):
    return set(re.findall(r"[a-z]+", text.lower()))

#implements the algp; gets wordnet senses for target word, collects context words from sentence, builds word set fro each sense, picks the one with max word overlap with context
def simplified_lesk(item):
    senses = wn.synsets(item["target_word"].lower())
    if not senses:
        senses = wn.synsets(item["lemma"])
    if not senses:
        return None, []

    context_words = get_words_from_text(" ".join(item["local_sentence_tokens"]))

    best_sense = senses[0].name()
    max_overlap = -1
    sense_overlaps = []

    for syn in senses:
        gloss_and_examples = syn.definition() + " " + " ".join(syn.examples())
        gloss_words = get_words_from_text(gloss_and_examples)
        overlap_words = sorted(list(context_words.intersection(gloss_words)))
        overlap_count = len(overlap_words)

        sense_overlaps.append({"sense": syn.name(),"gloss": syn.definition(),"overlap_count": overlap_count,"overlap_words": overlap_words,})

        if overlap_count > max_overlap:
            max_overlap = overlap_count
            best_sense = syn.name()

    return best_sense, sense_overlaps

#running the simple lesk algo and calculating precision, recall, f1 socre
def part2_problem_4(train_instances):
    predictions = []
    gold_labels = []
    example = None

    for item in train_instances:
        pred_sense, overlaps = simplified_lesk(item)
        predictions.append(pred_sense)
        gold_labels.append(item["gold_synset"])

        if example is None and len(overlaps) >= 3 and any(o["overlap_count"] > 0 for o in overlaps):
            example = {"sentence": item["raw_text"],"target_word": item["target_word"],"gold_sense": item["gold_synset"],"predicted_sense": pred_sense,"candidates": overlaps,}

    metrics = compute_wsd_metrics(predictions, gold_labels)
    return metrics, predictions, example

#problem 5: improved lesk algo

# 1st improvement: lemmitiationa n stopword removal
def clean_and_lemmatize(text_or_tokens, lemmatizer, stop_words):
    if isinstance(text_or_tokens, str):
        tokens = re.findall(r"[a-z]+", text_or_tokens.lower())
    else:
        tokens = []
        for t in text_or_tokens:
            tokens.extend(re.findall(r"[a-z]+", t.lower()))

    cleaned = set()
    for word in tokens:
        if len(word) <= 2 or word in stop_words:
            continue
        lemma = lemmatizer.lemmatize(word, pos=wn.NOUN)
        lemma = lemmatizer.lemmatize(lemma, pos=wn.VERB)
        if lemma not in stop_words:
            cleaned.add(lemma)
    return cleaned

#3rd improvement: including glosses adn examples of hypernyms and hypomym as well
def get_expanded_gloss_words(synset, lemmatizer, stop_words):
    parts = [synset.definition()] + list(synset.examples())

    for related in synset.hypernyms() + synset.hyponyms():
        parts.append(related.definition())
        parts.extend(related.examples())

    full_text = " ".join(parts)
    return clean_and_lemmatize(full_text, lemmatizer, stop_words)

#applying the 4 improvemnets to get better lesk algo
def improved_lesk(item, lemmatizer, stop_words):
    w_idx = item["target_index"]
    pos_tag = item["pos_tags"][w_idx][1]
    wn_pos = map_pos_to_wordnet(pos_tag) or item["wn_pos"]

    #2nd improvement: POS-based filtering
    if wn_pos is not None:
        senses = wn.synsets(item["lemma"], pos=wn_pos)
    else:
        senses = wn.synsets(item["lemma"])

    if not senses:
        senses = wn.synsets(item["target_word"].lower())
    if not senses:
        return None

    # 4rth improvement: expanding context window to include neighboring sentences
    context_tokens = [tok for i, tok in enumerate(item["tokens"]) if i != w_idx]

    # 1st improvement applied
    context_words = clean_and_lemmatize(context_tokens, lemmatizer, stop_words)

    best_sense = senses[0].name()
    max_overlap = -1

    for syn in senses:
        gloss_words = get_expanded_gloss_words(syn, lemmatizer, stop_words) #3rd improvement applied
        overlap = len(context_words.intersection(gloss_words))

        if overlap > max_overlap:
            max_overlap = overlap
            best_sense = syn.name()

    return best_sense

# running improved lesk algo and calculating precision, recall and f1 score
def part2_problem_5(train_instances):
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words("english"))

    predictions = []
    gold_labels = []

    for item in train_instances:
        pred = improved_lesk(item, lemmatizer, stop_words)
        predictions.append(pred)
        gold_labels.append(item["gold_synset"])

    metrics = compute_wsd_metrics(predictions, gold_labels)
    return metrics, predictions

#problem 6: evaluaation and analysis of 10 ambiguous words

#selcting 10 ambiguoug words and comparing predicted sense from basci lesk algo vs improved lesk algo vs wordnet's intended sense
def part2_problem_6(train_instances, basic_preds, improved_preds):
    selected = []
    seen_lemmas = set()

    for idx, item in enumerate(train_instances):
        lemma = item["lemma"].lower()
        gold_sense = item["gold_synset"]
        b_pred = basic_preds[idx]
        i_pred = improved_preds[idx]

        if lemma not in seen_lemmas:
            seen_lemmas.add(lemma)
            gold_gloss = wn.synset(gold_sense).definition()
            b_gloss = wn.synset(b_pred).definition() if b_pred else "None"
            i_gloss = wn.synset(i_pred).definition() if i_pred else "None"

            selected.append({"word": item["target_word"],"lemma": item["lemma"], "sentence": item["raw_text"], "gold_sense": gold_sense,"gold_gloss": gold_gloss,"basic_pred": b_pred,"basic_gloss": b_gloss,"improved_pred": i_pred,"improved_gloss": i_gloss,})
            if len(selected) == 10:
                break

    return selected
