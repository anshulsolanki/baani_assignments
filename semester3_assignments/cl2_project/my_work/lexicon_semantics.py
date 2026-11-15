
from nltk.corpus import opinion_lexicon
from preprocess import flatten, ensure_nltk


def build_lexicon():
    # CORRECTION 2a: Ensure NLTK data is ready before loading opinion_lexicon
    ensure_nltk()
    lexicon = {}

    for word in opinion_lexicon.positive():
        lexicon[word] = 1.0

    for word in opinion_lexicon.negative():
        lexicon[word] = -1.0

    return lexicon


def apply_lexicon(sentences, lexicon):
    for token in flatten(sentences):
        # CORRECTION 2b: Check lowercase word first so "-ing"/"-ed" adjectives lemmatized as verbs are not missed
        polarity = lexicon.get(token.text.lower(), lexicon.get(token.lemma, 0.0))
        token.prior_polarity = polarity
        token.shifted_polarity = polarity

    return sentences


def lexicon_features(sentences):
    tokens = flatten(sentences)

    total_words = max(
        1,
        sum(1 for t in tokens if any(c.isalnum() for c in t.text))
    )

    positive = [t.prior_polarity for t in tokens if t.prior_polarity > 0]
    negative = [t.prior_polarity for t in tokens if t.prior_polarity < 0]

    return {
        "lex_pos_density": sum(positive) / total_words,
        "lex_neg_density": abs(sum(negative)) / total_words,
        "lex_pos_count_density": len(positive) / total_words,
        "lex_neg_count_density": len(negative) / total_words,
        "lex_total_density": (len(positive) + len(negative)) / total_words,
        "lex_polarity_density": sum(positive + negative) / total_words,
        # CORRECTION 4a: Non-negative net polarity features so Multinomial Naive Bayes does not drop net polarity
        "lex_pos_excess_density": max(0.0, sum(positive + negative)) / total_words,
        "lex_neg_excess_density": max(0.0, -sum(positive + negative)) / total_words
    }
