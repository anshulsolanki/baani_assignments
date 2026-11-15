"""
pos_and_parse.py
Handles Step 1 (POS tagging using the NLTK tagger) and
Step 2 (Parsing the sentence using an NLTK parser and visualizing the parse tree).
"""

import nltk


def step_1_pos_tag(sentence):
    """
    Step 1: Tokenize the sentence and assign POS tags using NLTK's tagger.
    """
    clean_sentence = sentence.replace("’", "'")
    tokens = nltk.word_tokenize(clean_sentence)
    pos_tags = nltk.pos_tag(tokens)

    print("1. POS Tags (NLTK Tagger):")
    print("  ", pos_tags)
    return pos_tags


def step_2_parse_sentence(pos_tags):
    """
    Step 2: Parse the POS-tagged sentence using an NLTK RegexpParser
    and visualize the parse tree using tree.pretty_print().
    """
    # Fix NLTK tagger's ambiguity where 'sees' after a singular noun is tagged NNS
    parser_tags = []
    for i, (word, tag) in enumerate(pos_tags):
        if word.lower() == "sees" and i > 0 and pos_tags[i - 1][1].startswith("NN"):
            parser_tags.append((word, "VBZ"))
        else:
            parser_tags.append((word, tag))

    grammar = r"""
        NP: {<DT|PRP\$|JJ.*>*<NN.*>+}
            {<DT><JJS>}
            {<CD><CC><CD><NN.*>+}
            {<PRP>}
            {<DT><IN><WDT>}
            {<WP|WDT>}
        NP: {<NP><CC><NP>}
        NP: {<NP><CC><NP>}
        PP: {<IN|TO><NP>}
        VP: {<MD>?<VB.*>?<RB.*>*<VB.*><RP>?}
    """

    parser = nltk.RegexpParser(grammar)
    parse_tree = parser.parse(parser_tags)

    print("\n2. Parse Tree & Visualization:")
    parse_tree.pretty_print()
    return parse_tree
