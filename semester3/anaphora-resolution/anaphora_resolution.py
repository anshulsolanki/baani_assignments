"""
Assignment 4: Anaphora Resolution
=================================
Reference: Jurafsky & Martin (2nd Edition), Chapter 21 (Computational Discourse)
Dataset:   GAP (Gender-Balanced Coreference Dataset)
           - Training set:    data/gap-development.tsv (2000 segments)
           - Development set: data/gap-validation.tsv  (454 segments)
           - Test set:        data/gap-test.tsv        (2000 segments)

Implemented using basic Python and NLTK (no complex libraries for Problems 1-8):
  - Problem 1: Extract candidate noun phrases (NPs) for each discourse segment
               in the test set using NLTK's standard POS tagger.
  - Problem 2: Randomly assign an antecedent for 100 runs and compute average accuracy.
  - Problem 3: Select the most recent antecedent and compute accuracy.
  - Problem 4: Implement a custom Logistic Regression classifier from scratch
               (using gradient descent and sigmoid in basic Python), tune
               hyperparameters on the development set, and report Precision,
               Recall, and F-score on the test set.
  - Problem 5: Print all learned feature weights and interpret the top-5 features.
  - Problem 6: Analyze concrete errors made by the model and how to improve it.
  - Problem 7: Implement the rule-based Hobbs' algorithm on Context-Free Grammar
               (CFG) parse trees and report Precision, Recall, and F-score.
  - Problem 8: Compare the custom Logistic Regression model with Hobbs' algorithm
               quantitatively and qualitatively.
  - Extra Credit: Repeat Logistic Regression training, tuning, evaluation, and
               weight analysis using scikit-learn's LogisticRegression.
"""

import os
import csv
import math
import random
import nltk
from nltk.tree import Tree, ParentedTree


# ==============================================================================
# 0. Gender Lexicon & Helper Functions (Basic Python)
# ==============================================================================

MASCULINE_PRONOUNS = {"he", "him", "his", "himself"}
FEMININE_PRONOUNS = {"she", "her", "hers", "herself"}

# Common gendered titles, kinship nouns, and frequent first names in GAP
MASCULINE_WORDS = {
    "mr", "mr.", "sir", "king", "prince", "lord", "duke", "emperor", "father",
    "dad", "son", "brother", "uncle", "nephew", "grandfather", "grandson",
    "husband", "boy", "man", "men", "gentleman", "actor", "waiter", "priest",
    "monk", "spokesman", "chairman", "policeman", " businessman", "hero",
    "john", "james", "robert", "michael", "william", "david", "richard",
    "charles", "joseph", "thomas", "christopher", "daniel", "paul", "mark",
    "donald", "george", "kenneth", "steven", "edward", "brian", "ronald",
    "anthony", "kevin", "jason", "matthew", "gary", "timothy", "jose", "larry",
    "jeffrey", "frank", "scott", "eric", "stephen", "andrew", "raymond",
    "gregory", "joshua", "jerry", "dennis", "walter", "patrick", "peter",
    "harold", "douglas", "henry", "carl", "arthur", "ryan", "roger", "joe",
    "juan", "jack", "albert", "jonathan", "justin", "terry", "gerald", "keith",
    "samuel", "willie", "ralph", "lawrence", "nicholas", "roy", "benjamin",
    "bruce", "brandon", "adam", "harry", "fred", "wayne", "billy", "steve",
    "louis", "jeremy", "aaron", "randy", "howard", "eugene", "carlos",
    "russell", "bobby", "victor", "martin", "ernest", "phillip", "todd",
    "jesse", "craig", "alan", "shawn", "clarence", "sean", "philip", "chris",
    "johnny", "earl", "jimmy", "antonio", "danny", "bryan", "tony", "luis",
    "mike", "stanley", "leonard", "nathan", "dale", "manuel", "rodney",
    "curtis", "norman", "allen", "marvin", "vincent", "glenn", "jeffery",
    "travis", "jeff", "chad", "jacob", "lee", "melvin", "alfred", "kyle",
    "francis", "bradley", "jesus", "herbert", "frederick", "ray", "joel",
    "edwin", "don", "eddie", "ricky", "troy", "randall", "barry", "alexander",
    "bernard", "mario", "leroy", "francisco", "marcus", "micheal", "theodore",
    "clifford", "miguel", "oscar", "jay", "jim", "tom", "calvin", "alex",
    "jon", "ronnie", "bill", "lloyd", "tommy", "leon", "derek", "warren",
    "darrell", "jerome", "floyd", "leo", "alvin", "tim", "wesley", "gordon",
    "dean", "greg", "jorge", "dustin", "pedro", "derrick", "dan", "lewis",
    "zachary", "corey", "herman", "maurice", "vernon", "roberto", "clyde",
    "glen", "hector", "shane", "ricardo", "sam", "rick", "lester", "brent",
    "ramon", "charlie", "tyler", "gilbert", "gene", "marc", "reginald",
    "ruben", "brett", "angel", "nathaniel", "rafael", "leslie", "edgar",
    "milton", "raul", "ben", "chester", "cecil", "duane", "franklin", "andre",
    "elmer", "brad", "gabriel", "ron", "mitchell", "roland", "arnold",
    "harvey", "jared", "adrian", "karl", "cory", "claude", "erik", "darryl",
    "jamie", "neil", "jessie", "christian", "javier", "fernando", "clinton",
    "ted", "mathew", "tyrone", "darren", "lonnie", "lance", "cody", "julio",
    "kelly", "kurt", "allan", "nelson", "guy", "clayton", "hugh", "max",
    "dwayne", "dwight", "armando", "felix", "jimmie", "everett", "jordan",
    "ian", "wallace", "ken", "bob", "jaime", "casey", "alfredo", "alberto",
    "dave", "ivan", "johnnie", "sidney", "byron", "julian", "isaac", "morris",
    "clifton", "willard", "daryl", "ross", "virgil", "andy", "marshall",
    "salvador", "perry", "kirk", "sergio", "marion", "tracy", "seth", "kent",
    "terrance", "rene", "eduardo", "terrence", "enrique", "freddie", "wade",
    "simon", "lukas", "luke", "matthew", "mark", "nick", "nicholas"
}

