#getting naiseo_makers frame from wordnet and listing all its lexical units _ids +dictionary definitions
def exercise_3_1(fn_corpus):
    # Look up the specific frame by its name
    noise_makers_frame = fn_corpus.frame("Noise_makers")

    print(f"Frame Name: {noise_makers_frame.name} (ID: {noise_makers_frame.ID})")
    print(f"Definition: {noise_makers_frame.definition}\n")

    # Access the dictionary of lexical units using the .lexUnit attribute
    lex_units = noise_makers_frame.lexUnit
    print(f"Total lexical units in '{noise_makers_frame.name}': {len(lex_units)}")
    print("Lexical Units in 'Noise_makers':")

    for lu_name in sorted(lex_units.keys()):
        lu_obj = lex_units[lu_name]
        print(f"  - {lu_name:<15} (ID: {lu_obj.ID}) | Definition: {lu_obj.definition}")

    return list(lex_units.keys())
