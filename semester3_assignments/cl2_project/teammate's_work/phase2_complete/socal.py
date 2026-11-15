
import numpy as np

from lexicon_semantics import build_lexicon
from preprocess import preprocess, flatten
from config import INTENSIFIERS

NEGATORS = {"not", "n't", "never", "no", "hardly"}

class SOCal:

    def __init__(self, lexicon=None):
        self.lexicon = lexicon if lexicon is not None else build_lexicon()

    def score_review(self, review):

        sentences = preprocess(review)
        tokens = flatten(sentences)

        scores = []

        for i, token in enumerate(tokens):

            polarity = self.lexicon.get(token.lemma, 0.0)

            if polarity == 0:
                continue

            # Check preceding tokens for negation
            for j in range(max(0, i - 6), i):
                previous = tokens[j]

                if previous.text.lower() in NEGATORS:
                    polarity = -polarity
                    break

            # Check preceding tokens for intensifiers/downtoners
            for j in range(max(0, i - 3), i):
                previous = tokens[j]
                word = previous.text.lower()

                if word in INTENSIFIERS:
                    polarity *= INTENSIFIERS[word]

            scores.append(polarity)

        if not scores:
            return 0.0

        return float(np.mean(scores))

    def predict(self, reviews):
        scores = self.predict_scores(reviews)
        return np.where(scores > 0, 1, np.where(scores < 0, 0, -1))

    def predict_scores(self, reviews):
        return np.array([
            self.score_review(review)
            for review in reviews
        ])
