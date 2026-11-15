"""
propbank_and_verbnet.py
Handles Step 3 (Extracting verbs/predicates), Step 4 (Printing PropBank roles
and assigning them to the sentence's constituents from the parse tree),
and Step 5 (Extracting VerbNet frames and semantic representations).
"""

import nltk
from nltk.corpus import propbank, verbnet
from nltk.stem import WordNetLemmatizer


MONTHS = {
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december"
}


def step_3_extract_verbs(pos_tags):
    """
    Step 3: Extract the verbs/predicates in the sentence and lemmatize them.
    """
    lemmatizer = WordNetLemmatizer()
    verbs = []

    for i, (word, tag) in enumerate(pos_tags):
        is_sees = (word.lower() == "sees" and i > 0 and pos_tags[i - 1][1].startswith("NN"))
        if tag.startswith("VB") or is_sees:
            clean_word = word.lower().replace("’", "'")
            if clean_word in ("'s", "is", "are", "was", "were", "be", "been"):
                lemma = "be"
            else:
                lemma = lemmatizer.lemmatize(clean_word, "v")
            verbs.append((word, "VBZ" if is_sees else tag, lemma))

    print("\n3. Extracted Verbs / Predicates:")
    for word, tag, lemma in verbs:
        print(f"   Token: '{word}' (POS: {tag}) -> Lemma: '{lemma}'")

    return verbs


def step_4_propbank_roles(pos_tags, verbs):
    """
    Step 4: Print the PropBank roles defined in NLTK's PropBank corpus for each verb,
    and map the PropBank roles (ARG0, ARG1, ARG2, ARGM-*) to the sentence constituents
    using the parsed phrase structure and the verb's PropBank roleset.
    """
    print("\n4. PropBank Roles Assigned to Main Verbs / Predicates:")
    seen_lemmas = []

    for word, tag, lemma in verbs:
        if lemma in seen_lemmas:
            continue
        seen_lemmas.append(lemma)

        try:
            rolesets = propbank.rolesets(lemma)
        except ValueError:
            print(f"   Verb '{lemma}': No PropBank roleset found.")
            continue

        print(f"   PropBank Frameset for '{lemma}' ({len(rolesets)} roleset(s)):")
        for rs in rolesets:
            rs_id = rs.attrib.get("id", "")
            rs_name = rs.attrib.get("name", "")
            print(f"     Roleset [{rs_id}] ({rs_name}):")
            for role in rs.findall("roles/role"):
                print(f"       ARG{role.attrib['n']}: {role.attrib['descr']}")

    # Algorithmically assign roles to the main verbs in the sentence from the parse chunks
    assigned_roles = assign_roles_from_chunks(pos_tags)
    print("\n   Assigned PropBank Roles in Sentence:")
    for item in assigned_roles:
        print(f"     Predicate: '{item['predicate']}' (Roleset: {item['roleset']})")
        for role_label, span_text in item["roles"]:
            print(f"       {role_label:<10}: {span_text}")

    return assigned_roles


def _build_srl_chunks(pos_tags):
    """
    Helper that chunks the POS-tagged sentence into TMP, NP, PP, and VP constituents
    and attaches 'of'-PPs to their head NPs for argument boundary identification.
    """
    tagged = []
    for i, (w, t) in enumerate(pos_tags):
        if w.lower() == "sees" and i > 0 and pos_tags[i - 1][1].startswith("NN"):
            t = "VBZ"
        elif t == "NNP" and w.lower() in MONTHS:
            t = "MONTH"
        elif w.lower() in ("but", "that", "whether", "as") and t in ("CC", "IN"):
            t = "SCONJ"
        tagged.append((w, t))

    grammar = r"""
        TMP: {<IN>?<DT|JJ>*<MONTH>}
             {<IN><CD><CC><CD><NN.*>+}
             {<CD>}
        NP: {<DT|PRP\$|JJ.*>*<NN.*>+}
            {<DT><JJS>}
            {<PRP>}
            {<DT><IN><WDT>}
            {<WP|WDT>}
        NP: {<NP><CC><NP>}
        NP: {<NP><CC><NP>}
        PP: {<IN|TO><NP>}
        VP: {<MD>?<VB.*>?<RB.*>*<VB.*><RP>?}
    """
    tree = nltk.RegexpParser(grammar).parse(tagged)
    merged = []
    for ch in tree:
        if isinstance(ch, nltk.Tree) and ch.label() == "PP":
            if ch.leaves()[0][0].lower() == "of" and merged and isinstance(merged[-1], nltk.Tree) and merged[-1].label() in ("NP", "PP"):
                prev = merged.pop()
                merged.append(nltk.Tree(prev.label(), list(prev) + list(ch)))
                continue
        merged.append(ch)
    return merged


