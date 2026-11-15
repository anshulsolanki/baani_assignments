from synonyms import nltk_get_synonyms
from wordnet_questions import (get_all_noun_forms,question_1,question_2,question_3,question_4)

def main():
    print("============================================================")
    print("CL-2 Tutorial 1: WordNet Activity")
    print("============================================================\n")

    # Part 1: Test the synonym retrieval procedure on ('dog', 'n')
    print("=== Procedure Test: nltk_get_synonyms('dog', 'n') ===")
    dog_synonyms = nltk_get_synonyms('dog', 'n')
    print(dog_synonyms)
    print(f"Total unique synonyms returned for ('dog', 'n'): {len(dog_synonyms)}")

    # Verify against the handout's expected set of 22 strings
    expected_dog_synonyms = ['dog', 'Canis familiaris', 'domestic dog', 'frump', 'hound','bounder', 'blackguard', 'cad', 'heel', 'wiener', 'frankfurter','hot dog', 'wienerwurst', 'frank', 'weenie', 'hotdog', 'pawl','click', 'detent', 'andiron', 'firedog', 'dog-iron']
    matches_expected = (set(dog_synonyms) == set(expected_dog_synonyms)and len(dog_synonyms) == len(expected_dog_synonyms))
    print(f"Matches expected handout set (no duplicates, exact strings): {matches_expected}\n")

    # Precompute the set of all noun forms once using the handout's snippet
    print("Computing all WordNet noun forms...")
    all_noun_forms = get_all_noun_forms()
    print("Done.\n")

    # Question 1
    print("=== Question 1: How many nouns are there in WordNet? ===")
    count_synsets, count_index = question_1(all_noun_forms)
    print(f"Number of unique noun forms (via handout snippet / synset lemmas): {count_synsets}")
    print(f"Number of unique lowercase noun lemmas (via wn.all_lemma_names('n')): {count_index}\n")

    # Question 2
    print("=== Question 2: How many noun synsets are there? ===")
    num_noun_synsets = question_2()
    print(f"Number of noun synsets: {num_noun_synsets}\n")

    # Question 3
    print("=== Question 3: What noun has the largest number of senses? ===")
    best_all_nouns, max_all_senses = question_3(all_noun_forms)
    print(f"Noun(s) with largest total senses (across all POS): {best_all_nouns}")
    print(f"Total number of senses (synsets): {max_all_senses}\n")

    # Question 4
    print("=== Question 4: What noun has the largest number of noun senses? ===")
    best_noun_nouns, max_noun_senses = question_4(all_noun_forms)
    print(f"Noun(s) with largest number of noun senses (POS='n'): {best_noun_nouns}")
    print(f"Number of noun senses (noun synsets): {max_noun_senses}\n")


if __name__ == "__main__":
    main()
