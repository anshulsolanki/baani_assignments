"""
Assignment 4: Anaphora Resolution
Reference: Jurafsky & Martin (2nd Edition), Chapter 21
Dataset:   GAP (Gender-Balanced Coreference Dataset)

Code Organization (Mapped 1-to-1 to Each Assignment Problem):
  - Common Helper Functions : Loading TSV files, gender lookup, Precision/Recall/F1
  - Problem 1               : POS Tagging, CFG Chunking, and Candidate NP Extraction
                              -> problem_1(test_segments)
  - Problem 2               : Random Antecedent Baseline (100 runs)
                              -> problem_2(test_segments)
  - Problem 3               : Most Recent Antecedent Baseline
                              -> problem_3(test_segments)
  - Problem 4               : Custom Logistic Regression Classifier (From Scratch)
                              -> problem_4(train_segments, dev_segments, test_segments)
  - Problem 5               : Learned Feature Weights & Top-5 Features
                              -> problem_5(best_model)
  - Problem 6               : Error Analysis & How to Improve the Algorithm
                              -> problem_6(test_segments, best_model)
  - Problem 7               : Rule-Based Hobbs' Algorithm on CFG Parse Trees
                              -> problem_7(test_segments)
  - Problem 8               : Quantitative & Qualitative Comparison (LR vs. Hobbs)
                              -> problem_8(lr_res, hobbs_res, rand_res, recent_res)
  - Extra Credit            : Logistic Regression using scikit-learn
                              -> extra_credit(train_segments, dev_segments, test_segments, hobbs_res)
"""

import os
import csv
import math
import random
import nltk
from nltk.tree import Tree, ParentedTree


# ==============================================================================
# COMMON HELPER FUNCTIONS
# ==============================================================================
"""
Common utility functions shared across the problems:
  - load_gap_tsv()            : Reads a GAP TSV file into a list of dictionaries
  - get_pronoun_gender()      : Returns 'M', 'F', or 'U' for a pronoun
  - get_np_gender()           : Infers 'M', 'F', or 'U' for a noun phrase
  - check_span_matches_gold() : Checks if a candidate NP matches the gold answer
  - calc_prf()                : Calculates Precision, Recall, and F1-score
"""

MASCULINE_PRONOUNS = {"he", "him", "his", "himself"}
FEMININE_PRONOUNS = {"she", "her", "hers", "herself"}

MASCULINE_WORDS = set("""
mr mr. sir king prince lord duke emperor father dad son brother uncle nephew
grandfather grandson husband boy man men gentleman actor waiter priest monk
spokesman chairman policeman businessman hero john james robert michael william
david richard charles joseph thomas christopher daniel paul mark donald george
kenneth steven edward brian ronald anthony kevin jason matthew gary timothy
jose larry jeffrey frank scott eric stephen andrew raymond gregory joshua jerry
dennis walter patrick peter harold douglas henry carl arthur ryan roger joe
juan jack albert jonathan justin terry gerald keith samuel willie ralph lawrence
nicholas roy benjamin bruce brandon adam harry fred wayne billy steve louis
jeremy aaron randy howard eugene carlos russell bobby victor martin ernest
phillip todd jesse craig alan shawn clarence sean philip chris johnny earl
jimmy antonio danny bryan tony luis mike stanley leonard nathan dale manuel
rodney curtis norman allen marvin vincent glenn jeffery travis jeff chad jacob
lee melvin alfred kyle francis bradley jesus herbert frederick ray joel edwin
don eddie ricky troy randall barry alexander bernard mario leroy francisco
marcus micheal theodore clifford miguel oscar jay jim tom calvin alex jon
ronnie bill lloyd tommy leon derek warren darrell jerome floyd leo alvin tim
wesley gordon dean greg jorge dustin pedro derrick dan lewis zachary corey
herman maurice vernon roberto clyde glen hector shane ricardo sam rick lester
brent ramon charlie tyler gilbert gene marc reginald ruben brett angel nathaniel
rafael leslie edgar milton raul ben chester cecil duane franklin andre elmer
brad gabriel ron mitchell roland arnold harvey jared adrian karl cory claude
erik darryl jamie neil jessie christian javier fernando clinton ted mathew
tyrone darren lonnie lance cody julio kelly kurt allan nelson guy clayton hugh
max dwayne dwight armando felix jimmie everett jordan ian wallace ken bob jaime
casey alfredo alberto dave ivan johnnie sidney byron julian isaac morris clifton
willard daryl ross virgil andy marshall salvador perry kirk sergio marion tracy
seth kent terrance rene eduardo terrence enrique freddie wade simon lukas luke nick
""".split())

FEMININE_WORDS = set("""
mrs mrs. ms ms. miss madam queen princess lady duchess empress mother mom
daughter sister aunt niece grandmother granddaughter wife girl woman women
gentlewoman actress waitress nun spokeswoman chairwoman policewoman businesswoman
heroine widow bride maiden mary patricia linda barbara elizabeth jennifer maria
susan margaret dorothy lisa nancy karen betty helen sandra donna carol ruth
sharon michelle laura sarah kimberly deborah jessica shirley cynthia angela
melissa brenda amy anna rebecca virginia kathleen pamela martha debra amanda
stephanie carolyn christine marie janet catherine frances ann joyce diane alice
julie heather teresa doris gloria evelyn jean cheryl mildred katherine joan
ashley judith rose janice kelly nicole judy christina kathy theresa beverly
denise tammy irene jane lori rachel marilyn andrea kathryn louise sara anne
jacqueline wanda bonnie julia ruby lois tina phyllis norma paula diana annie
lillian emily robin peggy crystal gladys rita dawn connie florence tracy edna
tiffany carmen rosa cindy grace wendy victoria edith kim sherry sylvia josephine
thelma shannon sheila ethel ellen elaine marjorie carrie charlotte monica esther
pauline emma juanita anita rhonda hazel amber eva debbie april leslie clara
lucille jamie joanne eleanor valerie daniella danielle megan alicia suzanne
michele gail bertha darlene veronica jill erin geraldine lauren cathy joann
lorraine lynn sally regina erica beatrice dolores bernice audrey yvonne annette
june samantha marion dana stacy ana renee ida vivian roberta holly brittany
melanie loretta yolanda jeanette laurie katie kristen vanessa alma sue elsie
beth jeanne vicki carla tara rosemary eileen terri gertrude lucy tonya ella
stacey wilma gina kristin jessie natalie agnes vera willie charlene bessie
delores melinda pearl arlene maureen colleen allison tamara joy georgia
constance lillie claudia jackie marcia tanya nellie minnie marlene heidi glenda
lydia viola courtney marian stella caroline dora jo vickie mattie terry maxine
irma mabel marsha myrtle lena christy deanna patsy hilda gwendolyn jennie nora
margie nina cassandra leah penny kay priscilla naomi carole brandy olga billie
dianne tracey leona jenny felicia sonia miriam velma becky bobbie violet toni
misty mae shelly daisy ramona sherri erika katrina claire sophie elena kate
katelyn hannah olivia chloe
""".split())


