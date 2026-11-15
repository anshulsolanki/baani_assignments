"""
main.py
Main script for the NLTK PropBank and VerbNet Activity (CL-2 Tutorial 3).
Runs the 6 required operations sequentially on each of the 10 given sentences.
"""

import os
import nltk
from pos_and_parse import step_1_pos_tag, step_2_parse_sentence
from propbank_and_verbnet import (
    step_3_extract_verbs,
    step_4_propbank_roles,
    step_5_verbnet_frames,
)
from brat_roles import step_6_brat_annotation


# The 10 sentences given in the assignment handout
SENTENCES = [
    "Senators and a good teacher believes in the possibilities of every boy and girl.",
    "The good teacher sees what is possible.",
    "A good teacher believes in the responsibility of every school to bring out the best in every student, and 2001, we passed what’s called the No Child Left Behind legislation.",
    "Education reform depends on good laws and good plans but you and I know it ultimately depends on good teachers.",
    "Last June states submitted to the department of education strategies for ensuring that all teachers are highly qualified.",
    "Inherent in the law is the vision of high standards, and money to meet the standards.",
    "All of which put the education decisions of America in the hands of teachers and principals and local officials.",
    "But we also said that as we seek excellence for every child, we must design accountability systems at the state level to determine whether or not each child is learning.",
    "By this September, states will assess the programs they expect to make by 2005 and 2006 school year.",
    "People are responding to the challenge at the local level.",
]


def ensure_nltk_data():
    """Ensure required NLTK data packages are available locally."""
    required = [
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("taggers/averaged_perceptron_tagger_eng", "averaged_perceptron_tagger_eng"),
        ("corpora/wordnet.zip", "wordnet"),
        ("corpora/propbank.zip", "propbank"),
        ("corpora/verbnet.zip", "verbnet"),
    ]
    for path, pkg in required:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(pkg, quiet=True)


def main():
    ensure_nltk_data()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    brat_dir = os.path.join(base_dir, "brat_annotations")

    for i in range(len(SENTENCES)):
        sent_num = i + 1
        sentence = SENTENCES[i]

        print("=" * 80)
        print(f"SENTENCE {sent_num}: {sentence}")
        print("=" * 80)

        # 1. POS tag using the NLTK tagger
        pos_tags = step_1_pos_tag(sentence)

        # 2. Parse the sentence using an NLTK parser and visualize the parse tree
        step_2_parse_sentence(pos_tags)

        # 3. Extract the verbs/predicates in the sentence
        verbs = step_3_extract_verbs(pos_tags)

        # 4. Print the PropBank roles assigned to the main verbs/predicates
        assigned_roles = step_4_propbank_roles(pos_tags, verbs)

        # 5. Extract VerbNet frames and semantic representations of this verb
        step_5_verbnet_frames(verbs)

        # 6. Use BRAT to annotate its semantic roles (ARG0, ARG1, etc.)
        step_6_brat_annotation(sent_num, sentence, assigned_roles, brat_dir)
        print()


if __name__ == "__main__":
    main()
