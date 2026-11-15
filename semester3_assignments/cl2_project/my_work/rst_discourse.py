# Module for Rule-Based Rhetorical Structure Theory (RST) EDU Segmentation and Weighting (Model M4)
# Segments sentences into Elementary Discourse Units (EDUs) and weights Nucleus vs. Satellite clauses

from preprocess import flatten

# Approximately 45 explicit discourse connectives grouped by rhetorical relation
RST_CONNECTIVES = {
    "Concession": [
        "even though", "in spite of", "regardless of", "even if",
        "although", "though", "despite", "whereas", "while",
        "albeit", "admittedly", "granted"
    ],
    "Contrast": [
        "on the other hand", "in contrast", "on the contrary",
        "but", "however", "yet", "nevertheless", "nonetheless",
        "conversely", "instead", "rather", "still", "alternatively"
    ],
    "Result": [
        "as a result", "for this reason", "as a consequence", "so that",
        "therefore", "thus", "hence", "consequently", "accordingly"
    ],
    "Cause": [
        "due to", "owing to", "because of",
        "because", "since", "as"
    ],
    "Condition": [
        "provided that", "providing that", "as long as", "so long as",
        "on condition that", "in case", "assuming that",
        "if", "unless", "suppose"
    ]
}

# Weights for RST Nucleus (author's core claim) vs. Satellite (conceded/background clause)
NUCLEUS_WEIGHT = 1.5
SATELLITE_WEIGHT = 0.5
CONTRAST_PRE_SATELLITE_WEIGHT = 0.6
CAUSE_SATELLITE_WEIGHT = 0.75


# Disambiguate polysemous discourse markers ("while", "since", "as") using POS tags
def is_valid_discourse_connective(tokens, idx, marker_word, relation):
    # "while" followed by a gerund (VBG, e.g. "while watching") or noun is Temporal, not Concession
    if marker_word == "while" and relation == "Concession":
        if idx + 1 < len(tokens):
            next_pos = tokens[idx + 1].pos
            if next_pos == "VBG":
                return False
        # Check if there is a finite verb (VB, VBD, VBP, VBZ) in the next 6 tokens
        has_finite_verb = False
        for look_tok in tokens[idx + 1 : idx + 7]:
            if look_tok.text in {",", ";", ".", "!"}:
                break
            if look_tok.pos in {"VBD", "VBP", "VBZ", "MD"}:
                has_finite_verb = True
                break
        return has_finite_verb

    # "since" or "as" is only causal when followed by a clause with a verb (not "since 1995" or "as a hero")
    if marker_word in {"since", "as"} and relation == "Cause":
        if idx + 1 < len(tokens) and tokens[idx + 1].pos == "CD":
            return False
        has_verb = False
        for look_tok in tokens[idx + 1 : idx + 6]:
            if look_tok.text in {",", ";", ".", "!"}:
                break
            if look_tok.pos.startswith("VB") or look_tok.pos == "MD":
                has_verb = True
                break
        return has_verb

    return True


# Find if a connective starts at token position `idx` in the sentence
def match_connective_at(tokens, idx):
    n = len(tokens)

    for relation, phrases in RST_CONNECTIVES.items():
        for phrase in phrases:
            parts = phrase.split()
            k = len(parts)
            if idx + k > n:
                continue

            # Match each word in the connective phrase
            matched = True
            for offset in range(k):
                if tokens[idx + offset].text.lower() != parts[offset]:
                    matched = False
                    break

            if matched:
                if is_valid_discourse_connective(tokens, idx, phrase, relation):
                    return relation, phrase, k

    return None, None, 0


# Segment a sentence into Elementary Discourse Units (EDUs) and detect rhetorical relations
def segment_sentence_edus(sentence):
    tokens = sentence.tokens
    if not tokens:
        return []

    edu_id = 0
    edu_relations = {0: None}
    i = 0
    n = len(tokens)

    while i < n:
        tok = tokens[i]
        rel, phrase, span_len = match_connective_at(tokens, i)

        # Start a new EDU (or label the fresh EDU after a comma) if a connective appears
        if rel is not None and i > 0 and len([t for t in tokens[:i] if any(c.isalnum() for c in t.text)]) >= 2:
            if edu_relations.get(edu_id) is not None or any(t.edu_id == edu_id for t in tokens[:i]):
                edu_id += 1
            edu_relations[edu_id] = rel
        elif rel is not None and i == 0:
            edu_relations[edu_id] = rel

        # Assign edu_id to the connective tokens
        if span_len > 1:
            for offset in range(span_len):
                tokens[i + offset].edu_id = edu_id
            i += span_len
            continue

        tok.edu_id = edu_id

        # Punctuation boundary (",", ";", ":", "--") splits into a new EDU if enough words preceded it
        if tok.text in {",", ";", ":", "--"} and i < n - 2:
            edu_id += 1
            if edu_id not in edu_relations:
                edu_relations[edu_id] = None

        i += 1

    # Group tokens by edu_id
    edus = []
    for eid in sorted(edu_relations.keys()):
        edu_tokens = [t for t in tokens if t.edu_id == eid]
        if edu_tokens:
            edus.append({
                "edu_id": eid,
                "relation": edu_relations[eid],
                "tokens": edu_tokens,
                "role": "Neutral",
                "rst_weight": 1.0
            })

    return edus


