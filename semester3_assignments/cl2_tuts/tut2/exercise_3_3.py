#lexical unit lookup examples 
def show_lu_lookup_examples(fn_corpus):
    absorb_lus = fn_corpus.lus(r"absorb\.v")
    spin_lus = fn_corpus.lus(r"spin\.v")
    sample_lu = fn_corpus.lu(14833)

    print("Handout example lookups:")
    print(f"  fn.lus(r'absorb\\.v') -> {absorb_lus}")
    print(f"  fn.lus(r'spin\\.v')   -> Found {len(spin_lus)} lexical units: {spin_lus}")
    print(
        f"  fn.lu(14833)         -> Name: {sample_lu.name}, "
        f"Frame: {sample_lu.frame.name}, Definition: {sample_lu.definition}\n"
    )

#counting diff lexical units each verb occurs in and frames it evokes
def count_verb_polysemy(fn_corpus):
    verb_lu_counts = {}
    verb_frames = {}

    for lu in fn_corpus.lus():
        # In FrameNet, verb lexical units end with the '.v' suffix
        if lu.name.endswith(".v"):
            verb_name = lu.name
            verb_lu_counts[verb_name] = verb_lu_counts.get(verb_name, 0) + 1

            if verb_name not in verb_frames:
                verb_frames[verb_name] = []
            verb_frames[verb_name].append((lu.ID, lu.frame.name))

    return verb_lu_counts, verb_frames

#most polysemous verbs
def exercise_3_3(fn_corpus):
    show_lu_lookup_examples(fn_corpus)
    verb_lu_counts, verb_frames = count_verb_polysemy(fn_corpus)

    # Find the maximum number of lexical units any verb appears in
    max_count = 0
    for verb_name in verb_lu_counts:
        if verb_lu_counts[verb_name] > max_count:
            max_count = verb_lu_counts[verb_name]

    # Collect all verbs that achieve this maximum count
    most_polysemous = []
    for verb_name in sorted(verb_lu_counts.keys()):
        if verb_lu_counts[verb_name] == max_count:
            most_polysemous.append(verb_name)

    print(f"Maximum lexical units for a single verb: {max_count}")
    print(f"Most polysemous verbs ({len(most_polysemous)} verbs tied at {max_count} LUs):")

    for verb_name in most_polysemous:
        print(f"\n  Verb: {verb_name} (occurs in {max_count} lexical units):")
        for lu_id, frame_name in sorted(verb_frames[verb_name]):
            print(f"    - LU ID: {lu_id:<6} | Frame: {frame_name}")

    # Also show the runner-up verbs (occurring in 8 lexical units) for completeness
    print("\nRunner-up polysemous verbs (occurring in 8 lexical units):")
    for verb_name in sorted(verb_lu_counts.keys()):
        if verb_lu_counts[verb_name] == 8:
            print(f"  - {verb_name} (8 lexical units)")

    return most_polysemous
