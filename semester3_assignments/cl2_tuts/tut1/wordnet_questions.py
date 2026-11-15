from nltk.corpus import wordnet as wn

#set of all unique noun forms in wordnet
def get_all_noun_forms():
    all_noun_forms = set()
    for synset in wn.all_synsets('n'):
        for l in synset.lemmas():
            all_noun_forms.add(l.name())
    return all_noun_forms

def question_1(all_noun_forms=None):
    if all_noun_forms is None:
        all_noun_forms = get_all_noun_forms()

    count_from_synsets = len(all_noun_forms)
    count_from_index = len(list(wn.all_lemma_names('n')))

    return count_from_synsets, count_from_index

def question_2():
    noun_synsets = list(wn.all_synsets('n'))
    return len(noun_synsets)

def question_3(all_noun_forms=None):
    if all_noun_forms is None:
        all_noun_forms = get_all_noun_forms()

    max_senses = 0
    best_nouns = []

    for noun in sorted(all_noun_forms):
        # wn.synsets(noun) without a POS filter returns senses across all POS tags
        num_senses = len(wn.synsets(noun))
        if num_senses > max_senses:
            max_senses = num_senses
            best_nouns = [noun]
        elif num_senses == max_senses:
            best_nouns.append(noun)

    return best_nouns, max_senses

def question_4(all_noun_forms=None):
    if all_noun_forms is None:
        all_noun_forms = get_all_noun_forms()

    max_noun_senses = 0
    best_nouns = []

    for noun in sorted(all_noun_forms):
        # Restrict synset lookup strictly to nouns ('n')
        num_noun_senses = len(wn.synsets(noun, 'n'))
        if num_noun_senses > max_noun_senses:
            max_noun_senses = num_noun_senses
            best_nouns = [noun]
        elif num_noun_senses == max_noun_senses:
            best_nouns.append(noun)

    return best_nouns, max_noun_senses
