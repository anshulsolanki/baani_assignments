# Module for Pronominal Anaphora Resolution and Topical Entity Salience (Model M3)
# Uses NLTK RegexpParser NP chunking, Binding Theory constraints, and a 2-sentence window

import nltk
from collections import Counter
from preprocess import flatten

# Third-person pronouns we want to resolve
PERSONAL_PRONOUNS = {
    "he", "him", "his",
    "she", "her", "hers",
    "it", "its",
    "they", "them", "their", "theirs"
}

REFLEXIVE_PRONOUNS = {
    "himself", "herself", "itself", "themselves"
}

ALL_TARGET_PRONOUNS = PERSONAL_PRONOUNS | REFLEXIVE_PRONOUNS

# Gender word lists (adapted from CL2 Assignment 4 Anaphora Resolution)
MASCULINE_WORDS = {
    "mr", "sir", "king", "prince", "father", "dad", "son", "brother", "uncle",
    "husband", "boy", "man", "gentleman", "actor", "hero", "villain", "director",
    "guy", "fellow", "chap", "policeman", "businessman", "waiter", "priest",
    "john", "james", "robert", "michael", "william", "david", "richard", "charles",
    "joseph", "thomas", "peter", "paul", "jack", "bob", "tom", "harry", "frank",
    "kevin", "brian", "GEORGE", "edward", "steven", "bruce", "arnold", "cameron"
}

FEMININE_WORDS = {
    "mrs", "ms", "miss", "madam", "queen", "princess", "mother", "mom", "daughter",
    "sister", "aunt", "wife", "girl", "woman", "lady", "actress", "heroine",
    "waitress", "bride", "widow", "mary", "linda", "elizabeth", "jennifer",
    "susan", "sarah", "jessica", "karen", "nancy", "lisa", "helen", "sandra",
    "alice", "julie", "rose", "jane", "anna", "kate", "emma", "claire", "rachel"
}

# Important movie-domain nouns that are often discourse centers in reviews
CORE_MOVIE_NOUNS = {
    "movie", "film", "plot", "story", "script", "screenplay", "acting",
    "performance", "character", "director", "cast", "ending", "scene",
    "dialogue", "comedy", "drama", "thriller", "sequel", "cinema", "work",
    "picture", "production", "pacing", "direction", "humor", "action"
}

# Generic filler nouns that should not be treated as main topical entities
STOP_ENTITIES = {
    "way", "time", "thing", "fact", "lot", "bit", "kind", "sort", "part",
    "point", "case", "hand", "place", "year", "day", "minute", "hour",
    "one", "someone", "anyone", "nothing", "everything", "something"
}

# Words after "it is/was ..." that indicate dummy/pleonastic "it" (not an entity)
PLEONASTIC_ADJ = {
    "clear", "obvious", "true", "false", "hard", "easy", "difficult",
    "impossible", "possible", "likely", "unlikely", "sad", "shame",
    "pity", "necessary", "important", "evident", "apparent", "worth"
}

# Simple CFG grammar to chunk Noun Phrases (NP) from POS tags
NP_GRAMMAR = r"""
    NP: {<DT|PRP\$>?<JJ.*>*<NN.*>+}
"""
NP_PARSER = nltk.RegexpParser(NP_GRAMMAR)

# Weight boost when a sentiment word modifies a top salient entity
SALIENT_ENTITY_BOOST = 1.35


# Determine gender/number category of a pronoun: M (male), F (female), N (neuter), P (plural)
def get_pronoun_category(word_lower):
    if word_lower in {"he", "him", "his", "himself"}:
        return "M"
    if word_lower in {"she", "her", "hers", "herself"}:
        return "F"
    if word_lower in {"it", "its", "itself"}:
        return "N"
    if word_lower in {"they", "them", "their", "theirs", "themselves"}:
        return "P"
    return "U"