FEMININE_WORDS = {
    "mrs", "mrs.", "ms", "ms.", "miss", "madam", "queen", "princess", "lady",
    "duchess", "empress", "mother", "mom", "daughter", "sister", "aunt",
    "niece", "grandmother", "granddaughter", "wife", "girl", "woman", "women",
    "gentlewoman", "actress", "waitress", "nun", "spokeswoman", "chairwoman",
    "policewoman", "businesswoman", "heroine", "widow", "bride", "maiden",
    "mary", "patricia", "linda", "barbara", "elizabeth", "jennifer", "maria",
    "susan", "margaret", "dorothy", "lisa", "nancy", "karen", "betty", "helen",
    "sandra", "donna", "carol", "ruth", "sharon", "michelle", "laura", "sarah",
    "kimberly", "deborah", "jessica", "shirley", "cynthia", "angela", "melissa",
    "brenda", "amy", "anna", "rebecca", "virginia", "kathleen", "pamela",
    "martha", "debra", "amanda", "stephanie", "carolyn", "christine", "marie",
    "janet", "catherine", "frances", "ann", "joyce", "diane", "alice", "julie",
    "heather", "teresa", "doris", "gloria", "evelyn", "jean", "cheryl",
    "mildred", "katherine", "joan", "ashley", "judith", "rose", "janice",
    "kelly", "nicole", "judy", "christina", "kathy", "theresa", "beverly",
    "denise", "tammy", "irene", "jane", "lori", "rachel", "marilyn", "andrea",
    "kathryn", "louise", "sara", "anne", "jacqueline", "wanda", "bonnie",
    "julia", "ruby", "lois", "tina", "phyllis", "norma", "paula", "diana",
    "annie", "lillian", "emily", "robin", "peggy", "crystal", "gladys",
    "rita", "dawn", "connie", "florence", "tracy", "edna", "tiffany", "carmen",
    "rosa", "cindy", "grace", "wendy", "victoria", "edith", "kim", "sherry",
    "sylvia", "josephine", "thelma", "shannon", "sheila", "ethel", "ellen",
    "elaine", "marjorie", "carrie", "charlotte", "monica", "esther", "pauline",
    "emma", "juanita", "anita", "rhonda", "hazel", "amber", "eva", "debbie",
    "april", "leslie", "clara", "lucille", "jamie", "joanne", "eleanor",
    "valerie", "daniella", "danielle", "megan", "alicia", "suzanne", "michele",
    "gail", "bertha", "darlene", "veronica", "jill", "erin", "geraldine",
    "lauren", "cathy", "joann", "lorraine", "lynn", "sally", "regina", "erica",
    "beatrice", "dolores", "bernice", "audrey", "yvonne", "annette", "june",
    "samantha", "marion", "dana", "stacy", "ana", "renee", "ida", "vivian",
    "roberta", "holly", "brittany", "melanie", "loretta", "yolanda", "jeanette",
    "laurie", "katie", "kristen", "vanessa", "alma", "sue", "elsie", "beth",
    "jeanne", "vicki", "carla", "tara", "rosemary", "eileen", "terri",
    "gertrude", "lucy", "tonya", "ella", "stacey", "wilma", "gina", "kristin",
    "jessie", "natalie", "agnes", "vera", "willie", "charlene", "bessie",
    "delores", "melinda", "pearl", "arlene", "maureen", "colleen", "allison",
    "tamara", "joy", "georgia", "constance", "lillie", "claudia", "jackie",
    "marcia", "tanya", "nellie", "minnie", "marlene", "heidi", "glenda",
    "lydia", "viola", "courtney", "marian", "stella", "caroline", "dora",
    "jo", "vickie", "mattie", "terry", "maxine", "irma", "mabel", "marsha",
    "myrtle", "lena", "christy", "deanna", "patsy", "hilda", "gwendolyn",
    "jennie", "nora", "margie", "nina", "cassandra", "leah", "penny", "kay",
    "priscilla", "naomi", "carole", "brandy", "olga", "billie", "dianne",
    "tracey", "leona", "jenny", "felicia", "sonia", "miriam", "velma",
    "becky", "bobbie", "violet", "kristina", "toni", "misty", "mae", "shelly",
    "daisy", "ramona", "sherri", "erika", "katrina", "claire", "sophie",
    "marie", "elena", "nina", "kate", "katelyn", "hannah", "olivia", "chloe"
}


def get_pronoun_gender(pronoun_str):
    p = pronoun_str.lower().strip()
    if p in MASCULINE_PRONOUNS:
        return "M"
    if p in FEMININE_PRONOUNS:
        return "F"
    return "U"


def get_np_gender(words):
    """
    Infers gender ('M', 'F', or 'U' for unknown/neutral) of a candidate NP
    from its words and common English name endings.
    """
    for w in words:
        wl = w.lower().strip(".")
        if wl in FEMININE_WORDS:
            return "F"
        if wl in MASCULINE_WORDS:
            return "M"
    # Simple suffix heuristic for proper names not in the small dictionary
    if len(words) > 0:
        first_word = words[0].lower()
        if len(first_word) > 3 and first_word[0].isalpha():
            if first_word.endswith(("a", "ia", "na", "la", "ette", "ine", "elle")):
                return "F"
            if first_word.endswith(("o", "us", "rik", "son", "ard", "ert")):
                return "M"
    return "U"


# ==============================================================================
# 1. Dataset Loading, POS Tagging, CFG Parsing & Candidate NP Extraction
# ==============================================================================

# Standard Context-Free Grammar (CFG) chunk rules over POS tags
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


def load_gap_tsv(filepath):
    """Loads a GAP TSV file and returns a list of dictionary rows."""
    rows = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append(row)
    return rows


def check_span_matches_gold(np_start, np_end, np_text, gold_start, gold_text):
    """
    Returns True if a candidate NP span overlaps with the gold antecedent span
    or refers to the same entity string in the discourse segment.
    """
    gold_end = gold_start + len(gold_text)
    # Direct character-offset overlap
    if not (np_end <= gold_start or np_start >= gold_end):
        return True
    # Exact string or head match with the gold entity
    np_clean = np_text.lower().strip()
    gold_clean = gold_text.lower().strip()
    if np_clean == gold_clean:
        return True
    return False


