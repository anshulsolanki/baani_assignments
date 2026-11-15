
from preprocess import preprocess, flatten
from lexicon_semantics import (
    build_lexicon,
    apply_lexicon,
    lexicon_features
)
from compositional_rules import (
    apply_shifters,
    shifter_features
)
from features_2 import extract_features
from socal import SOCal


def run_tests():

    lexicon = build_lexicon()

    # 1. Lexicon tests
    assert lexicon["excellent"] > 0
    assert lexicon["bad"] < 0
    assert lexicon["terrible"] < 0

    print("PASS: Lexicon tests")

    sentences = preprocess(
        "The acting was excellent but the story was terrible."
    )
    apply_lexicon(sentences, lexicon)
    features = lexicon_features(sentences)

    assert features["lex_pos_count_density"] > 0
    assert features["lex_neg_count_density"] > 0

    print("PASS: Lexicon feature extraction")

    sentences = preprocess("The movie was not good.")
    apply_lexicon(sentences, lexicon)
    apply_shifters(sentences)

    shift_features = shifter_features(sentences)

    assert shift_features["shift_neg_density"] > 0

    print("PASS: Negation handling")

    review = "The movie was very good but the ending was terrible."

    m0 = extract_features(review, model="M0", lexicon=lexicon)
    m1 = extract_features(review, model="M1", lexicon=lexicon)
    m2 = extract_features(review, model="M2", lexicon=lexicon)

    assert not any(k.startswith("lex_") for k in m0)
    assert any(k.startswith("lex_") for k in m1)
    assert any(k.startswith("shift_") for k in m2)

    print("PASS: M0, M1 and M2 feature extraction")

    socal = SOCal(lexicon)

    assert socal.score_review("The movie was excellent.") > 0
    assert socal.score_review("The movie was terrible.") < 0
    assert socal.score_review("The movie was not good.") < 0

    print("PASS: SO-CAL sentiment tests")

    print("\nAll component tests passed!")


if __name__ == "__main__":
    run_tests()