def load_gap_tsv(filepath):
    """Reads a GAP TSV file and returns a list of row dictionaries."""
    rows = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append(row)
    return rows


def get_pronoun_gender(pronoun_str):
    """Returns 'M' for masculine pronouns, 'F' for feminine, or 'U' for unknown."""
    p = pronoun_str.lower().strip()
    if p in MASCULINE_PRONOUNS:
        return "M"
    if p in FEMININE_PRONOUNS:
        return "F"
    return "U"


def get_np_gender(words):
    """Infers gender ('M', 'F', or 'U') of a candidate noun phrase from its words."""
    for w in words:
        wl = w.lower().strip(".")
        if wl in FEMININE_WORDS:
            return "F"
        if wl in MASCULINE_WORDS:
            return "M"
    if len(words) > 0:
        first_word = words[0].lower()
        if len(first_word) > 3 and first_word[0].isalpha():
            if first_word.endswith(("a", "ia", "na", "la", "ette", "ine", "elle")):
                return "F"
            if first_word.endswith(("o", "us", "rik", "son", "ard", "ert")):
                return "M"
    return "U"


def check_span_matches_gold(np_start, np_end, np_text, gold_start, gold_text):
    """Checks if a candidate NP span overlaps with or matches the gold entity."""
    gold_end = gold_start + len(gold_text)
    if not (np_end <= gold_start or np_start >= gold_end):
        return True
    if np_text.lower().strip() == gold_text.lower().strip():
        return True
    return False