# Assign Nucleus vs. Satellite weights to EDUs in each sentence (M4)
def apply_rst(sentences, nucleus_w=NUCLEUS_WEIGHT, satellite_w=SATELLITE_WEIGHT):
    for sentence in sentences:
        edus = segment_sentence_edus(sentence)
        num_edus = len(edus)

        for idx, edu in enumerate(edus):
            rel = edu["relation"]

            # Rule 1: Concession ("although", "though", "despite", "while") -> this EDU is Satellite,
            # and the adjacent main-clause EDU is the Nucleus
            if rel == "Concession":
                edu["role"] = "Satellite"
                edu["rst_weight"] = satellite_w
                if idx == 0 and num_edus > 1:
                    edus[idx + 1]["role"] = "Nucleus"
                    edus[idx + 1]["rst_weight"] = nucleus_w
                elif idx > 0 and edus[idx - 1]["role"] == "Neutral":
                    edus[idx - 1]["role"] = "Nucleus"
                    edus[idx - 1]["rst_weight"] = nucleus_w

            # Rule 2: Contrast ("but", "however", "yet", "nevertheless") -> this EDU is the Nucleus,
            # and any preceding setup clause in the same sentence is downweighted as Satellite
            elif rel == "Contrast":
                edu["role"] = "Nucleus"
                edu["rst_weight"] = nucleus_w
                if idx > 0 and edus[idx - 1]["role"] == "Neutral":
                    edus[idx - 1]["role"] = "Satellite"
                    edus[idx - 1]["rst_weight"] = CONTRAST_PRE_SATELLITE_WEIGHT

            # Rule 3: Result ("therefore", "thus", "consequently", "hence") -> conclusion is Nucleus
            elif rel == "Result":
                edu["role"] = "Nucleus"
                edu["rst_weight"] = nucleus_w

            # Rule 4: Condition ("if", "unless", "provided that") -> hypothetical clause is Satellite
            elif rel == "Condition":
                edu["role"] = "Satellite"
                edu["rst_weight"] = satellite_w
                if idx == 0 and num_edus > 1 and edus[idx + 1]["role"] == "Neutral":
                    edus[idx + 1]["role"] = "Nucleus"
                    edus[idx + 1]["rst_weight"] = 1.25

            # Rule 5: Cause ("because", "since", "due to") -> reason is Satellite, claim is Nucleus
            elif rel == "Cause":
                edu["role"] = "Satellite"
                edu["rst_weight"] = CAUSE_SATELLITE_WEIGHT
                if idx > 0 and edus[idx - 1]["role"] == "Neutral":
                    edus[idx - 1]["role"] = "Nucleus"
                    edus[idx - 1]["rst_weight"] = 1.3
                elif idx == 0 and num_edus > 1 and edus[idx + 1]["role"] == "Neutral":
                    edus[idx + 1]["role"] = "Nucleus"
                    edus[idx + 1]["rst_weight"] = 1.3

        # Multiply each token's weight by its EDU's RST weight and store role on token
        for edu in edus:
            for tok in edu["tokens"]:
                tok.weight *= edu["rst_weight"]
                tok.rst_role = edu["role"]

    return sentences


# Compute document-level RST discourse features (M4)
def rst_features(sentences):
    tokens = flatten(sentences)

    total_words = max(
        1,
        sum(1 for t in tokens if any(c.isalnum() for c in t.text))
    )

    nuc_pos = 0.0
    nuc_neg = 0.0
    sat_pos = 0.0
    sat_neg = 0.0
    weighted_pos = 0.0
    weighted_neg = 0.0

    for t in tokens:
        if t.prior_polarity == 0:
            continue

        role = getattr(t, "rst_role", "Neutral")
        val = t.shifted_polarity
        w_val = t.shifted_polarity * t.weight

        if w_val > 0:
            weighted_pos += w_val
        elif w_val < 0:
            weighted_neg += abs(w_val)

        if role == "Nucleus":
            if val > 0:
                nuc_pos += val
            elif val < 0:
                nuc_neg += abs(val)
        elif role == "Satellite":
            if val > 0:
                sat_pos += val
            elif val < 0:
                sat_neg += abs(val)

    net_weighted = weighted_pos - weighted_neg
    net_nucleus = nuc_pos - nuc_neg
    # Scale densities by 25.0 so they match the numeric range (0-3) of BoW word counts in Logistic Regression
    scale = 25.0

    return {
        "rst_nucleus_pos_density": (nuc_pos / total_words) * scale,
        "rst_nucleus_neg_density": (nuc_neg / total_words) * scale,
        "rst_satellite_pos_density": (sat_pos / total_words) * scale,
        "rst_satellite_neg_density": (sat_neg / total_words) * scale,
        "rst_weighted_pos_density": (weighted_pos / total_words) * scale,
        "rst_weighted_neg_density": (weighted_neg / total_words) * scale,
        "rst_weighted_polarity_density": (net_weighted / total_words) * scale,
        "rst_weighted_pos_excess_density": (max(0.0, net_weighted) / total_words) * scale,
        "rst_weighted_neg_excess_density": (max(0.0, -net_weighted) / total_words) * scale,
        "rst_nucleus_pos_excess_density": (max(0.0, net_nucleus) / total_words) * scale,
        "rst_nucleus_neg_excess_density": (max(0.0, -net_nucleus) / total_words) * scale
    }