# Determine gender/number category of a candidate Noun Phrase
def get_np_category(np_tokens, head_token):
    # Plural nouns (NNS or NNPS) match "they/them/their"
    if head_token.pos in {"NNS", "NNPS"}:
        return "P"

    for tok in np_tokens:
        w = tok.text.lower().strip(".")
        if w in FEMININE_WORDS or tok.lemma.lower() in FEMININE_WORDS:
            return "F"
        if w in MASCULINE_WORDS or tok.lemma.lower() in MASCULINE_WORDS:
            return "M"

    # Proper nouns (NNP) usually refer to people (actors, directors, characters)
    if head_token.pos == "NNP":
        return "PERSON"

    # Common singular nouns (like "movie", "plot", "script") are neuter ("it")
    return "N"


# Check if pronoun category and NP category agree in gender and number
def check_agreement(pron_cat, np_cat):
    if pron_cat == np_cat:
        return True
    # Proper names not in our small dictionary can match "he" or "she"
    if np_cat == "PERSON" and pron_cat in {"M", "F"}:
        return True
    # Singular human nouns like "character", "star", "lead" can match he/she/it
    return False


# Check if an occurrence of "it" is pleonastic (dummy "it", like "it is obvious that...")
def is_pleonastic_it(tokens, idx):
    tok = tokens[idx]
    if tok.text.lower() != "it":
        return False

    # Look at the next 1 to 3 words in the same sentence
    if idx + 2 < len(tokens):
        next1 = tokens[idx + 1].lemma.lower()
        next2 = tokens[idx + 2].lemma.lower()
        if next1 in {"be", "seem", "appear"} and next2 in PLEONASTIC_ADJ:
            if idx + 3 < len(tokens) and tokens[idx + 3].text.lower() in {"that", "to"}:
                return True
    return False


# Extract candidate Noun Phrases (NPs) from a sentence using NLTK RegexpParser
def extract_sentence_nps(sentence):
    if not sentence.tokens:
        return []

    pos_pairs = [(t.text, t.pos) for t in sentence.tokens]
    tree = NP_PARSER.parse(pos_pairs)

    nps = []
    tok_Cursor = 0

    for child in tree:
        if isinstance(child, nltk.Tree) and child.label() == "NP":
            length = len(child.leaves())
            np_tokens = sentence.tokens[tok_Cursor : tok_Cursor + length]
            head_tok = np_tokens[-1]
            head_lemma = head_tok.lemma.lower()

            if head_lemma not in STOP_ENTITIES and any(c.isalpha() for c in head_lemma):
                # Mark the head token with its canonical entity name
                head_tok.entity = head_lemma
                # Check if this NP is likely the grammatical subject (appears before main verb)
                is_subj = (tok_Cursor < 5) or (np_tokens[0].clause_id == head_tok.clause_id and tok_Cursor == 0)

                nps.append({
                    "head_lemma": head_lemma,
                    "head_token": head_tok,
                    "tokens": np_tokens,
                    "sent_id": sentence.sent_id,
                    "clause_id": head_tok.clause_id,
                    "start_idx": tok_Cursor,
                    "end_idx": tok_Cursor + length - 1,
                    "category": get_np_category(np_tokens, head_tok),
                    "is_subject": is_subj
                })
            tok_Cursor += length
        else:
            tok_Cursor += 1

    return nps