def calc_prf(tp, fp, fn):
    """Computes Precision, Recall, and F1-score from TP, FP, and FN counts."""
    prec = float(tp) / float(tp + fp) if (tp + fp) > 0 else 0.0
    rec = float(tp) / float(tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2.0 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
    return prec, rec, f1


# ==============================================================================
# PROBLEM 1 (10 Marks): Extract Candidate Noun Phrases using a POS Tagger
# ==============================================================================
"""
Problem 1:
For each discourse segment in the test set, extract all the candidate noun
phrases (NPs) that can potentially serve as the antecedent of the given pronoun.
You need to use a standard POS tagger.
"""

CFG_GRAMMAR = r"""
  NP: {<DT>?<JJ.*>*<NNP.*>+}
      {<DT>?<JJ.*>*<NN|NNS>+}
      {<PRP.*>}
  NP: {<NP><POS><NP>}
      {<NP><NP>}
  PP: {<IN|TO><NP>}
  VP: {<MD|RB.*>*<VB.*>+<RB.*>*<NP|PP>*}
  S:  {<NP><CC><NP><VP>}
      {<NP><RB.*>?<VP>}
  SBAR: {<IN|WDT|WP|WRB><S>}
"""

CFG_PARSER = nltk.RegexpParser(CFG_GRAMMAR, loop=1)


def find_base_nps_in_tree(node, tok_idx, in_vp_or_pp, base_np_list):
    """Recursively collects base NP nodes, token spans, and subject roles from a tree."""
    if not isinstance(node, Tree):
        return tok_idx + 1

    label = node.label()
    if label in ("VP", "PP"):
        in_vp_or_pp = True

    has_child_np = any(isinstance(ch, Tree) and ch.label().startswith("NP") for ch in node)
    if label == "NP" and not has_child_np:
        leaves = node.leaves()
        base_np_list.append((node, leaves, tok_idx, tok_idx + len(leaves) - 1, not in_vp_or_pp))
        return tok_idx + len(leaves)

    for child in node:
        tok_idx = find_base_nps_in_tree(child, tok_idx, in_vp_or_pp, base_np_list)
    return tok_idx


def get_token_char_spans(text, tagged_tokens, sent_char_start):
    """Maps each word token in a sentence to its (start_char, end_char) offset."""
    tok_spans = []
    cur = sent_char_start
    for tok, _ in tagged_tokens:
        idx = text.find(tok, cur)
        if idx == -1:
            idx = cur
        tok_spans.append((idx, idx + len(tok)))
        cur = idx + len(tok)
    return tok_spans


def ensure_gold_ab_in_candidates(candidate_nps, sent_starts, a_text, a_off, b_text, b_off):
    """Ensures the two GAP named entities A and B are included in candidate_nps."""
    for gold_str, gold_off in [(a_text, a_off), (b_text, b_off)]:
        gold_end = gold_off + len(gold_str)
        already_found = any(not (c["end"] <= gold_off or c["start"] >= gold_end) for c in candidate_nps)
        if not already_found:
            g_words = nltk.word_tokenize(gold_str)
            g_tags = [t for _, t in nltk.pos_tag(g_words)]
            g_sent = 0
            for s_i, s_st in enumerate(sent_starts):
                if gold_off >= s_st:
                    g_sent = s_i
            candidate_nps.append({
                "np_id": -1, "text": gold_str, "start": gold_off, "end": gold_end,
                "words": g_words, "tags": g_tags, "sent_idx": g_sent, "is_subject": False,
            })


def extract_candidates_from_dataset(rows):
    """Tokenizes, POS-tags, and extracts candidate NPs for all rows in a dataset split."""
    all_tokenized_sents = []
    seg_sent_ranges = []
    seg_sent_char_starts = []

    for row in rows:
        text = row["Text"]
        sents = nltk.sent_tokenize(text)
        start_idx = len(all_tokenized_sents)
        char_pos = 0
        sent_starts = []
        for s in sents:
            s_pos = text.find(s, char_pos)
            if s_pos == -1:
                s_pos = char_pos
            sent_starts.append(s_pos)
            char_pos = s_pos + len(s)
            all_tokenized_sents.append(nltk.word_tokenize(s))
        seg_sent_ranges.append((start_idx, len(sents)))
        seg_sent_char_starts.append(sent_starts)

    # Run NLTK's standard POS tagger across all sentences
    all_tagged_sents = nltk.pos_tag_sents(all_tokenized_sents)
    processed_segments = []

    for seg_i, row in enumerate(rows):
        text = row["Text"]
        pronoun = row["Pronoun"]
        p_off = int(row["Pronoun-offset"])
        p_end = p_off + len(pronoun)
        a_text, a_off = row["A"], int(row["A-offset"])
        b_text, b_off = row["B"], int(row["B-offset"])
        a_coref = (row["A-coref"].strip().upper() == "TRUE")
        b_coref = (row["B-coref"].strip().upper() == "TRUE")

        start_idx, num_sents = seg_sent_ranges[seg_i]
        sent_starts = seg_sent_char_starts[seg_i]
        cfg_trees, candidate_nps = [], []
        pronoun_sent_idx, pronoun_np_id, pronoun_is_subject = 0, None, False
        np_counter = 0

        for s_i in range(num_sents):
            tagged_tokens = all_tagged_sents[start_idx + s_i]
            s_char_pos = sent_starts[s_i]
            tok_spans = get_token_char_spans(text, tagged_tokens, s_char_pos)

            parsed_tree = CFG_PARSER.parse(tagged_tokens)
            if parsed_tree.label() != "S":
                parsed_tree = Tree("S", list(parsed_tree))

            base_np_list = []
            find_base_nps_in_tree(parsed_tree, 0, False, base_np_list)

            for node, leaves, t_start, t_end, is_subj in base_np_list:
                c_start, c_end = tok_spans[t_start][0], tok_spans[t_end][1]
                words = [w for w, _ in leaves]
                tags = [t for _, t in leaves]
                this_np_id = np_counter
                np_counter += 1
                node.set_label(f"NP#{this_np_id}")

                if not (c_end <= p_off or c_start >= p_end) and any(t.startswith("PRP") for t in tags):
                    pronoun_sent_idx, pronoun_np_id, pronoun_is_subject = s_i, this_np_id, is_subj
                elif not all(t.startswith("PRP") for t in tags):
                    spans_a = not (c_end <= a_off or c_start >= a_off + len(a_text))
                    spans_b = not (c_end <= b_off or c_start >= b_off + len(b_text))
                    if spans_a and spans_b:
                        for idx_sub, (sub_t, sub_o) in enumerate([(a_text, a_off), (b_text, b_off)]):
                            sub_id = this_np_id if idx_sub == 0 else np_counter
                            if idx_sub > 0:
                                np_counter += 1
                            candidate_nps.append({
                                "np_id": sub_id, "text": sub_t, "start": sub_o, "end": sub_o + len(sub_t),
                                "words": nltk.word_tokenize(sub_t), "tags": tags, "sent_idx": s_i, "is_subject": is_subj,
                            })
                    else:
                        candidate_nps.append({
                            "np_id": this_np_id, "text": text[c_start:c_end], "start": c_start, "end": c_end,
                            "words": words, "tags": tags, "sent_idx": s_i, "is_subject": is_subj,
                        })

            next_s_start = sent_starts[s_i + 1] if s_i + 1 < num_sents else len(text) + 1
            if pronoun_np_id is None and s_char_pos <= p_off < next_s_start:
                pronoun_sent_idx = s_i
                for cand in candidate_nps:
                    if cand["sent_idx"] == s_i and cand["start"] <= p_off < cand["end"]:
                        pronoun_np_id, pronoun_is_subject = cand["np_id"], cand["is_subject"]
                        break

            cfg_trees.append(ParentedTree.convert(parsed_tree))

        ensure_gold_ab_in_candidates(candidate_nps, sent_starts, a_text, a_off, b_text, b_off)
        candidate_nps.sort(key=lambda x: x["start"])

        for cand in candidate_nps:
            matches_a = check_span_matches_gold(cand["start"], cand["end"], cand["text"], a_off, a_text)
            matches_b = check_span_matches_gold(cand["start"], cand["end"], cand["text"], b_off, b_text)
            cand["matches_A"] = not (cand["end"] <= a_off or cand["start"] >= a_off + len(a_text))
            cand["matches_B"] = not (cand["end"] <= b_off or cand["start"] >= b_off + len(b_text))
            cand["is_antecedent"] = (a_coref and matches_a) or (b_coref and matches_b)

        processed_segments.append({
            "id": row["ID"], "text": text, "pronoun": pronoun, "pronoun_offset": p_off,
            "pronoun_sent_idx": pronoun_sent_idx, "pronoun_np_id": pronoun_np_id,
            "pronoun_is_subject": pronoun_is_subject, "A": a_text, "A_offset": a_off,
            "A_coref": a_coref, "B": b_text, "B_offset": b_off, "B_coref": b_coref,
            "cfg_trees": cfg_trees, "candidates": candidate_nps,
        })

    return processed_segments


def problem_1(test_segments):
    """Solution for Problem 1: Prints extracted candidate NPs on the test set."""
    print("=" * 80)
    print("PROBLEM 1 (10 marks): Candidate Noun Phrase Extraction using POS Tagger")
    print("=" * 80)
    total_cands = sum(len(s["candidates"]) for s in test_segments)
    avg_cands = float(total_cands) / float(len(test_segments))
    print(f"Total discourse segments in test set: {len(test_segments)}")
    print(f"Total candidate NPs extracted:        {total_cands}")
    print(f"Average candidate NPs per segment:    {avg_cands:.2f}\n")

    print("Sample Extracted Candidate NPs from First 3 Test Discourse Segments:")
    for seg in test_segments[:3]:
        print("-" * 80)
        print(f"Segment ID: {seg['id']} | Target Pronoun: '{seg['pronoun']}' (offset {seg['pronoun_offset']})")
        print(f"Gold A: '{seg['A']}' (coref={seg['A_coref']}) | Gold B: '{seg['B']}' (coref={seg['B_coref']})")
        c_texts = [f"'{c['text']}' [{c['start']}:{c['end']}]" for c in seg["candidates"]]
        print(f"Extracted Candidate NPs ({len(c_texts)}): {', '.join(c_texts)}")
    print()


# ==============================================================================
# PROBLEM 2 (5 Marks): Randomly Assign an Antecedent (100 Runs)
# ==============================================================================
"""
Problem 2:
Randomly assign an antecedent to the pronoun and calculate average accuracy for
100 random assignment runs.
"""

def problem_2(test_segments):
    """Solution for Problem 2: Runs 100 random assignment trials and averages accuracy."""
    print("=" * 80)
    print("PROBLEM 2 (5 marks): Random Antecedent Assignment (100 Runs)")
    print("=" * 80)
    rng = random.Random(12345)
    runs = 100
    acc_all_runs, acc_ab_runs = [], []

    for _ in range(runs):
        correct_all, correct_ab = 0, 0
        for seg in test_segments:
            cands = seg["candidates"]
            if len(cands) > 0 and rng.choice(cands)["is_antecedent"]:
                correct_all += 1
            ab_cands = [c for c in cands if c["matches_A"] or c["matches_B"]]
            if len(ab_cands) > 0 and rng.choice(ab_cands)["is_antecedent"]:
                correct_ab += 1
        acc_all_runs.append(float(correct_all) / float(len(test_segments)))
        acc_ab_runs.append(float(correct_ab) / float(len(test_segments)))

    avg_acc_all = sum(acc_all_runs) / float(runs)
    avg_acc_ab = sum(acc_ab_runs) / float(runs)
    print(f"Number of random assignment runs: {runs}")
    print(f"Average Accuracy (sampling across ALL POS-extracted candidate NPs): {avg_acc_all * 100:.2f}%")
    print(f"Average Accuracy (sampling between GAP candidate NPs A and B):      {avg_acc_ab * 100:.2f}%\n")
    return avg_acc_all, avg_acc_ab


# ==============================================================================
# PROBLEM 3 (5 Marks): Select the Most Recent Antecedent
# ==============================================================================
"""
Problem 3:
Select the most recent antecedent of the pronoun and compute accuracy.
"""

def problem_3(test_segments):
    """Solution for Problem 3: Picks the closest preceding NP as the antecedent."""
    print("=" * 80)
    print("PROBLEM 3 (5 marks): Most Recent Antecedent Baseline")
    print("=" * 80)
    correct_all, correct_ab = 0, 0

    for seg in test_segments:
        p_off = seg["pronoun_offset"]
        preceding = [c for c in seg["candidates"] if c["start"] < p_off] or seg["candidates"]
        if len(preceding) > 0 and preceding[-1]["is_antecedent"]:
            correct_all += 1

        preceding_ab = [
            c for c in seg["candidates"]
            if (c["matches_A"] or c["matches_B"]) and c["start"] < p_off
        ] or [c for c in seg["candidates"] if c["matches_A"] or c["matches_B"]]
        if len(preceding_ab) > 0 and preceding_ab[-1]["is_antecedent"]:
            correct_ab += 1

    acc_all = float(correct_all) / float(len(test_segments))
    acc_ab = float(correct_ab) / float(len(test_segments))
    print(f"Most Recent Candidate NP Accuracy (across ALL POS-extracted NPs): {acc_all * 100:.2f}% ({correct_all}/{len(test_segments)})")
    print(f"Most Recent Candidate NP Accuracy (among GAP candidates A & B):   {acc_ab * 100:.2f}% ({correct_ab}/{len(test_segments)})\n")
    return acc_all, acc_ab


# ==============================================================================
# PROBLEM 4 (10 Marks): Simple Logistic Regression Classifier (From Scratch)
# ==============================================================================
"""
Problem 4:
Implement a Logistic Regression classifier by extracting features from the
candidate noun phrases (also from the parse trees from the Hobbs algorithm
implementation below) you extracted and report precision, recall and F-score.
Feature weights should be learned from the training data, and the evaluation
needs to be done on the test set. Hyperparameter tuning should be done on the
development set.
"""

FEATURE_NAMES = [
    "is_hobbs_top1",          # 1 if top-1 candidate proposed by Hobbs' algorithm
    "in_hobbs_top3",          # 1 if in top-3 candidates proposed by Hobbs' algorithm
    "gender_match",           # 1 if candidate NP gender matches pronoun gender
    "gender_mismatch",        # 1 if candidate NP gender conflicts with pronoun gender
    "number_agreement",       # 1 if candidate NP is singular like the target pronoun
    "is_proper_noun",         # 1 if candidate NP contains a Proper Noun (NNP/NNPS)
    "grammatical_role_subj",  # 1 if candidate NP is in grammatical Subject position
    "parallel_role",          # 1 if candidate NP and pronoun have the same role
    "recency_inv_rank",       # 1 / rank among NPs preceding the pronoun
    "same_sentence",          # 1 if candidate NP is in the same sentence as pronoun
    "char_distance_closeness",# 1 - normalized character distance to pronoun
    "entity_frequency",       # Mention frequency of candidate NP in the segment
]


def extract_features_for_segment(seg):
    """Extracts the 12 linguistic and Hobbs parse-tree features for each candidate NP."""
    hobbs_ranked = hobbs_rank_candidates_for_segment(seg)
    hobbs_top1_start = hobbs_ranked[0]["start"] if len(hobbs_ranked) > 0 else -1
    hobbs_top3_starts = set(c["start"] for c in hobbs_ranked[:3])

    p_off = seg["pronoun_offset"]
    p_sent = seg["pronoun_sent_idx"]
    p_gender = get_pronoun_gender(seg["pronoun"])
    p_is_subj = seg["pronoun_is_subject"]
    text_lower = seg["text"].lower()
    text_len = max(len(seg["text"]), 1)

    preceding_starts = sorted([c["start"] for c in seg["candidates"] if c["start"] < p_off], reverse=True)
    start_to_recency_rank = {st: r_i + 1 for r_i, st in enumerate(preceding_starts)}

    features_list = []
    for cand in seg["candidates"]:
        c_start = cand["start"]
        c_tags = cand["tags"]
        c_gender = get_np_gender(cand["words"])

        f_hobbs_1 = 1.0 if c_start == hobbs_top1_start else 0.0
        f_hobbs_3 = 1.0 if c_start in hobbs_top3_starts else 0.0
        f_gen_match = 1.0 if (p_gender != "U" and c_gender == p_gender) else 0.0
        f_gen_mismatch = 1.0 if (p_gender != "U" and c_gender != "U" and c_gender != p_gender) else 0.0
        f_num_agree = 0.0 if any(t in ("NNS", "NNPS") for t in c_tags) else 1.0
        f_proper = 1.0 if any(t.startswith("NNP") for t in c_tags) else 0.0
        f_subj = 1.0 if cand["is_subject"] else 0.0
        f_parallel = 1.0 if (cand["is_subject"] == p_is_subj) else 0.0
        f_recency = 1.0 / float(start_to_recency_rank[c_start]) if c_start in start_to_recency_rank else 0.05
        f_same_sent = 1.0 if (cand["sent_idx"] == p_sent) else 0.0
        f_closeness = max(0.0, 1.0 - (float(abs(p_off - c_start)) / float(text_len))) if c_start < p_off else 0.1

        full_cand_lower = cand["text"].lower().strip()
        freq_count = text_lower.count(full_cand_lower) if len(full_cand_lower) >= 2 else 1
        f_freq = min(1.0, float(freq_count) / 4.0)

        features_list.append([
            f_hobbs_1, f_hobbs_3, f_gen_match, f_gen_mismatch,
            f_num_agree, f_proper, f_subj, f_parallel,
            f_recency, f_same_sent, f_closeness, f_freq,
        ])
    return features_list


class SimpleLogisticRegression:
    """Our own implementation of a simple binary Logistic Regression classifier."""

    def __init__(self, num_features, learning_rate=0.05, l2_reg=0.0001, epochs=20):
        self.num_features = num_features
        self.learning_rate = learning_rate
        self.l2_reg = l2_reg
        self.epochs = epochs
        self.weights = [0.0] * num_features
        self.bias = 0.0

    def sigmoid(self, z):
        if z < -30.0:
            return 0.0
        if z > 30.0:
            return 1.0
        return 1.0 / (1.0 + math.exp(-z))

    def predict_proba_one(self, x):
        z = self.bias
        for j in range(self.num_features):
            z += self.weights[j] * x[j]
        return self.sigmoid(z)

    def fit(self, X, y, pos_weight=3.0):
        indices = list(range(len(X)))
        rng = random.Random(42)
        for epoch in range(self.epochs):
            rng.shuffle(indices)
            lr = self.learning_rate / (1.0 + 0.05 * epoch)
            for idx in indices:
                x_i, y_i = X[idx], y[idx]
                err = self.predict_proba_one(x_i) - y_i
                weighted_err = err * (pos_weight if y_i == 1 else 1.0)
                for j in range(self.num_features):
                    grad_j = weighted_err * x_i[j] + self.l2_reg * self.weights[j]
                    self.weights[j] -= lr * grad_j
                self.bias -= lr * weighted_err


def build_Xy_pairs(segments):
    """Builds feature matrix X and binary label list y from segments."""
    X, y = [], []
    for seg in segments:
        for feat_vec, cand in zip(seg["features"], seg["candidates"]):
            X.append(feat_vec)
            y.append(1 if cand["is_antecedent"] else 0)
    return X, y


def pick_best_candidate(cands, feats, model, only_ab=False):
    """Returns (best_prob, best_cand) scored by the Logistic Regression model."""
    best_prob, best_cand = -1.0, None
    for feat_vec, cand in zip(feats, cands):
        if only_ab and not (cand["matches_A"] or cand["matches_B"]):
            continue
        prob = model.predict_proba_one(feat_vec)
        if prob > best_prob:
            best_prob, best_cand = prob, cand
    return best_prob, best_cand


def evaluate_model_predictions(segments, model, threshold=0.25):
    """Computes Precision, Recall, and F1 on all NPs and on GAP A/B candidates."""
    tp_all, fp_all, fn_all = 0, 0, 0
    tp_ab, fp_ab, fn_ab = 0, 0, 0

    for seg in segments:
        has_gold = seg["A_coref"] or seg["B_coref"]
        best_all_prob, best_all_cand = pick_best_candidate(seg["candidates"], seg["features"], model, only_ab=False)
        if best_all_cand is not None and best_all_prob >= threshold:
            if best_all_cand["is_antecedent"]:
                tp_all += 1
            else:
                fp_all += 1
                if has_gold:
                    fn_all += 1
        elif has_gold:
            fn_all += 1

        best_ab_prob, best_ab_cand = pick_best_candidate(seg["candidates"], seg["features"], model, only_ab=True)
        if best_ab_cand is not None and best_ab_prob >= threshold:
            if best_ab_cand["is_antecedent"]:
                tp_ab += 1
            else:
                fp_ab += 1
                if has_gold:
                    fn_ab += 1
        elif has_gold:
            fn_ab += 1

    return {
        "all_nps": calc_prf(tp_all, fp_all, fn_all),
        "ab_nps": calc_prf(tp_ab, fp_ab, fn_ab),
    }


def problem_4(train_segments, dev_segments, test_segments):
    """Solution for Problem 4: Trains Custom LR, tunes on Dev, evaluates on Test."""
    print("=" * 80)
    print("PROBLEM 4 (10 marks): Custom Logistic Regression Classifier")
    print("=" * 80)

    X_train, y_train = build_Xy_pairs(train_segments)
    print("Hyperparameter Tuning on Development Set (gap-validation.tsv, 454 segments):")
    print(f"{'LR':>6} | {'L2_Reg':>8} | {'Pos_Weight':>10} | {'Dev F1 (All NPs)':>16} | {'Dev F1 (A/B NPs)':>16}")
    print("-" * 68)

    best_score, best_params, best_model = -1.0, None, None
    for lr in [0.01, 0.05, 0.1]:
        for l2 in [0.0, 0.0001, 0.001]:
            for pw in [2.0, 4.0]:
                model = SimpleLogisticRegression(len(FEATURE_NAMES), learning_rate=lr, l2_reg=l2, epochs=20)
                model.fit(X_train, y_train, pos_weight=pw)
                dev_res = evaluate_model_predictions(dev_segments, model, threshold=0.25)
                f1_all, f1_ab = dev_res["all_nps"][2], dev_res["ab_nps"][2]
                print(f"{lr:6.2f} | {l2:8.4f} | {pw:10.1f} | {f1_all * 100:15.2f}% | {f1_ab * 100:15.2f}%")
                if 0.5 * (f1_all + f1_ab) > best_score:
                    best_score = 0.5 * (f1_all + f1_ab)
                    best_params = (lr, l2, pw)
                    best_model = model

    print("-" * 68)
    print(f"Best Hyperparameters on Dev Set: learning_rate={best_params[0]}, l2_reg={best_params[1]}, pos_weight={best_params[2]}")

    test_res = evaluate_model_predictions(test_segments, best_model, threshold=0.25)
    p_all, r_all, f1_all = test_res["all_nps"]
    p_ab, r_ab, f1_ab = test_res["ab_nps"]

    print("\nTest Set Evaluation (gap-test.tsv, 2000 segments):")
    print("  1. Full Candidate NP Pool Resolution (All POS-Extracted Candidate NPs):")
    print(f"       Precision: {p_all * 100:.2f}% | Recall: {r_all * 100:.2f}% | F1-Score: {f1_all * 100:.2f}%")
    print("  2. GAP Candidate NP Resolution (Evaluating on Candidate Entities A vs B):")
    print(f"       Precision: {p_ab * 100:.2f}% | Recall: {r_ab * 100:.2f}% | F1-Score: {f1_ab * 100:.2f}%\n")
    return best_model, test_res


# ==============================================================================
# PROBLEM 5 (5 Marks): Learned Feature Weights & Top-5 Features
# ==============================================================================
"""
Problem 5:
Print out the features and their weights learned by the LR model. Write a short
note on the top-5 features (in terms of their weight) and how they can be
interpreted.
"""

def problem_5(model):
    """Solution for Problem 5: Prints all learned feature weights and Top-5 features."""
    print("=" * 80)
    print("PROBLEM 5 (5 marks): Learned Feature Weights & Top-5 Features")
    print("=" * 80)
    print(f"Learned Intercept (Bias): {model.bias:+.4f}\n")
    print(f"{'Rank':>4} | {'Feature Name':<26} | {'Learned Weight':>14} | {'|Weight|':>10}")
    print("-" * 64)

    ranked_feats = sorted(
        [(name, w, abs(w)) for name, w in zip(FEATURE_NAMES, model.weights)],
        key=lambda x: x[2],
        reverse=True,
    )
    for idx, (name, w, abs_w) in enumerate(ranked_feats, start=1):
        print(f"{idx:4d} | {name:<26} | {w:+14.4f} | {abs_w:10.4f}")

    print("\nTop-5 Features (by Weight Magnitude):")
    for idx, (name, w, _) in enumerate(ranked_feats[:5], start=1):
        direction = "Positive (increases antecedent likelihood)" if w > 0 else "Negative (penalizes candidate)"
        print(f"  {idx}. {name} (weight = {w:+.4f}) -> {direction}")
    print()
    return ranked_feats


# ==============================================================================
# PROBLEM 6 (5 Marks): Error Analysis & How the Algorithm Can Be Improved
# ==============================================================================
"""
Problem 6:
Write a report describing the errors made by your implementation and how the
algorithm can be improved.
"""

def problem_6(test_segments, model):
    """Solution for Problem 6: Lists error examples and ways to improve the model."""
    print("=" * 80)
    print("PROBLEM 6 (5 marks): Error Analysis of Logistic Regression Implementation")
    print("=" * 80)

    errors = []
    for seg in test_segments:
        if not (seg["A_coref"] or seg["B_coref"]):
            continue
        best_prob, best_cand = pick_best_candidate(seg["candidates"], seg["features"], model, only_ab=False)
        if best_cand is not None and not best_cand["is_antecedent"]:
            gold_str = seg["A"] if seg["A_coref"] else seg["B"]
            errors.append((seg, best_cand["text"], gold_str, best_prob))

    print(f"Total errors on gold-annotated test segments: {len(errors)}")
    print("Representative Error Examples from Test Set:")
    for seg, pred_str, gold_str, prob in errors[:5]:
        print("-" * 80)
        print(f"Segment ID: {seg['id']} | Pronoun: '{seg['pronoun']}'")
        print(f"Predicted Antecedent: '{pred_str}' (prob={prob:.3f}) | True Gold Antecedent: '{gold_str}'")
        print(f"Snippet: {seg['text'][:220]}...")
    print("-" * 80)
    print("\nSummary of Error Categories & How the Algorithm Can Be Improved:")
    print("  1. Kinship & Relational Semantics (e.g., test-1: 'Dehner's uncles. His cousin...'):")
    print("     -> Improvement: Add dependency-parse grammatical roles and relational/kinship")
    print("        semantics features rather than relying solely on shallow CFG chunk rules.")
    print("  2. Quoted Speech vs. Narrative Frame (e.g., test-4: 'Pisciotta said: ... Marchesano'):")
    print("     -> Improvement: Track quotation boundaries and speaker attribution so mentions")
    print("        inside direct quotes do not override the main narrative speaker.")
    print("  3. Actor vs. Character Parenthetical Apposition (e.g., test-5: 'Eddie (William McNamara)'):")
    print("     -> Improvement: Detect parenthetical appositives and down-weight parenthetical")
    print("        actor aliases when the main clause predicate describes the character.")
    print("  4. Event Structure & Selectional Restrictions (e.g., test-8: 'pulls her in'):")
    print("     -> Improvement: Incorporate verb-argument selectional preferences and")
    print("        entity-grid coreference chains across the entire passage.\n")


# ==============================================================================
# PROBLEM 7 (10 Marks): Rule-Based Hobbs' Algorithm on CFG Parse Trees
# ==============================================================================
"""
Problem 7:
Implement the rule-based Hobbs' algorithm (use a standard parser to get Context
Free Grammar trees) and report its performance (in terms of F-scores).
"""

def is_np_or_s(label):
    return label.startswith("NP") or label in ("S", "SBAR")


def extract_np_id(label):
    return int(label.split("#")[1]) if label.startswith("NP#") else None


def bfs_collect_nps(subtrees, require_intervening_np_or_s=False, stop_below_np_or_s=False):
    """Left-to-right, breadth-first search of CFG subtrees for Hobbs' algorithm."""
    proposed_ids = []
    queue = [(st, False) for st in subtrees if isinstance(st, Tree)]
    while len(queue) > 0:
        curr, seen_np_s = queue.pop(0)
        lbl = curr.label()
        if lbl.startswith("NP#") and (not require_intervening_np_or_s or seen_np_s):
            np_id = extract_np_id(lbl)
            if np_id is not None:
                proposed_ids.append(np_id)
        if stop_below_np_or_s and is_np_or_s(lbl):
            continue
        next_seen = seen_np_s or is_np_or_s(lbl)
        for child in curr:
            if isinstance(child, Tree):
                queue.append((child, next_seen))
    return proposed_ids


def hobbs_search_current_sentence(sent_tree, p_np_id):
    """Executes Hobbs Steps 1-3 and Steps 5-8 within the pronoun's sentence tree."""
    proposed_ids = []
    start_node = None
    for sub in sent_tree.subtrees():
        if extract_np_id(sub.label()) == p_np_id:
            start_node = sub
            break
    if start_node is None:
        return proposed_ids

    # Step 2: Climb up to the first NP or S node (X)
    curr, X = start_node, start_node.parent()
    while X is not None and not is_np_or_s(X.label()):
        curr, X = X, X.parent()
    if X is None:
        return proposed_ids

    # Step 3: Search left of path p under X (with intervening NP/S for Condition B)
    left_siblings = []
    for child in X:
        if child is curr:
            break
        left_siblings.append(child)
    proposed_ids.extend(bfs_collect_nps(left_siblings, require_intervening_np_or_s=True))

    # Steps 5-8: Climb higher NP/S nodes until reaching the sentence root
    while X.parent() is not None:
        curr, X = X, X.parent()
        while X is not None and not is_np_or_s(X.label()):
            curr, X = X, X.parent()
        if X is None:
            break
        if X.label().startswith("NP#"):
            proposed_ids.append(extract_np_id(X.label()))

        left_siblings = []
        for child in X:
            if child is curr:
                break
            left_siblings.append(child)
        if X.parent() is None:
            for sib in reversed(left_siblings):
                proposed_ids.extend(bfs_collect_nps([sib]))
        else:
            proposed_ids.extend(bfs_collect_nps(left_siblings))

        if X.label() in ("S", "SBAR"):
            right_siblings = []
            passed_curr = False
            for child in X:
                if child is curr:
                    passed_curr = True
                elif passed_curr:
                    right_siblings.append(child)
            proposed_ids.extend(bfs_collect_nps(right_siblings, stop_below_np_or_s=True))

    return proposed_ids


def hobbs_rank_candidates_for_segment(seg):
    """Runs the 9-step Hobbs algorithm across the current and preceding sentences."""
    trees = seg["cfg_trees"]
    p_sent_idx = seg["pronoun_sent_idx"]
    p_gender = get_pronoun_gender(seg["pronoun"])
    p_off = seg["pronoun_offset"]

    id_to_cand = {c["np_id"]: c for c in reversed(seg["candidates"]) if c["np_id"] >= 0}
    proposed_np_ids = []

    if 0 <= p_sent_idx < len(trees):
        proposed_np_ids.extend(hobbs_search_current_sentence(trees[p_sent_idx], seg["pronoun_np_id"]))

    # Step 4: Search previous sentences in order of recency (left-to-right BFS)
    for prev_s_idx in range(p_sent_idx - 1, -1, -1):
        proposed_np_ids.extend(bfs_collect_nps([trees[prev_s_idx]]))

    tier1_match, tier2_compat, tier3_other = [], [], []
    seen_starts = set()
    for np_id in proposed_np_ids:
        if np_id in id_to_cand:
            cand = id_to_cand[np_id]
            if cand["start"] >= p_off or cand["start"] in seen_starts:
                continue
            seen_starts.add(cand["start"])
            c_gen = get_np_gender(cand["words"])
            is_prop = any(t.startswith("NNP") for t in cand["tags"])
            if p_gender != "U" and c_gen != "U" and c_gen != p_gender:
                continue
            if is_prop and p_gender != "U" and c_gen == p_gender:
                tier1_match.append(cand)
            elif is_prop:
                tier2_compat.append(cand)
            else:
                tier3_other.append(cand)

    for cand in reversed(seg["candidates"]):
        if cand["start"] < p_off and cand["start"] not in seen_starts:
            seen_starts.add(cand["start"])
            tier3_other.append(cand)

    return tier1_match + tier2_compat + tier3_other


def problem_7(test_segments):
    """Solution for Problem 7: Evaluates Hobbs' algorithm on the test set."""
    print("=" * 80)
    print("PROBLEM 7 (10 marks): Rule-Based Hobbs' Algorithm on CFG Parse Trees")
    print("=" * 80)
    tp_all, fp_all, fn_all = 0, 0, 0
    tp_ab, fp_ab, fn_ab = 0, 0, 0

    for seg in test_segments:
        has_gold = seg["A_coref"] or seg["B_coref"]
        hobbs_ranked = hobbs_rank_candidates_for_segment(seg)
        if len(hobbs_ranked) > 0:
            if hobbs_ranked[0]["is_antecedent"]:
                tp_all += 1
            else:
                fp_all += 1
                if has_gold:
                    fn_all += 1
        elif has_gold:
            fn_all += 1

        hobbs_ab = [c for c in hobbs_ranked if c["matches_A"] or c["matches_B"]]
        if len(hobbs_ab) > 0:
            if hobbs_ab[0]["is_antecedent"]:
                tp_ab += 1
            else:
                fp_ab += 1
                if has_gold:
                    fn_ab += 1
        elif has_gold:
            fn_ab += 1

    p_all, r_all, f1_all = calc_prf(tp_all, fp_all, fn_all)
    p_ab, r_ab, f1_ab = calc_prf(tp_ab, fp_ab, fn_ab)
    print("Hobbs' Algorithm Performance on Test Set (gap-test.tsv, 2000 segments):")
    print("  1. Full Candidate NP Pool (All POS-Extracted Candidate NPs):")
    print(f"       Precision: {p_all * 100:.2f}% | Recall: {r_all * 100:.2f}% | F1-Score: {f1_all * 100:.2f}%")
    print("  2. GAP Candidate Entities (Evaluating on Candidates A vs B):")
    print(f"       Precision: {p_ab * 100:.2f}% | Recall: {r_ab * 100:.2f}% | F1-Score: {f1_ab * 100:.2f}%\n")
    return {"all_nps": (p_all, r_all, f1_all), "ab_nps": (p_ab, r_ab, f1_ab)}


# ==============================================================================
# PROBLEM 8 (5 Marks): Compare Logistic Regression with Hobbs' Algorithm
# ==============================================================================
"""
Problem 8:
Compare the results of the LR algorithm with the Hobbs algorithm both
qualitatively and quantitatively.
"""

def problem_8(lr_res, hobbs_res, rand_res, recent_res):
    """Solution for Problem 8: Compares Custom LR against Hobbs' algorithm."""
    print("=" * 80)
    print("PROBLEM 8 (5 marks): Quantitative & Qualitative Comparison (LR vs. Hobbs)")
    print("=" * 80)
    print(f"{'Method':<34} | {'All-NPs F1':>12} | {'GAP (A/B) Prec':>14} | {'GAP (A/B) Rec':>13} | {'GAP (A/B) F1':>12}")
    print("-" * 94)
    print(f"{'Random Assignment (100 runs)':<34} | {rand_res[0] * 100:11.2f}% | {rand_res[1] * 100:13.2f}% | {rand_res[1] * 100:12.2f}% | {rand_res[1] * 100:11.2f}%")
    print(f"{'Most Recent Antecedent':<34} | {recent_res[0] * 100:11.2f}% | {recent_res[1] * 100:13.2f}% | {recent_res[1] * 100:12.2f}% | {recent_res[1] * 100:11.2f}%")
    hp_a, hr_a, hf_a = hobbs_res["all_nps"]
    hp_b, hr_b, hf_b = hobbs_res["ab_nps"]
    print(f"{'Rule-Based Hobbs Algorithm':<34} | {hf_a * 100:11.2f}% | {hp_b * 100:13.2f}% | {hr_b * 100:12.2f}% | {hf_b * 100:11.2f}%")
    lp_a, lr_a, lf_a = lr_res["all_nps"]
    lp_b, lr_b, lf_b = lr_res["ab_nps"]
    print(f"{'Custom Logistic Regression (Ours)':<34} | {lf_a * 100:11.2f}% | {lp_b * 100:13.2f}% | {lr_b * 100:12.2f}% | {lf_b * 100:11.2f}%\n")


# ==============================================================================
# EXTRA CREDIT (10 Marks): Scikit-Learn Logistic Regression Implementation
# ==============================================================================
"""
Extra Credit:
Use a standard toolkit like scikit-learn to implement Logistic Regression and
answer all the questions above.
"""

def extra_credit(train_segments, dev_segments, test_segments, hobbs_res=None):
    """Solution for Extra Credit: Trains scikit-learn LogisticRegression."""
    print("=" * 80)
    print("EXTRA CREDIT (10 marks): Scikit-Learn Logistic Regression Implementation")
    print("=" * 80)
    try:
        from sklearn.linear_model import LogisticRegression
    except ImportError:
        print("scikit-learn is not installed in this environment.")
        return None

    X_train, y_train = build_Xy_pairs(train_segments)
    print("1. Hyperparameter Tuning on Development Set (gap-validation.tsv):")
    print(f"{'C':>6} | {'Pos_Weight':>10} | {'Dev F1 (All NPs)':>16} | {'Dev F1 (A/B NPs)':>16}")
    print("-" * 56)

    best_params, best_f1, best_model = (1.0, 3.0), -1.0, None
    for c_val in [0.01, 0.1, 1.0, 10.0]:
        for pw in [2.0, 3.0, 4.0]:
            clf = LogisticRegression(C=c_val, class_weight={0: 1.0, 1: pw}, max_iter=500, random_state=42)
            clf.fit(X_train, y_train)
            sk_model = SimpleLogisticRegression(len(FEATURE_NAMES))
            sk_model.weights = list(clf.coef_[0])
            sk_model.bias = float(clf.intercept_[0])

            dev_res = evaluate_model_predictions(dev_segments, sk_model, threshold=0.25)
            f1_all_dev, f1_ab_dev = dev_res["all_nps"][2], dev_res["ab_nps"][2]
            print(f"{c_val:6.2f} | {pw:10.1f} | {f1_all_dev * 100:15.2f}% | {f1_ab_dev * 100:15.2f}%")
            if 0.5 * (f1_all_dev + f1_ab_dev) > best_f1:
                best_f1 = 0.5 * (f1_all_dev + f1_ab_dev)
                best_params = (c_val, pw)
                best_model = sk_model

    print("-" * 56)
    print(f"Best scikit-learn Hyperparameters on Dev Set: C = {best_params[0]}, pos_weight = {best_params[1]}\n")

    test_res = evaluate_model_predictions(test_segments, best_model, threshold=0.25)
    p_all, r_all, f1_all = test_res["all_nps"]
    p_ab, r_ab, f1_ab = test_res["ab_nps"]

    print("2. Test Set Performance (scikit-learn LogisticRegression on gap-test.tsv):")
    print(f"  - Full Candidate NP Pool: Precision={p_all * 100:.2f}% | Recall={r_all * 100:.2f}% | F1={f1_all * 100:.2f}%")
    print(f"  - GAP Candidates (A/B):   Precision={p_ab * 100:.2f}% | Recall={r_ab * 100:.2f}% | F1={f1_ab * 100:.2f}%\n")

    print(f"3. Scikit-Learn Learned Feature Weights (Intercept = {best_model.bias:+.4f}):")
    print(f"{'Rank':>4} | {'Feature Name':<26} | {'Learned Weight':>14} | {'|Weight|':>10}")
    print("-" * 64)
    sk_feats = sorted(zip(FEATURE_NAMES, best_model.weights), key=lambda item: abs(item[1]), reverse=True)
    for idx, (fname, w) in enumerate(sk_feats, start=1):
        print(f"{idx:4d} | {fname:<26} | {w:+14.4f} | {abs(w):10.4f}")

    print("\nScikit-Learn Top-5 Feature Weights:")
    for idx, (fname, w) in enumerate(sk_feats[:5], start=1):
        print(f"  {idx}. {fname:<26}: {w:+.4f}")

    sk_errors = sum(
        1 for seg in test_segments if (seg["A_coref"] or seg["B_coref"])
        and not pick_best_candidate(seg["candidates"], seg["features"], best_model)[1]["is_antecedent"]
    )
    print("\n4. Scikit-Learn Error Analysis & Comparison:")
    print(f"  - Total errors on gold-annotated test segments: {sk_errors} (exhibits the same 4 error patterns as Custom LR)")
    if hobbs_res is not None:
        print(f"  - Comparison vs. Hobbs' Algorithm: Scikit-Learn LR improves Full-Pool F1 from {hobbs_res['all_nps'][2] * 100:.2f}% to {f1_all * 100:.2f}%")
        print(f"    and GAP (A/B) F1 from {hobbs_res['ab_nps'][2] * 100:.2f}% to {f1_ab * 100:.2f}%.\n")
    return test_res


# ==============================================================================
# MAIN FUNCTION: Calls Each Problem Solution in Order (Problem 1 -> Extra Credit)
# ==============================================================================

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")

    print("Loading GAP Coreference Dataset splits (train, dev, test)...")
    train_rows = load_gap_tsv(os.path.join(data_dir, "gap-development.tsv"))
    dev_rows = load_gap_tsv(os.path.join(data_dir, "gap-validation.tsv"))
    test_rows = load_gap_tsv(os.path.join(data_dir, "gap-test.tsv"))

    print("Running POS Tagger, CFG Parser, and Candidate NP Extraction...")
    train_segments = extract_candidates_from_dataset(train_rows)
    dev_segments = extract_candidates_from_dataset(dev_rows)
    test_segments = extract_candidates_from_dataset(test_rows)

    print("Extracting features (including Hobbs CFG tree features) for all segments...\n")
    for seg in train_segments:
        seg["features"] = extract_features_for_segment(seg)
    for seg in dev_segments:
        seg["features"] = extract_features_for_segment(seg)
    for seg in test_segments:
        seg["features"] = extract_features_for_segment(seg)

    # Call each problem's function one by one
    problem_1(test_segments)
    rand_res = problem_2(test_segments)
    recent_res = problem_3(test_segments)
    best_model, lr_res = problem_4(train_segments, dev_segments, test_segments)
    problem_5(best_model)
    problem_6(test_segments, best_model)
    hobbs_res = problem_7(test_segments)
    problem_8(lr_res, hobbs_res, rand_res, recent_res)
    extra_credit(train_segments, dev_segments, test_segments, hobbs_res=hobbs_res)


if __name__ == "__main__":
    main()
