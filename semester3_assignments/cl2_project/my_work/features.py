
from collections import Counter

from preprocess import preprocess
from lexicon_semantics import apply_lexicon, lexicon_features
from compositional_rules import apply_shifters, shifter_features
# ADDED FOR PHASE 3 (M3 & M4): Import anaphora and RST discourse modules
from anaphora_salience import apply_anaphora, anaphora_features
from rst_discourse import apply_rst, rst_features


def bow_features(sentences):
    features = Counter()

    for sentence in sentences:
        tokens = [
            token.lemma.lower()
            for token in sentence.tokens
            if any(ch.isalnum() for ch in token.text)
        ]

        # unigrams
        for token in tokens:
            features[f"UNI_{token}"] += 1

        # bigrams
        for i in range(len(tokens) - 1):
            features[f"BI_{tokens[i]}_{tokens[i+1]}"] += 1

    return dict(features)


def extract_features(review, model="M0", lexicon=None):

    # ADDED FOR PHASE 3 (M3 & M4): Allow M0 through M4
    if model not in {"M0", "M1", "M2", "M3", "M4"}:
        raise ValueError("Model must be M0, M1, M2, M3 or M4")

    sentences = preprocess(review)

    features = bow_features(sentences)

    if model in {"M1", "M2", "M3", "M4"}:
        if lexicon is None:
            raise ValueError("A sentiment lexicon is required")

        apply_lexicon(sentences, lexicon)
        features.update(lexicon_features(sentences))

    if model in {"M2", "M3", "M4"}:
        apply_shifters(sentences)
        features.update(shifter_features(sentences))

    # ADDED FOR PHASE 3 (M3): Apply pronominal anaphora resolution and entity salience
    if model in {"M3", "M4"}:
        apply_anaphora(sentences)
        features.update(anaphora_features(sentences))

    # ADDED FOR PHASE 3 (M4): Apply RST EDU segmentation and Nucleus/Satellite weighting
    if model == "M4":
        apply_rst(sentences)
        features.update(rst_features(sentences))

    return features