# Resolve pronouns across a 2-sentence window and weight salient topical entities
def apply_anaphora(sentences, top_k=5, boost=SALIENT_ENTITY_BOOST):
    all_nps_by_sent = []
    entity_counts = Counter()

    # Step 1: Extract NPs in every sentence and count entity mentions
    for sentence in sentences:
        sent_nps = extract_sentence_nps(sentence)
        all_nps_by_sent.append(sent_nps)
        for np_item in sent_nps:
            entity_counts[np_item["head_lemma"]] += 1

    # Step 2: Resolve third-person pronouns within a 2-sentence window
    for s_idx, sentence in enumerate(sentences):
        tokens = sentence.tokens
        for t_idx, token in enumerate(tokens):
            word_low = token.text.lower()
            if word_low not in ALL_TARGET_PRONOUNS:
                continue

            token.is_pronoun = True

            # Skip pleonastic/dummy "it"
            if is_pleonastic_it(tokens, t_idx):
                continue

            pron_cat = get_pronoun_category(word_low)
            is_reflexive = (word_low in REFLEXIVE_PRONOUNS)

            # Collect candidate NPs from current sentence and previous 2 sentences
            candidates = []
            start_sent = s_idx if is_reflexive else max(0, s_idx - 2)

            for cand_s_idx in range(start_sent, s_idx + 1):
                for np_item in all_nps_by_sent[cand_s_idx]:
                    # Antecedent must appear BEFORE the pronoun
                    if cand_s_idx == s_idx and np_item["end_idx"] >= t_idx:
                        continue

                    # Binding Theory Principle A: reflexive must be in the same sentence/clause
                    if is_reflexive and cand_s_idx != s_idx:
                        continue

                    # Binding Theory Principle B: non-reflexive object pronoun cannot bind
                    # to a non-subject NP immediately adjacent in the exact same clause
                    if not is_reflexive and cand_s_idx == s_idx:
                        if np_item["clause_id"] == token.clause_id and not np_item["is_subject"]:
                            if (t_idx - np_item["end_idx"]) <= 2:
                                continue

                    # Gender and number agreement check
                    if not check_agreement(pron_cat, np_item["category"]):
                        continue

                    candidates.append(np_item)

            # Score candidates by sentence distance, subject salience, and discourse frequency
            best_entity = ""
            best_score = -999.0

            for cand in candidates:
                sent_dist = s_idx - cand["sent_id"]
                score = 0.0
                # Prefer closer sentences (Hobbs recency)
                score -= sent_dist * 2.0
                # Prefer grammatical subjects (Hobbs left-to-right breadth-first subject preference)
                if cand["is_subject"]:
                    score += 2.5
                # Prefer frequent movie-domain entities
                score += min(3.0, entity_counts[cand["head_lemma"]] * 0.5)
                if cand["head_lemma"] in CORE_MOVIE_NOUNS:
                    score += 1.0

                if score > best_score:
                    best_score = score
                    best_entity = cand["head_lemma"]

            if best_entity:
                token.entity = best_entity
                entity_counts[best_entity] += 1

    # Step 3: Find top salient entities (discourse centers) in this review
    top_entities = {ent for ent, _ in entity_counts.most_common(top_k)}
    # Also include core movie entities that appeared at least twice
    for ent, count in entity_counts.items():
        if ent in CORE_MOVIE_NOUNS and count >= 2:
            top_entities.add(ent)

    # Step 4: Upweight sentiment tokens in clauses that mention a salient entity
    for sentence in sentences:
        salient_clauses = set()
        for token in sentence.tokens:
            if token.entity and token.entity in top_entities:
                salient_clauses.add(token.clause_id)

        for token in sentence.tokens:
            if token.prior_polarity != 0 and token.clause_id in salient_clauses:
                token.weight *= boost

    return sentences


# Extract document-level anaphora and entity salience features (M3)
def anaphora_features(sentences):
    tokens = flatten(sentences)

    total_words = max(
        1,
        sum(1 for t in tokens if any(c.isalnum() for c in t.text))
    )

    salient_pos = 0.0
    salient_neg = 0.0
    resolved_count = 0

    for t in tokens:
        if t.is_pronoun and t.entity != "":
            resolved_count += 1
        # Sentiment tokens that received the entity salience boost (weight > 1.0)
        if t.prior_polarity != 0 and t.weight > 1.0:
            weighted_val = t.shifted_polarity * t.weight
            if weighted_val > 0:
                salient_pos += weighted_val
            elif weighted_val < 0:
                salient_neg += abs(weighted_val)

    net_salient = salient_pos - salient_neg
    # Scale densities by 25.0 so they match the numeric range (0-3) of BoW word counts in Logistic Regression
    scale = 25.0

    return {
        "ana_salient_pos_density": (salient_pos / total_words) * scale,
        "ana_salient_neg_density": (salient_neg / total_words) * scale,
        "ana_salient_net_density": (net_salient / total_words) * scale,
        "ana_salient_pos_excess_density": (max(0.0, net_salient) / total_words) * scale,
        "ana_salient_neg_excess_density": (max(0.0, -net_salient) / total_words) * scale,
        "ana_resolved_pronoun_density": (resolved_count / total_words) * scale
    }