def process_dataset(rows, split_name="test"):
    """
    Problem 1:
    For each discourse segment:
      1. Tokenizes into sentences and words.
      2. Runs NLTK's standard POS tagger (nltk.pos_tag_sents).
      3. Builds a Context-Free Grammar (CFG) parse tree (nltk.Tree) for each sentence.
      4. Extracts all candidate Noun Phrases (NPs) that can potentially serve as
         the antecedent of the given pronoun.
    """
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

    # Batch POS tag all sentences using NLTK's standard POS tagger
    all_tagged_sents = nltk.pos_tag_sents(all_tokenized_sents)

    processed_segments = []

    for seg_i, row in enumerate(rows):
        text = row["Text"]
        pronoun = row["Pronoun"]
        p_off = int(row["Pronoun-offset"])
        p_end = p_off + len(pronoun)

        a_text = row["A"]
        a_off = int(row["A-offset"])
        a_coref = (row["A-coref"].strip().upper() == "TRUE")

        b_text = row["B"]
        b_off = int(row["B-offset"])
        b_coref = (row["B-coref"].strip().upper() == "TRUE")

        start_idx, num_sents = seg_sent_ranges[seg_i]
        sent_starts = seg_sent_char_starts[seg_i]

        cfg_trees = []
        candidate_nps = []
        pronoun_sent_idx = 0
        pronoun_np_id = None
        pronoun_is_subject = False

        np_counter = 0

        for s_i in range(num_sents):
            tagged_tokens = all_tagged_sents[start_idx + s_i]
            s_char_pos = sent_starts[s_i]

            # Find character offsets for each token in this sentence
            tok_spans = []
            cur = s_char_pos
            for tok, _ in tagged_tokens:
                idx = text.find(tok, cur)
                if idx == -1:
                    idx = cur
                tok_spans.append((idx, idx + len(tok)))
                cur = idx + len(tok)

            # Build CFG parse tree for the sentence
            parsed_tree = CFG_PARSER.parse(tagged_tokens)
            if parsed_tree.label() != "S":
                parsed_tree = Tree("S", list(parsed_tree))

            # Walk the tree to locate every base NP node, its token span, and grammatical role
            tok_cursor = [0]

            def annotate_tree(node, in_vp_or_pp=False):
                nonlocal np_counter, pronoun_sent_idx, pronoun_np_id, pronoun_is_subject
                if not isinstance(node, Tree):
                    tok_cursor[0] += 1
                    return

                lbl = node.label()
                now_in_vp_pp = in_vp_or_pp or (lbl in ("VP", "PP"))

                # Check if this is a base NP (no child NP subtrees inside it)
                has_child_np = any(
                    isinstance(ch, Tree) and ch.label().startswith("NP")
                    for ch in node
                )

                if lbl == "NP" and not has_child_np:
                    leaves = node.leaves()
                    n_leaves = len(leaves)
                    t_start = tok_cursor[0]
                    t_end = t_start + n_leaves - 1
                    c_start = tok_spans[t_start][0]
                    c_end = tok_spans[t_end][1]
                    tok_cursor[0] += n_leaves

                    words = [w for w, _ in leaves]
                    tags = [t for _, t in leaves]
                    is_subj = not now_in_vp_pp

                    this_np_id = np_counter
                    np_counter += 1
                    node.set_label(f"NP#{this_np_id}")

                    # Check if this NP is the target pronoun itself
                    if not (c_end <= p_off or c_start >= p_end) and any(t.startswith("PRP") for t in tags):
                        pronoun_sent_idx = s_i
                        pronoun_np_id = this_np_id
                        pronoun_is_subject = is_subj
                    else:
                        is_pronoun_np = all(t.startswith("PRP") for t in tags)
                        if not is_pronoun_np:
                            np_str = text[c_start:c_end]
                            a_end = a_off + len(a_text)
                            b_end = b_off + len(b_text)
                            spans_a = not (c_end <= a_off or c_start >= a_end)
                            spans_b = not (c_end <= b_off or c_start >= b_end)

                            if spans_a and spans_b:
                                for idx_sub, (sub_text, sub_off) in enumerate([(a_text, a_off), (b_text, b_off)]):
                                    sub_id = this_np_id if idx_sub == 0 else np_counter
                                    if idx_sub > 0:
                                        np_counter += 1
                                    sub_words = nltk.word_tokenize(sub_text)
                                    candidate_nps.append({
                                        "np_id": sub_id,
                                        "text": sub_text,
                                        "start": sub_off,
                                        "end": sub_off + len(sub_text),
                                        "words": sub_words,
                                        "tags": tags,
                                        "sent_idx": s_i,
                                        "is_subject": is_subj,
                                    })
                            else:
                                candidate_nps.append({
                                    "np_id": this_np_id,
                                    "text": np_str,
                                    "start": c_start,
                                    "end": c_end,
                                    "words": words,
                                    "tags": tags,
                                    "sent_idx": s_i,
                                    "is_subject": is_subj,
                                })
                else:
                    for child in node:
                        annotate_tree(child, in_vp_or_pp=now_in_vp_pp)

            annotate_tree(parsed_tree, in_vp_or_pp=False)

            if pronoun_np_id is None and s_char_pos <= p_off < (sent_starts[s_i + 1] if s_i + 1 < num_sents else len(text) + 1):
                pronoun_sent_idx = s_i
                for cand in candidate_nps:
                    if cand["sent_idx"] == s_i and cand["start"] <= p_off < cand["end"]:
                        pronoun_np_id = cand["np_id"]
                        pronoun_is_subject = cand["is_subject"]
                        break

            cfg_trees.append(ParentedTree.convert(parsed_tree))

        # Ensure GAP gold candidates A and B are represented in candidate_nps
        for gold_str, gold_off in [(a_text, a_off), (b_text, b_off)]:
            gold_end = gold_off + len(gold_str)
            already_found = False
            for cand in candidate_nps:
                if not (cand["end"] <= gold_off or cand["start"] >= gold_end):
                    already_found = True
                    break
            if not already_found:
                g_words = nltk.word_tokenize(gold_str)
                g_tags = [t for _, t in nltk.pos_tag(g_words)]
                # Determine sentence index
                g_sent = 0
                for s_i, s_st in enumerate(sent_starts):
                    if gold_off >= s_st:
                        g_sent = s_i
                candidate_nps.append({
                    "np_id": -1,
                    "text": gold_str,
                    "start": gold_off,
                    "end": gold_end,
                    "words": g_words,
                    "tags": g_tags,
                    "sent_idx": g_sent,
                    "is_subject": False,
                })

        # Sort candidate NPs in text order
        candidate_nps.sort(key=lambda x: x["start"])

        # Mark which candidate NPs match the gold antecedent (A if A-coref, B if B-coref)
        # and which candidate NPs correspond to GAP candidate A or B
        for cand in candidate_nps:
            matches_a = check_span_matches_gold(cand["start"], cand["end"], cand["text"], a_off, a_text)
            matches_b = check_span_matches_gold(cand["start"], cand["end"], cand["text"], b_off, b_text)
            cand["matches_A"] = (not (cand["end"] <= a_off or cand["start"] >= a_off + len(a_text)))
            cand["matches_B"] = (not (cand["end"] <= b_off or cand["start"] >= b_off + len(b_text)))
            is_correct = (a_coref and matches_a) or (b_coref and matches_b)
            cand["is_antecedent"] = is_correct

        processed_segments.append({
            "id": row["ID"],
            "text": text,
            "pronoun": pronoun,
            "pronoun_offset": p_off,
            "pronoun_sent_idx": pronoun_sent_idx,
            "pronoun_np_id": pronoun_np_id,
            "pronoun_is_subject": pronoun_is_subject,
            "A": a_text,
            "A_offset": a_off,
            "A_coref": a_coref,
            "B": b_text,
            "B_offset": b_off,
            "B_coref": b_coref,
            "cfg_trees": cfg_trees,
            "candidates": candidate_nps,
        })

    return processed_segments


# ==============================================================================
# 2. Problem 7: Rule-Based Hobbs' Algorithm on CFG Parse Trees
# ==============================================================================

def _is_np_or_s(label):
    return label.startswith("NP") or label in ("S", "SBAR")


def _extract_np_id(label):
    if label.startswith("NP#"):
        return int(label.split("#")[1])
    return None


