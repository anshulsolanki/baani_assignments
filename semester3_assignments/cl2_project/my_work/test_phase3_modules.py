# Independent unit tests for Phase 3 modules:
#   1. anaphora_salience.py (Model M3)
#   2. rst_discourse.py (Model M4)
#   3. features_2.py integration for M3 and M4

from preprocess import preprocess, flatten
from lexicon_semantics import build_lexicon, apply_lexicon
from compositional_rules import apply_shifters
from anaphora_salience import (
    extract_sentence_nps,
    apply_anaphora,
    anaphora_features
)
from rst_discourse import (
    segment_sentence_edus,
    apply_rst,
    rst_features
)
from features_2 import extract_features


def test_anaphora_module(lexicon):
    print("=== Testing Module 1: Pronominal Anaphora & Entity Salience (M3) ===")

    # Test 1: Cross-sentence pronoun resolution (Neuter "it" & Masculine "his")
    text = (
        "The director adapted a classic movie. "
        "It was a masterpiece, but his screenplay was terrible."
    )
    sentences = preprocess(text)
    apply_lexicon(sentences, lexicon)
    apply_shifters(sentences)
    apply_anaphora(sentences)

    tokens = flatten(sentences)
    it_tok = [t for t in tokens if t.text.lower() == "it"][0]
    his_tok = [t for t in tokens if t.text.lower() == "his"][0]

    print(f"Resolved 'It'  -> '{it_tok.entity}'")
    print(f"Resolved 'his' -> '{his_tok.entity}'")
    assert it_tok.entity in {"movie", "classic"}
    assert his_tok.entity == "director"

    # Test 2: Feminine pronoun resolution ("she")
    text_fem = "Sarah gave a wonderful performance. She was brilliant in every scene."
    s_fem = preprocess(text_fem)
    apply_lexicon(s_fem, lexicon)
    apply_shifters(s_fem)
    apply_anaphora(s_fem)
    she_tok = [t for t in flatten(s_fem) if t.text.lower() == "she"][0]
    print(f"Resolved 'She' -> '{she_tok.entity}'")
    assert she_tok.entity == "sarah"

    # Test 3: Pleonastic "it" check ("It is obvious that...")
    text_pleo = "The film had a slow plot. It is obvious that the script needed work."
    s_pleo = preprocess(text_pleo)
    apply_anaphora(s_pleo)
    pleo_it = [t for t in s_pleo[1].tokens if t.text.lower() == "it"][0]
    print(f"Pleonastic 'It' entity (should be empty): '{pleo_it.entity}'")
    assert pleo_it.entity == ""

    # Test 4: Salient entity weight boost and M3 feature dictionary
    ana_feats = anaphora_features(sentences)
    print("M3 Anaphora Features:", ana_feats)
    assert ana_feats["ana_resolved_pronoun_density"] > 0
    assert ana_feats["ana_salient_pos_density"] > 0 or ana_feats["ana_salient_neg_density"] > 0

    print("PASS: Anaphora resolution and M3 salience tests!\n")


def test_rst_module(lexicon):
    print("=== Testing Module 2: Rule-Based RST Discourse Segmentation & Weighting (M4) ===")

    # Test 1: Concession ("Although [Satellite], [Nucleus]")
    text_conc = "Although the cinematography was excellent, the plot was predictable and terrible."
    s_conc = preprocess(text_conc)
    apply_lexicon(s_conc, lexicon)
    apply_shifters(s_conc)
    edus = segment_sentence_edus(s_conc[0])
    apply_rst(s_conc)

    print("Concession EDUs:", len(edus))
    assert len(edus) >= 2

    exc_tok = [t for t in flatten(s_conc) if t.text.lower() == "excellent"][0]
    terr_tok = [t for t in flatten(s_conc) if t.text.lower() == "terrible"][0]
    print(f"'excellent' (Satellite) weight: {exc_tok.weight}, role: {getattr(exc_tok, 'rst_role', '')}")
    print(f"'terrible'  (Nucleus)   weight: {terr_tok.weight}, role: {getattr(terr_tok, 'rst_role', '')}")
    assert exc_tok.weight < 1.0
    assert terr_tok.weight > 1.0

    # Test 2: Contrast ("[Satellite], but [Nucleus]")
    text_cont = "The trailer looked good, but the actual movie was awful."
    s_cont = preprocess(text_cont)
    apply_lexicon(s_cont, lexicon)
    apply_shifters(s_cont)
    apply_rst(s_cont)

    good_tok = [t for t in flatten(s_cont) if t.text.lower() == "good"][0]
    awful_tok = [t for t in flatten(s_cont) if t.text.lower() == "awful"][0]
    print(f"'good'  (pre-but Satellite) weight: {good_tok.weight}")
    print(f"'awful' (post-but Nucleus)  weight: {awful_tok.weight}")
    assert good_tok.weight < 1.0
    assert awful_tok.weight > 1.0

    # Test 3: Polysemy disambiguation of "while" (Temporal VBG vs Concessive clause)
    text_temp = "While watching the movie, the audience laughed."
    s_temp = preprocess(text_temp)
    edus_temp = segment_sentence_edus(s_temp[0])
    print("Temporal 'While watching' relation:", edus_temp[0]["relation"])
    assert edus_temp[0]["relation"] is None

    text_conc_while = "While the acting is great, the story fails completely."
    s_conc_while = preprocess(text_conc_while)
    edus_conc_while = segment_sentence_edus(s_conc_while[0])
    print("Concessive 'While the acting is great' relation:", edus_conc_while[0]["relation"])
    assert edus_conc_while[0]["relation"] == "Concession"

    # Test 4: M4 feature dictionary
    rst_feats = rst_features(s_conc)
    print("M4 RST Features:", rst_feats)
    assert rst_feats["rst_nucleus_neg_density"] > rst_feats["rst_satellite_pos_density"] * 0.5

    print("PASS: RST EDU segmentation, polysemy disambiguation, and M4 weighting tests!\n")


def test_full_feature_pipeline(lexicon):
    print("=== Testing Full Feature Pipeline (M0 -> M1 -> M2 -> M3 -> M4) ===")
    review = (
        "The director adapted a classic novel. "
        "Although the cinematography was excellent, it had a terrible plot and his script was not very good."
    )

    for model_name in ["M0", "M1", "M2", "M3", "M4"]:
        feats = extract_features(review, model=model_name, lexicon=lexicon)
        print(f"{model_name}: {len(feats)} total features")

        if model_name == "M3":
            assert any(k.startswith("ana_") for k in feats)
        if model_name == "M4":
            assert any(k.startswith("ana_") for k in feats)
            assert any(k.startswith("rst_") for k in feats)

    print("PASS: Full M0-M4 feature extraction pipeline works cleanly!")


if __name__ == "__main__":
    lex = build_lexicon()
    test_anaphora_module(lex)
    test_rst_module(lex)
    test_full_feature_pipeline(lex)