def assign_roles_from_chunks(pos_tags):
    """
    Walks each VP constituent in the parsed sentence, looks up its head verb's
    primary PropBank roleset, and assigns ARG0, ARG1, ARG2, and ARGM-* to the
    surrounding syntactic chunks.
    """
    lemmatizer = WordNetLemmatizer()
    chunks = _build_srl_chunks(pos_tags)
    results = []

    for idx, ch in enumerate(chunks):
        if not (isinstance(ch, nltk.Tree) and ch.label() == "VP"):
            continue
        leaves = ch.leaves()
        v_tokens = [(w, t) for w, t in leaves if t.startswith("VB")]
        if not v_tokens:
            continue

        verb_word, verb_tag = v_tokens[-1]
        has_be_aux = any(w.lower() in ("'s", "is", "are", "was", "were", "be", "been") for w, _ in leaves[:-1])
        is_passive = has_be_aux and verb_tag == "VBN"
        lemma = "be" if verb_word.lower() in ("'s", "is", "are") else lemmatizer.lemmatize(verb_word.lower(), "v")

        rs = propbank.rolesets(lemma)[0]
        rs_id = rs.attrib["id"]
        role_map = {r.attrib["n"]: r.attrib["descr"] for r in rs.findall("roles/role")}
        roles = []

        for w, t in leaves:
            if t == "MD":
                roles.append(("ARGM-MOD", w))
            elif t.startswith("RB"):
                roles.append(("ARGM-ADV", w))

        # Find pre-verbal subject (ARG0, or ARG1 if passive/copula) and temporal modifier
        subj_found = False
        for left_i in range(idx - 1, -1, -1):
            lch = chunks[left_i]
            if isinstance(lch, nltk.Tree):
                lbl = lch.label()
                txt = " ".join(w for w, _ in lch.leaves())
                if lbl == "TMP":
                    roles.insert(0, ("ARGM-TMP", txt))
                elif lbl in ("NP", "PP") and not subj_found:
                    if lbl == "PP" and lemma != "be":
                        np_subs = [s for s in lch if isinstance(s, nltk.Tree) and s.label() == "NP"]
                        if np_subs:
                            txt = " ".join(w for w, _ in np_subs[-1].leaves())
                    subj_role = "ARG1" if (is_passive or "0" not in role_map) else "ARG0"
                    roles.insert(0, (subj_role, txt))
                    subj_found = True
            elif lch[0] in (",", ";") or (lch[1] == "SCONJ" and subj_found):
                break

        # Find post-verbal objects and complements (ARG1, ARG2, ARGM-LOC, ARGM-TMP)
        next_arg = "ARG2" if (is_passive or "0" not in role_map) else "ARG1"
        right_parts = []
        for right_i in range(idx + 1, len(chunks)):
            rch = chunks[right_i]
            if isinstance(rch, nltk.Tree):
                lbl = rch.label()
                txt = " ".join(w for w, _ in rch.leaves())
                if lbl == "TMP":
                    roles.append(("ARGM-TMP", txt))
                elif lbl in ("NP", "PP"):
                    if lbl == "PP" and rch.leaves()[0][0].lower() == "at":
                        roles.append(("ARGM-LOC", txt))
                    else:
                        right_parts.append((lbl, txt))
                elif lbl == "VP":
                    break
            else:
                if rch[1].startswith("JJ"):
                    right_parts.append(("JJ", rch[0]))
                elif (rch[1] == "SCONJ" or rch[0] == "to") and not right_parts:
                    clause_words = []
                    for k in range(right_i, len(chunks)):
                        nk = chunks[k]
                        if not isinstance(nk, nltk.Tree) and nk[0] in (".", ","):
                            break
                        clause_words.extend([w for w, _ in nk.leaves()] if isinstance(nk, nltk.Tree) else [nk[0]])
                    right_parts.append(("CLAUSE", " ".join(clause_words)))
                    break
                elif rch[0] in (",", ".", ";") or rch[1] == "SCONJ":
                    break

        if len(right_parts) == 1:
            roles.append((next_arg, right_parts[0][1]))
        elif len(right_parts) >= 2:
            if right_parts[0][0] == "PP" and right_parts[1][0] == "NP" and "2" in role_map:
                roles.append(("ARG2", right_parts[0][1]))
                roles.append(("ARG1", right_parts[1][1]))
            elif right_parts[0][0] == "NP" and right_parts[1][0] == "PP" and "2" in role_map:
                roles.append(("ARG1", right_parts[0][1]))
                roles.append(("ARG2", right_parts[1][1]))
            elif right_parts[0][0] == "NP" and right_parts[1][0] == "NP":
                roles.append((next_arg, right_parts[0][1]))
            else:
                roles.append((next_arg, " ".join(p[1] for p in right_parts)))

        results.append({"predicate": verb_word, "roleset": rs_id, "roles": roles})
    return results


def step_5_verbnet_frames(verbs):
    """
    Step 5: Extract VerbNet frames and semantic representations of each verb
    using verbnet.classids() and verbnet.pprint_frames().
    """
    print("\n5. VerbNet Frames and Semantic Representations:")
    seen_lemmas = []

    for word, tag, lemma in verbs:
        if lemma in seen_lemmas:
            continue
        seen_lemmas.append(lemma)

        class_ids = verbnet.classids(lemma=lemma)
        if not class_ids:
            print(f"   Verb Lemma: '{lemma}' -> No VerbNet classes found.")
            continue

        print(f"   Verb Lemma: '{lemma}' -> VerbNet Classes: {class_ids}")
        for cid in class_ids:
            print(f"     --- VerbNet Class: {cid} ---")
            print(verbnet.pprint_frames(cid, indent="       "))