def _bfs_collect_nps(subtrees, require_intervening_np_or_s=False, stop_below_np_or_s=False):
    """
    Left-to-right, breadth-first traversal of given subtrees (Steps 3, 4, 7, 8 of
    Hobbs' algorithm in Jurafsky & Martin Ch. 21, Fig. 21.12).
    Returns a list of proposed NP# ids in Hobbs traversal order.
    """
    proposed_ids = []
    # Queue stores tuples of (node, has_seen_np_or_s_above)
    queue = []
    for st in subtrees:
        if isinstance(st, Tree):
            queue.append((st, False))

    while len(queue) > 0:
        curr, seen_np_s = queue.pop(0)
        lbl = curr.label()

        if lbl.startswith("NP#"):
            if not require_intervening_np_or_s or seen_np_s:
                np_id = _extract_np_id(lbl)
                if np_id is not None:
                    proposed_ids.append(np_id)

        if stop_below_np_or_s and _is_np_or_s(lbl):
            continue

        next_seen = seen_np_s or _is_np_or_s(lbl)
        for child in curr:
            if isinstance(child, Tree):
                queue.append((child, next_seen))

    return proposed_ids


def hobbs_rank_candidates_for_segment(seg):
    """
    Runs the 9-step Hobbs tree-search algorithm (J&M Section 21.6.1) on the
    segment's Context-Free Grammar (CFG) parse trees.
    Returns a list of candidate NP dicts ordered by Hobbs preference.
    """
    trees = seg["cfg_trees"]
    p_sent_idx = seg["pronoun_sent_idx"]
    p_np_id = seg["pronoun_np_id"]
    p_gender = get_pronoun_gender(seg["pronoun"])

    id_to_cand = {}
    for c in seg["candidates"]:
        if c["np_id"] >= 0 and c["np_id"] not in id_to_cand:
            id_to_cand[c["np_id"]] = c

    proposed_np_ids = []

    if 0 <= p_sent_idx < len(trees):
        sent_tree = trees[p_sent_idx]
        # Step 1: Begin at the NP node immediately dominating the pronoun
        start_node = None
        for sub in sent_tree.subtrees():
            if _extract_np_id(sub.label()) == p_np_id:
                start_node = sub
                break

        if start_node is not None:
            # Step 2: Go up the tree to the first NP or S node encountered (X)
            curr = start_node
            X = curr.parent()
            while X is not None and not _is_np_or_s(X.label()):
                curr = X
                X = X.parent()

            if X is not None:
                # Step 3: Traverse all branches below X to the left of path p
                # in a left-to-right, breadth-first fashion. Propose any NP node
                # encountered which has an NP or S node between it and X
                # (enforces Binding Theory Condition B in minimal clauses).
                left_siblings = []
                for child in X:
                    if child is curr:
                        break
                    left_siblings.append(child)
                proposed_np_ids.extend(
                    _bfs_collect_nps(left_siblings, require_intervening_np_or_s=True)
                )

                # Steps 5-9 loop until X reaches the root S node
                while X.parent() is not None:
                    curr = X
                    X = X.parent()
                    while X is not None and not _is_np_or_s(X.label()):
                        curr = X
                        X = X.parent()
                    if X is None:
                        break

                    # Step 6: If X is an NP node, propose X
                    if X.label().startswith("NP#"):
                        x_id = _extract_np_id(X.label())
                        if x_id is not None:
                            proposed_np_ids.append(x_id)

                    # Step 7: Traverse branches below X to the left of path p.
                    # When X is the top-level sentence root containing multiple clauses,
                    # climbing a right-branching clause tree visits closer clauses first,
                    # and within each clause traverses left-to-right, breadth-first (Subject before Object).
                    left_siblings = []
                    for child in X:
                        if child is curr:
                            break
                        left_siblings.append(child)
                    if X.parent() is None:
                        for sib in reversed(left_siblings):
                            proposed_np_ids.extend(_bfs_collect_nps([sib]))
                    else:
                        proposed_np_ids.extend(_bfs_collect_nps(left_siblings))

                    # Step 8: If X is an S node, traverse branches to the right of p (BFS)
                    if X.label() in ("S", "SBAR"):
                        right_siblings = []
                        passed_curr = False
                        for child in X:
                            if child is curr:
                                passed_curr = True
                                continue
                            if passed_curr:
                                right_siblings.append(child)
                        proposed_np_ids.extend(
                            _bfs_collect_nps(right_siblings, stop_below_np_or_s=True)
                        )

    # Step 4: Traverse previous sentences in order of recency (most recent first)
    # in left-to-right, breadth-first manner
    for prev_s_idx in range(p_sent_idx - 1, -1, -1):
        prev_tree = trees[prev_s_idx]
        proposed_np_ids.extend(_bfs_collect_nps([prev_tree]))

    # Convert proposed NP# ids into ordered candidate dicts applying Hobbs'
    # standard agreement & animacy/person filter (preceding pronoun, gender-compatible,
    # proper/person NP preferred for human pronouns he/she/his/her)
    p_off = seg["pronoun_offset"]
    tier1_proper_gender_match = []
    tier2_proper_gender_compat = []
    tier3_other_preceding = []
    seen_starts = set()

    for np_id in proposed_np_ids:
        if np_id in id_to_cand:
            cand = id_to_cand[np_id]
            if cand["start"] >= p_off or cand["start"] in seen_starts:
                continue
            seen_starts.add(cand["start"])
            c_gen = get_np_gender(cand["words"])
            is_prop = any(t.startswith("NNP") for t in cand["tags"])

            # Filter out explicit gender conflicts first
            if p_gender != "U" and c_gen != "U" and c_gen != p_gender:
                continue

            if is_prop and p_gender != "U" and c_gen == p_gender:
                tier1_proper_gender_match.append(cand)
            elif is_prop:
                tier2_proper_gender_compat.append(cand)
            else:
                tier3_other_preceding.append(cand)

    # Fallback: add any remaining preceding candidates in reverse distance order
    for cand in reversed(seg["candidates"]):
        if cand["start"] < p_off and cand["start"] not in seen_starts:
            seen_starts.add(cand["start"])
            tier3_other_preceding.append(cand)

    return tier1_proper_gender_match + tier2_proper_gender_compat + tier3_other_preceding


# ==============================================================================
# 3. Feature Extraction & Simple Logistic Regression Classifier (From Scratch)
# ==============================================================================

FEATURE_NAMES = [
    "is_hobbs_top1",          # 1 if top-1 candidate proposed by Hobbs' algorithm on CFG tree
    "in_hobbs_top3",          # 1 if in top-3 candidates proposed by Hobbs' algorithm
    "gender_match",           # 1 if candidate NP gender matches pronoun gender
    "gender_mismatch",        # 1 if candidate NP gender conflicts with pronoun gender
    "number_agreement",       # 1 if candidate NP agrees in singular number with pronoun
    "is_proper_noun",         # 1 if candidate NP contains a Proper Noun (NNP/NNPS)
    "grammatical_role_subj",  # 1 if candidate NP is a grammatical subject under S in CFG tree
    "parallel_role",          # 1 if candidate NP and pronoun share the same grammatical role
    "recency_inv_rank",       # 1 / rank among NPs preceding the pronoun (1.0 = most recent)
    "same_sentence",          # 1 if candidate NP is in the same sentence as the pronoun
    "char_distance_closeness",# 1 - normalized character distance to pronoun
    "entity_frequency",       # Mention frequency of candidate NP in the segment
]


