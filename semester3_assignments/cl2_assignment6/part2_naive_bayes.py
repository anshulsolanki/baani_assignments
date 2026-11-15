import re
import math
from collections import Counter, defaultdict
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from part2_preprocessing import compute_wsd_metrics
from part2_lesk import predict_mfs_sense, simplified_lesk, improved_lesk

#getting context features for target words by pos tag, neighbourhood words(+/-2 ka window) and content words int he sentce (BoW)
def extract_features(item, stop_words):
    tokens = item["tokens"]
    pos_tags = item["pos_tags"]
    target_idx = item["target_index"]

    features = []
    features.append("POS=" + pos_tags[target_idx][1])

    for offset in (-2, -1, 1, 2):
        nbr_idx = target_idx + offset
        if 0 <= nbr_idx < len(tokens):
            features.append(f"W_{offset}=" + tokens[nbr_idx].lower())
            features.append(f"P_{offset}=" + pos_tags[nbr_idx][1])

    for i, token in enumerate(tokens):
        if i != target_idx:
            word = re.sub(r"[^a-z]", "", token.lower())
            if len(word) > 2 and word not in stop_words:
                features.append("BOW=" + word)

    return features

#traingin multinomial naive bayes classifier per lemma using sense cunts and feature cooccurence counts
def train_naive_bayes(train_instances, stop_words):
    sense_counts = defaultdict(Counter)
    feature_counts = defaultdict(lambda: defaultdict(Counter))
    vocab = defaultdict(set)

    for item in train_instances:
        key = item["lemma_pos"]
        sense = item["gold_synset"]
        feats = extract_features(item, stop_words)

        sense_counts[key][sense] += 1
        for f in feats:
            feature_counts[key][sense][f] += 1
            vocab[key].add(f)

    return {"sense_counts": sense_counts,"feature_counts": feature_counts,"vocab": vocab,}

#predicting sense using highest log-probabiltiy (laplace smoothing done), and using mfs if lemma not in training data
def predict_naive_bayes(model, item, stop_words):
    key = item["lemma_pos"]
    if key not in model["sense_counts"]:
        return predict_mfs_sense(item)

    senses = model["sense_counts"][key]
    total_count = sum(senses.values())
    vocab_size = max(1, len(model["vocab"][key]))
    feats = extract_features(item, stop_words)

    best_sense = None
    best_score = -1e18

    for sense, s_count in senses.items():
        # Log prior: log P(sense)
        log_prob = math.log(s_count / total_count)

        # Log likelihoods: sum log P(f | sense) with Laplace (+1) smoothing
        total_feat_count = sum(model["feature_counts"][key][sense].values())
        denom = total_feat_count + vocab_size

        for f in feats:
            f_count = model["feature_counts"][key][sense].get(f, 0)
            log_prob += math.log((f_count + 1.0) / denom)

        if log_prob > best_score:
            best_score = log_prob
            best_sense = sense

    return best_sense

#trainging naive bayes and comparing with simplified lesk and improved lesk
def part2_problem_7_extra_credit(train_instances, test_instances):
    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()
    nb_model = train_naive_bayes(train_instances, stop_words)

    mfs_preds = []
    basic_preds = []
    imp_preds = []
    nb_preds = []
    gold_labels = []

    for item in test_instances:
        gold_labels.append(item["gold_synset"])
        mfs_preds.append(predict_mfs_sense(item))

        b_pred, _ = simplified_lesk(item)
        basic_preds.append(b_pred)

        i_pred = improved_lesk(item, lemmatizer, stop_words)
        imp_preds.append(i_pred)

        nb_preds.append(predict_naive_bayes(nb_model, item, stop_words))

    return {"MFS_Baseline_Test": compute_wsd_metrics(mfs_preds, gold_labels), "Simplified_Lesk_Test": compute_wsd_metrics(basic_preds, gold_labels),"Improved_Lesk_Test": compute_wsd_metrics(imp_preds, gold_labels),"Naive_Bayes_Test": compute_wsd_metrics(nb_preds, gold_labels),}
