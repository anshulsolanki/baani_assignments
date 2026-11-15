from nltk.corpus import wordnet as wn

#getting synonyms using wordnet
def nltk_get_synonyms(form, pos=None):
    # Convert spaces to underscores for lookup in case a multi-word string is passed
    lookup_form = form.replace(' ', '_')

    # Retrieve all synsets matching the word form and part of speech
    if pos is not None:
        synsets = wn.synsets(lookup_form, pos=pos)
    else:
        synsets = wn.synsets(lookup_form)

    synonyms = []

    # Loop through each synset and extract the string name of every lemma
    for synset in synsets:
        for lemma in synset.lemmas():
            # Convert WordNet's internal underscore representation back to spaces
            word_form = lemma.name().replace('_', ' ')

            # Check before appending to guarantee there are no duplicates
            if word_form not in synonyms:
                synonyms.append(word_form)

    return synonyms