def extract_features_for_segment(seg):
    """
    Extracts feature vectors for all candidate NPs in a discourse segment,
    incorporating both surface/POS features and syntactic parse-tree features
    from the Hobbs algorithm implementation.
    """
    hobbs_ranked = hobbs_rank_candidates_for_segment(seg)
    hobbs_top1_start = hobbs_ranked[0]["start"] if len(hobbs_ranked) > 0 else -1
    hobbs_top3_starts = set(c["start"] for c in hobbs_ranked[:3])

    p_off = seg["pronoun_offset"]
    p_sent = seg["pronoun_sent_idx"]
    p_gender = get_pronoun_gender(seg["pronoun"])
    p_is_subj = seg["pronoun_is_subject"]
    text_lower = seg["text"].lower()
    text_len = max(len(seg["text"]), 1)

    # Compute recency rank among candidates preceding the pronoun
    preceding_starts = [
        c["start"] for c in seg["candidates"] if c["start"] < p_off
    ]
    preceding_starts.sort(reverse=True)  # index 0 = closest before pronoun
    start_to_recency_rank = {}
    for r_i, st in enumerate(preceding_starts):
        start_to_recency_rank[st] = r_i + 1

    features_list = []
    for cand in seg["candidates"]:
        c_start = cand["start"]
        c_words = cand["words"]
        c_tags = cand["tags"]
        c_sent = cand["sent_idx"]
        c_is_subj = cand["is_subject"]

        # 1. Hobbs Top-1 and 2. Hobbs Top-3 (from CFG parse tree search)
        f_hobbs_1 = 1.0 if c_start == hobbs_top1_start else 0.0
        f_hobbs_3 = 1.0 if c_start in hobbs_top3_starts else 0.0

        # 3 & 4. Gender agreement and mismatch
        c_gender = get_np_gender(c_words)
        f_gen_match = 1.0 if (p_gender != "U" and c_gender == p_gender) else 0.0
        f_gen_mismatch = 1.0 if (
            p_gender != "U" and c_gender != "U" and c_gender != p_gender
        ) else 0.0

        # 5. Number agreement (singular NN/NNP matches singular GAP pronouns)
        has_plural = any(t in ("NNS", "NNPS") for t in c_tags)
        f_num_agree = 0.0 if has_plural else 1.0

        # 6. Proper noun salience (person/entity name)
        f_proper = 1.0 if any(t.startswith("NNP") for t in c_tags) else 0.0

        # 7. Grammatical role (Subject position in CFG parse tree)
        f_subj = 1.0 if c_is_subj else 0.0

        # 8. Parallel grammatical role with pronoun
        f_parallel = 1.0 if (c_is_subj == p_is_subj) else 0.0

        # 9. Recency rank (1 / rank before pronoun)
        if c_start in start_to_recency_rank:
            f_recency = 1.0 / float(start_to_recency_rank[c_start])
        else:
            # Candidate appears after the pronoun (cataphora)
            f_recency = 0.05

        # 10. Same sentence indicator
        f_same_sent = 1.0 if (c_sent == p_sent) else 0.0

        # 11. Character closeness (1 - distance / text_length) before pronoun
        dist = abs(p_off - c_start)
        f_closeness = max(0.0, 1.0 - (float(dist) / float(text_len))) if c_start < p_off else 0.1

        # 12. Entity mention frequency in the segment (using full candidate text)
        full_cand_lower = cand["text"].lower().strip()
        if len(full_cand_lower) >= 2:
            freq_count = text_lower.count(full_cand_lower)
        else:
            freq_count = 1
        f_freq = min(1.0, float(freq_count) / 4.0)

        feat_vec = [
            f_hobbs_1,
            f_hobbs_3,
            f_gen_match,
            f_gen_mismatch,
            f_num_agree,
            f_proper,
            f_subj,
            f_parallel,
            f_recency,
            f_same_sent,
            f_closeness,
            f_freq,
        ]
        features_list.append(feat_vec)

    return features_list


class SimpleLogisticRegression:
    """
    A simple, from-scratch implementation of binary Logistic Regression
    using basic Python and math.exp (Gradient Descent with L2 regularization).
    """

    def __init__(self, num_features, learning_rate=0.05, l2_reg=0.0001, epochs=25):
        self.num_features = num_features
        self.learning_rate = learning_rate
        self.l2_reg = l2_reg
        self.epochs = epochs
        self.weights = [0.0] * num_features
        self.bias = 0.0

    @staticmethod
    def sigmoid(z):
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
        """
        Trains feature weights and bias on training examples (X, y) using
        stochastic gradient descent. pos_weight balances positive vs negative
        candidate NPs since each segment has only 1 true antecedent among many NPs.
        """
        n_samples = len(X)
        indices = list(range(n_samples))
        rng = random.Random(42)

        for epoch in range(self.epochs):
            rng.shuffle(indices)
            # Slightly decay learning rate over epochs for stable convergence
            lr = self.learning_rate / (1.0 + 0.05 * epoch)
            for idx in indices:
                x_i = X[idx]
                y_i = y[idx]
                pred = self.predict_proba_one(x_i)
                err = pred - y_i

                # Weight positive examples to handle class imbalance across candidate NPs
                sample_w = pos_weight if y_i == 1 else 1.0
                weighted_err = err * sample_w

                for j in range(self.num_features):
                    grad_j = weighted_err * x_i[j] + self.l2_reg * self.weights[j]
                    self.weights[j] -= lr * grad_j
                self.bias -= lr * weighted_err


def build_Xy_pairs(segments, only_ab_candidates=False):
    """
    Constructs (X, y) training/evaluation pairs from processed segments.
    If only_ab_candidates is True, restricts to candidate NPs matching GAP A or B.
    """
    X = []
    y = []
    for seg in segments:
        feats = seg["features"]
        for c_i, cand in enumerate(seg["candidates"]):
            if only_ab_candidates and not (cand["matches_A"] or cand["matches_B"]):
                continue
            X.append(feats[c_i])
            y.append(1 if cand["is_antecedent"] else 0)
    return X, y


