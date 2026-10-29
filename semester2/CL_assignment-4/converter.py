import sys
import json

def map_relation(paninian_tag):
    """
    Maps a single Paninian dependency tag to a UD tag.
    Returns 'dep' as a fallback for unknown/unmapped tags.
    """
    # Standard Paninian to UD mapping logic
    mapping_dict = {
        'k1': 'nsubj',  # Karta (Agent/Subject)
        'k2': 'obj',  # Karma (Patient/Object)
        'k3': 'obl:inst',  # Karana (Instrument)
        'k4': 'iobj',  # Sampradana (Beneficiary/Recipient)
        'k5': 'obl',  # Apadana (Source)
        'k6': 'nmod:poss',  # Sambandha (Genitive/Possessor)
        'k7': 'obl',  # Adhikarana (General Location/Time)
        'k7p': 'obl:loc',  # Adhikarana (Place)
        'k7t': 'obl:tmod',  # Adhikarana (Time)
        'r6': 'nmod',  # Relational modifier
        'ccof': 'conj',  # Co-ordination
        'vmod': 'advmod',  # Verb modifier
        'nmod': 'nmod',  # Noun modifier
        'jjmod': 'amod',  # Adjective modifier
        'pof': 'compound:lvc',  # Part of complex predicate
        'root': 'root',  # Root node
        'main': 'root',  # Main verb
        'rs': 'advcl', # Adverbial clause complement (Suggestion)
        'rt': 'obl', # Purpose (Suggestion)
        'pk1': 'nsubj', # Prayojaka Karta / Causer (Suggestion)
    }
    # Clean the input tag to handle potential casing/spacing edge cases
    clean_tag = str(paninian_tag).strip().lower()
    # Return the mapped UD tag, falling back to 'dep' as instructed
    return mapping_dict.get(clean_tag, 'dep')

def process_file(input_path, output_path):
    """
    Reads the input JSON, applies the mapping, and writes to output JSON.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        tree_data = json.load(f)
    
    for node in tree_data:
        # Extract the Paninian tag and find the UD equivalent
        p_tag = node.get('paninian_relation', '')
        node['ud_relation'] = map_relation(p_tag)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(tree_data, f, indent=4)

if __name__ == "__main__":
    # Do NOT modify this execution block
    if len(sys.argv) != 3:
        print("Usage: python converter.py <input.json> <output.json>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    process_file(input_file, output_file)
