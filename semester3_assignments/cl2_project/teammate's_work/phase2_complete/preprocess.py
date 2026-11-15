
from dataclasses import dataclass, field
from typing import List

import nltk

from nltk import sent_tokenize, word_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer

@dataclass
class Token:

    text: str
    lemma: str
    pos: str

    sent_id: int
    index: int

    clause_id: int = 0
    edu_id: int = 0

    prior_polarity: float = 0.0
    shifted_polarity: float = 0.0

    weight: float = 1.0

    entity: str = ""
    is_pronoun: bool = False

@dataclass
class Sentence:

    text: str
    sent_id: int

    tokens: List[Token] = field(default_factory=list)

lemmatizer = WordNetLemmatizer()

_nltk_ready = False


def ensure_nltk():

    global _nltk_ready

    if _nltk_ready:
        return

    resources = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        (
            "taggers/averaged_perceptron_tagger_eng",
            "averaged_perceptron_tagger_eng"
        ),
        ("corpora/wordnet", "wordnet"),
        ("corpora/opinion_lexicon", "opinion_lexicon")
    ]

    for path, package in resources:

        try:
            nltk.data.find(path)

        except LookupError:
            nltk.download(package, quiet=True)

    _nltk_ready = True

def wn_pos(tag):

    if tag.startswith("J"):
        return "a"

    if tag.startswith("V"):
        return "v"

    if tag.startswith("N"):
        return "n"

    if tag.startswith("R"):
        return "r"

    return "n"

def preprocess(doc):

    ensure_nltk()

    if not isinstance(doc, str):
        raise TypeError("Document must be a string")

    result = []

    raw_sentences = sent_tokenize(doc)

    for sid, sent in enumerate(raw_sentences):

        tagged = pos_tag(word_tokenize(sent))

        tokens = []

        clause = 0

        for i, (word, tag) in enumerate(tagged):

            # Detect clause boundaries
            if word.lower() in {
                "but", "yet", "however", ";"
            }:
                clause += 1

            lemma = lemmatizer.lemmatize(
                word.lower(),
                wn_pos(tag)
            )

            token = Token(
                text=word,
                lemma=lemma,
                pos=tag,
                sent_id=sid,
                index=i,
                clause_id=clause,
                is_pronoun=tag in {"PRP", "PRP$"}
            )

            tokens.append(token)

            if word in {",", ";", ":"}:
                clause += 1

        result.append(
            Sentence(
                text=sent,
                sent_id=sid,
                tokens=tokens
            )
        )

    return result

def flatten(sentences):

    return [
        token
        for sentence in sentences
        for token in sentence.tokens
    ]