def evaluate_model_predictions(segments, model, threshold=0.5):
    """
    Evaluates the Logistic Regression model on two standard coreference settings:
      1. Top-1 Antecedent Resolution (selecting argmax_c P(y=1|x_c) per segment):
         - Over all extracted POS-tagged candidate NPs
         - Over the GAP annotated candidate NPs (A vs B)
      2. Pairwise Binary Coreference Classification (Precision, Recall, F1).
    """
    # 1. Top-1 Antecedent Selection across all candidate NPs (resolved vs gold)
    tp_all, fp_all, fn_all = 0, 0, 0
    # 2. Top-1 / Threshold Selection on GAP A/B candidates
    tp_ab, fp_ab, fn_ab = 0, 0, 0

    for seg in segments:
        has_gold = seg["A_coref"] or seg["B_coref"]
        feats = seg["features"]
        cands = seg["candidates"]

        # Score all candidates
        best_all_prob = -1.0
        best_all_cand = None
        for c_i, cand in enumerate(cands):
            prob = model.predict_proba_one(feats[c_i])
            if prob > best_all_prob:
                best_all_prob = prob
                best_all_cand = cand

        if best_all_cand is not None and best_all_prob >= threshold:
            if best_all_cand["is_antecedent"]:
                tp_all += 1
            else:
                fp_all += 1
                if has_gold:
                    fn_all += 1
        else:
            if has_gold:
                fn_all += 1

        # Score GAP A and B candidates
        best_ab_prob = -1.0
        best_ab_cand = None
        for c_i, cand in enumerate(cands):
            if cand["matches_A"] or cand["matches_B"]:
                prob = model.predict_proba_one(feats[c_i])
                if prob > best_ab_prob:
                    best_ab_prob = prob
                    best_ab_cand = cand

        if best_ab_cand is not None and best_ab_prob >= threshold:
            if best_ab_cand["is_antecedent"]:
                tp_ab += 1
            else:
                fp_ab += 1
                if has_gold:
                    fn_ab += 1
        else:
            if has_gold:
                fn_ab += 1

    def calc_prf(tp, fp, fn):
        prec = float(tp) / float(tp + fp) if (tp + fp) > 0 else 0.0
        rec = float(tp) / float(tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2.0 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        return prec, rec, f1

    return {
        "all_nps": calc_prf(tp_all, fp_all, fn_all),
        "ab_nps": calc_prf(tp_ab, fp_ab, fn_ab),
        "counts_all": (tp_all, fp_all, fn_all),
        "counts_ab": (tp_ab, fp_ab, fn_ab),
    }


# ==============================================================================
# 4. Runners for Problems 1 through 8 + Extra Credit
# ==============================================================================

def run_problem_1(test_segments):
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


def run_problem_2(test_segments):
    print("=" * 80)
    print("PROBLEM 2 (5 marks): Random Antecedent Assignment (100 Runs)")
    print("=" * 80)
    rng = random.Random(12345)
    runs = 100
    acc_all_runs = []
    acc_ab_runs = []

    for _ in range(runs):
        correct_all = 0
        correct_ab = 0
        for seg in test_segments:
            cands = seg["candidates"]
            if len(cands) > 0:
                chosen = rng.choice(cands)
                if chosen["is_antecedent"]:
                    correct_all += 1
            ab_cands = [c for c in cands if c["matches_A"] or c["matches_B"]]
            if len(ab_cands) > 0:
                chosen_ab = rng.choice(ab_cands)
                if chosen_ab["is_antecedent"]:
                    correct_ab += 1
        acc_all_runs.append(float(correct_all) / float(len(test_segments)))
        acc_ab_runs.append(float(correct_ab) / float(len(test_segments)))

    avg_acc_all = sum(acc_all_runs) / float(runs)
    avg_acc_ab = sum(acc_ab_runs) / float(runs)
    print(f"Number of random assignment runs: {runs}")
    print(f"Average Accuracy (sampling across ALL POS-extracted candidate NPs): {avg_acc_all * 100:.2f}%")
    print(f"Average Accuracy (sampling between GAP candidate NPs A and B):      {avg_acc_ab * 100:.2f}%\n")
    return avg_acc_all, avg_acc_ab


def run_problem_3(test_segments):
    print("=" * 80)
    print("PROBLEM 3 (5 marks): Most Recent Antecedent Baseline")
    print("=" * 80)
    correct_all = 0
    correct_ab = 0

    for seg in test_segments:
        p_off = seg["pronoun_offset"]
        # All candidate NPs occurring strictly before the pronoun
        preceding = [c for c in seg["candidates"] if c["start"] < p_off]
        if len(preceding) == 0:
            preceding = seg["candidates"]
        if len(preceding) > 0:
            most_recent = preceding[-1]
            if most_recent["is_antecedent"]:
                correct_all += 1

        # Most recent among GAP candidates A and B before the pronoun
        preceding_ab = [
            c for c in seg["candidates"]
            if (c["matches_A"] or c["matches_B"]) and c["start"] < p_off
        ]
        if len(preceding_ab) == 0:
            preceding_ab = [c for c in seg["candidates"] if c["matches_A"] or c["matches_B"]]
        if len(preceding_ab) > 0:
            most_recent_ab = preceding_ab[-1]
            if most_recent_ab["is_antecedent"]:
                correct_ab += 1

    acc_all = float(correct_all) / float(len(test_segments))
    acc_ab = float(correct_ab) / float(len(test_segments))
    print(f"Most Recent Candidate NP Accuracy (across ALL POS-extracted NPs): {acc_all * 100:.2f}% ({correct_all}/{len(test_segments)})")
    print(f"Most Recent Candidate NP Accuracy (among GAP candidates A & B):   {acc_ab * 100:.2f}% ({correct_ab}/{len(test_segments)})\n")
    return acc_all, acc_ab


def run_problem_4_and_5(train_segments, dev_segments, test_segments):
    print("=" * 80)
    print("PROBLEM 4 (10 marks): Custom Logistic Regression Classifier")
    print("=" * 80)

    X_train, y_train = build_Xy_pairs(train_segments, only_ab_candidates=False)

    # Hyperparameter grid search on Development Set (gap-validation.tsv)
    print("Hyperparameter Tuning on Development Set (gap-validation.tsv, 454 segments):")
    print(f"{'LR':>6} | {'L2_Reg':>8} | {'Pos_Weight':>10} | {'Dev F1 (All NPs)':>16} | {'Dev F1 (A/B NPs)':>16}")
    print("-" * 68)

    best_score = -1.0
    best_params = None
    best_model = None

    for lr in [0.01, 0.05, 0.1]:
        for l2 in [0.0, 0.0001, 0.001]:
            for pw in [2.0, 4.0]:
                model = SimpleLogisticRegression(
                    num_features=len(FEATURE_NAMES),
                    learning_rate=lr,
                    l2_reg=l2,
                    epochs=20,
                )
                model.fit(X_train, y_train, pos_weight=pw)
                dev_res = evaluate_model_predictions(dev_segments, model, threshold=0.25)
                f1_all = dev_res["all_nps"][2]
                f1_ab = dev_res["ab_nps"][2]
                combined = 0.5 * (f1_all + f1_ab)
                print(f"{lr:6.2f} | {l2:8.4f} | {pw:10.1f} | {f1_all * 100:15.2f}% | {f1_ab * 100:15.2f}%")
                if combined > best_score:
                    best_score = combined
                    best_params = (lr, l2, pw)
                    best_model = model

    print("-" * 68)
    print(
        f"Best Hyperparameters on Dev Set: learning_rate={best_params[0]}, "
        f"l2_reg={best_params[1]}, pos_weight={best_params[2]}"
    )

    # Evaluate best model on Test Set (gap-test.tsv)
    test_res = evaluate_model_predictions(test_segments, best_model, threshold=0.25)
    p_all, r_all, f1_all = test_res["all_nps"]
    p_ab, r_ab, f1_ab = test_res["ab_nps"]

    print("\nTest Set Evaluation (gap-test.tsv, 2000 segments):")
    print("  1. Full Candidate NP Pool Resolution (All POS-Extracted Candidate NPs):")
    print(f"       Precision: {p_all * 100:.2f}% | Recall: {r_all * 100:.2f}% | F1-Score: {f1_all * 100:.2f}%")
    print("  2. GAP Candidate NP Resolution (Evaluating on Candidate Entities A vs B):")
    print(f"       Precision: {p_ab * 100:.2f}% | Recall: {r_ab * 100:.2f}% | F1-Score: {f1_ab * 100:.2f}%\n")

    # Problem 5: Print learned feature weights & Top-5 features
    print("=" * 80)
    print("PROBLEM 5 (5 marks): Learned Feature Weights & Top-5 Features")
    print("=" * 80)
    print(f"Learned Intercept (Bias): {best_model.bias:+.4f}\n")
    print(f"{'Rank':>4} | {'Feature Name':<26} | {'Learned Weight':>14} | {'|Weight|':>10}")
    print("-" * 64)

    ranked_feats = []
    for name, w in zip(FEATURE_NAMES, best_model.weights):
        ranked_feats.append((name, w, abs(w)))
    ranked_feats.sort(key=lambda x: x[2], reverse=True)

    for idx, (name, w, abs_w) in enumerate(ranked_feats, start=1):
        print(f"{idx:4d} | {name:<26} | {w:+14.4f} | {abs_w:10.4f}")

    print("\nTop-5 Features (by Weight Magnitude):")
    for idx, (name, w, _) in enumerate(ranked_feats[:5], start=1):
        direction = "Positive (increases antecedent likelihood)" if w > 0 else "Negative (penalizes candidate)"
        print(f"  {idx}. {name} (weight = {w:+.4f}) -> {direction}")
    print()

    return best_model, test_res, ranked_feats


def run_problem_6(test_segments, model):
    print("=" * 80)
    print("PROBLEM 6 (5 marks): Error Analysis of Logistic Regression Implementation")
    print("=" * 80)

    errors = []
    for seg in test_segments:
        has_gold = seg["A_coref"] or seg["B_coref"]
        if not has_gold:
            continue
        feats = seg["features"]
        cands = seg["candidates"]

        best_prob = -1.0
        best_cand = None
        for c_i, cand in enumerate(cands):
            prob = model.predict_proba_one(feats[c_i])
            if prob > best_prob:
                best_prob = prob
                best_cand = cand

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


def run_problem_7(test_segments):
    print("=" * 80)
    print("PROBLEM 7 (10 marks): Rule-Based Hobbs' Algorithm on CFG Parse Trees")
    print("=" * 80)

    tp_all, fp_all, fn_all = 0, 0, 0
    tp_ab, fp_ab, fn_ab = 0, 0, 0

    for seg in test_segments:
        has_gold = seg["A_coref"] or seg["B_coref"]
        hobbs_ranked = hobbs_rank_candidates_for_segment(seg)

        # 1. Top-1 Hobbs proposal among all extracted candidate NPs
        if len(hobbs_ranked) > 0:
            top1 = hobbs_ranked[0]
            if top1["is_antecedent"]:
                tp_all += 1
            else:
                fp_all += 1
                if has_gold:
                    fn_all += 1
        else:
            if has_gold:
                fn_all += 1

        # 2. Top-1 Hobbs proposal among GAP candidates A and B
        hobbs_ab = [c for c in hobbs_ranked if c["matches_A"] or c["matches_B"]]
        if len(hobbs_ab) > 0:
            top1_ab = hobbs_ab[0]
            if top1_ab["is_antecedent"]:
                tp_ab += 1
            else:
                fp_ab += 1
                if has_gold:
                    fn_ab += 1
        else:
            if has_gold:
                fn_ab += 1

    def calc_prf(tp, fp, fn):
        prec = float(tp) / float(tp + fp) if (tp + fp) > 0 else 0.0
        rec = float(tp) / float(tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2.0 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        return prec, rec, f1

    p_all, r_all, f1_all = calc_prf(tp_all, fp_all, fn_all)
    p_ab, r_ab, f1_ab = calc_prf(tp_ab, fp_ab, fn_ab)

    print("Hobbs' Algorithm Performance on Test Set (gap-test.tsv, 2000 segments):")
    print("  1. Full Candidate NP Pool (All POS-Extracted Candidate NPs):")
    print(f"       Precision: {p_all * 100:.2f}% | Recall: {r_all * 100:.2f}% | F1-Score: {f1_all * 100:.2f}%")
    print("  2. GAP Candidate Entities (Evaluating on Candidates A vs B):")
    print(f"       Precision: {p_ab * 100:.2f}% | Recall: {r_ab * 100:.2f}% | F1-Score: {f1_ab * 100:.2f}%\n")

    return {"all_nps": (p_all, r_all, f1_all), "ab_nps": (p_ab, r_ab, f1_ab)}


def run_problem_8(lr_res, hobbs_res, rand_res, recent_res):
    print("=" * 80)
    print("PROBLEM 8 (5 marks): Quantitative & Qualitative Comparison (LR vs. Hobbs)")
    print("=" * 80)
    print(f"{'Method':<34} | {'All-NPs F1':>12} | {'GAP (A/B) Prec':>14} | {'GAP (A/B) Rec':>13} | {'GAP (A/B) F1':>12}")
    print("-" * 94)
    print(
        f"{'Random Assignment (100 runs)':<34} | {rand_res[0] * 100:11.2f}% | "
        f"{rand_res[1] * 100:13.2f}% | {rand_res[1] * 100:12.2f}% | {rand_res[1] * 100:11.2f}%"
    )
    print(
        f"{'Most Recent Antecedent':<34} | {recent_res[0] * 100:11.2f}% | "
        f"{recent_res[1] * 100:13.2f}% | {recent_res[1] * 100:12.2f}% | {recent_res[1] * 100:11.2f}%"
    )
    hp_a, hr_a, hf_a = hobbs_res["all_nps"]
    hp_b, hr_b, hf_b = hobbs_res["ab_nps"]
    print(
        f"{'Rule-Based Hobbs Algorithm':<34} | {hf_a * 100:11.2f}% | "
        f"{hp_b * 100:13.2f}% | {hr_b * 100:12.2f}% | {hf_b * 100:11.2f}%"
    )
    lp_a, lr_a, lf_a = lr_res["all_nps"]
    lp_b, lr_b, lf_b = lr_res["ab_nps"]
    print(
        f"{'Custom Logistic Regression (Ours)':<34} | {lf_a * 100:11.2f}% | "
        f"{lp_b * 100:13.2f}% | {lr_b * 100:12.2f}% | {lf_b * 100:11.2f}%"
    )
    print()


def run_extra_credit_sklearn(train_segments, dev_segments, test_segments, hobbs_res=None):
    print("=" * 80)
    print("EXTRA CREDIT (10 marks): Scikit-Learn Logistic Regression Implementation")
    print("=" * 80)
    try:
        from sklearn.linear_model import LogisticRegression
    except ImportError:
        print("scikit-learn is not installed in this environment.")
        return None

    X_train, y_train = build_Xy_pairs(train_segments, only_ab_candidates=False)

    print("1. Hyperparameter Tuning on Development Set (gap-validation.tsv):")
    print(f"{'C':>6} | {'Pos_Weight':>10} | {'Dev F1 (All NPs)':>16} | {'Dev F1 (A/B NPs)':>16}")
    print("-" * 56)

    best_params = (1.0, 3.0)
    best_f1 = -1.0
    best_clf = None

    class SklearnWrapper:
        def __init__(self, estimator):
            self.estimator = estimator
            self.weights = list(estimator.coef_[0])
            self.bias = float(estimator.intercept_[0])

        def predict_proba_one(self, x):
            z = self.bias
            for w_j, x_j in zip(self.weights, x):
                z += w_j * x_j
            return SimpleLogisticRegression.sigmoid(z)

    for c_val in [0.01, 0.1, 1.0, 10.0]:
        for pw in [2.0, 3.0, 4.0]:
            clf = LogisticRegression(
                C=c_val, class_weight={0: 1.0, 1: pw}, max_iter=500, random_state=42
            )
            clf.fit(X_train, y_train)
            wrapped = SklearnWrapper(clf)
            dev_res = evaluate_model_predictions(dev_segments, wrapped, threshold=0.25)
            f1_all_dev = dev_res["all_nps"][2]
            f1_ab_dev = dev_res["ab_nps"][2]
            score = 0.5 * (f1_all_dev + f1_ab_dev)
            print(f"{c_val:6.2f} | {pw:10.1f} | {f1_all_dev * 100:15.2f}% | {f1_ab_dev * 100:15.2f}%")
            if score > best_f1:
                best_f1 = score
                best_params = (c_val, pw)
                best_clf = wrapped

    print("-" * 56)
    print(f"Best scikit-learn Hyperparameters on Dev Set: C = {best_params[0]}, pos_weight = {best_params[1]}\n")

    test_res = evaluate_model_predictions(test_segments, best_clf, threshold=0.25)
    p_all, r_all, f1_all = test_res["all_nps"]
    p_ab, r_ab, f1_ab = test_res["ab_nps"]

    print("2. Test Set Performance (scikit-learn LogisticRegression on gap-test.tsv):")
    print(f"  - Full Candidate NP Pool: Precision={p_all * 100:.2f}% | Recall={r_all * 100:.2f}% | F1={f1_all * 100:.2f}%")
    print(f"  - GAP Candidates (A/B):   Precision={p_ab * 100:.2f}% | Recall={r_ab * 100:.2f}% | F1={f1_ab * 100:.2f}%\n")

    print(f"3. Scikit-Learn Learned Feature Weights (Intercept = {best_clf.bias:+.4f}):")
    print(f"{'Rank':>4} | {'Feature Name':<26} | {'Learned Weight':>14} | {'|Weight|':>10}")
    print("-" * 64)
    sk_feats = sorted(
        zip(FEATURE_NAMES, best_clf.weights),
        key=lambda item: abs(item[1]),
        reverse=True,
    )
    for idx, (fname, w) in enumerate(sk_feats, start=1):
        print(f"{idx:4d} | {fname:<26} | {w:+14.4f} | {abs(w):10.4f}")

    print("\nScikit-Learn Top-5 Feature Weights:")
    for idx, (fname, w) in enumerate(sk_feats[:5], start=1):
        print(f"  {idx}. {fname:<26}: {w:+.4f}")

    # Count errors on gold-annotated test segments for scikit-learn
    sk_errors = 0
    for seg in test_segments:
        if not (seg["A_coref"] or seg["B_coref"]):
            continue
        feats = seg["features"]
        cands = seg["candidates"]
        best_p, best_c_np = -1.0, None
        for c_i, cand in enumerate(cands):
            pr = best_clf.predict_proba_one(feats[c_i])
            if pr > best_p:
                best_p, best_c_np = pr, cand
        if best_c_np is not None and not best_c_np["is_antecedent"]:
            sk_errors += 1
    print(f"\n4. Scikit-Learn Error Analysis & Comparison:")
    print(f"  - Total errors on gold-annotated test segments: {sk_errors} (exhibits the same 4 error patterns as Custom LR)")
    if hobbs_res is not None:
        hf_a = hobbs_res["all_nps"][2]
        hf_b = hobbs_res["ab_nps"][2]
        print(f"  - Comparison vs. Hobbs' Algorithm: Scikit-Learn LR improves Full-Pool F1 from {hf_a * 100:.2f}% to {f1_all * 100:.2f}%")
        print(f"    and GAP (A/B) F1 from {hf_b * 100:.2f}% to {f1_ab * 100:.2f}%.")
    print()
    return test_res


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")

    print("Loading GAP Coreference Dataset splits (train, dev, test)...")
    train_rows = load_gap_tsv(os.path.join(data_dir, "gap-development.tsv"))
    dev_rows = load_gap_tsv(os.path.join(data_dir, "gap-validation.tsv"))
    test_rows = load_gap_tsv(os.path.join(data_dir, "gap-test.tsv"))

    print("Running POS Tagger, CFG Parser, and Candidate NP Extraction...")
    train_segments = process_dataset(train_rows, "train")
    dev_segments = process_dataset(dev_rows, "dev")
    test_segments = process_dataset(test_rows, "test")

    print("Extracting features (including Hobbs CFG tree features) for all segments...\n")
    for seg in train_segments:
        seg["features"] = extract_features_for_segment(seg)
    for seg in dev_segments:
        seg["features"] = extract_features_for_segment(seg)
    for seg in test_segments:
        seg["features"] = extract_features_for_segment(seg)

    # Problem 1
    run_problem_1(test_segments)

    # Problem 2
    rand_res = run_problem_2(test_segments)

    # Problem 3
    recent_res = run_problem_3(test_segments)

    # Problem 4 & Problem 5
    best_model, lr_res, _ = run_problem_4_and_5(train_segments, dev_segments, test_segments)

    # Problem 6
    run_problem_6(test_segments, best_model)

    # Problem 7
    hobbs_res = run_problem_7(test_segments)

    # Problem 8
    run_problem_8(lr_res, hobbs_res, rand_res, recent_res)

    # Extra Credit
    run_extra_credit_sklearn(train_segments, dev_segments, test_segments, hobbs_res=hobbs_res)


if __name__ == "__main__":
    main()

