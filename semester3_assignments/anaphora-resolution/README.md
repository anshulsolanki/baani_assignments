to run:
source .venv/bin/activate
python anaphora_resolution.py

assumptions:
1. cataphora aren't counted
2. using nltk.RegexpParser and nltk.tree.ParentedTree to generate standard CFG trees and not penn treebank parser
3. defualting to neutrl/unknown when gender not known


load_gap_tsv(path): Reads the GAP TSV files (gap-train.tsv, gap-validation.tsv, gap-test.tsv) using the standard csv module. Converts offsets to integers and coreference flags to booleans.

gender_of_pronoun(pronoun): Maps pronouns (he, his, him, she, her, hers) to a standard 'male' or 'female' label.

Problem 1

build_cfg_parser(): Builds the regex chunk parser (RegexpParser) that groups noun phrases and prepositional phrases into valid CFG chunk trees.

extract_candidate_nps_from_text(text, target_pronoun_offset): Tokenizes the text into sentences and POS tagged words, generates chunk trees, and finds all candidate NPs that end before target_pronoun_offset. Returns character spans, sentence indices and head tokens.

matches_entity(candidate_text, entity_text): Checks whether a candidate NP span matches named entity A or B using case-insensitive substring matching.

Problem 2 & 3

problem_2(test_data): Runs 100 trials of random antecedent assignment on both the full candidate NP pool and the binary A/B choice, then calculates the average accuracy.

problem_3(test_data): Selects the candidate NP with the highest character offset before the pronoun and calculates accuracy.

Hobbs' Algorithm (Problem 7)

build_sentence_trees(text): Creates an nltk.tree.ParentedTree for each sentence in the discourse segment.

find_pronoun_node(trees, pronoun_text): Finds the target pronoun's leaf node in the list of parented sentence trees.

hobbs_algorithm(trees, pronoun_node, gender): Implements Hobbs' 9-step search:
  Step 1: Finds the first NP above the pronoun.
  Steps 2-3: Traverses left to right through intermediate S/NP nodes.
  Steps 4-9: Moves up through clause roots and searches previous sentences in reverse order using breadth-first traversal. Returns candidate NPs in the order they are found.

Problem 4 & 5

extract_features(cand, segment, all_cands, hobbs_order): Calculates the 12 dimensional feature vector for a candidate NP.

CustomLogisticRegression:

__init__(learning_rate, l2_reg, epochs, pos_weight): Intializes the model parameters and weights.
  sigmoid(z): Calculates the numerically stable sigmoid function, 1 / (1 + exp(-z)).

 fit(X, y): Trains the weights using batch gradient descent with L2 regularization.

predict_proba(X): Returns the predicted coreference probabilities.


evaluate_lr_model(model, data): Calculates precision, recall and F1 on both the full candidate NP pool and the GAP A/B subset.

problem_4(...): Performs grid search using the validation set and evaluates the best model on the test set.

problem_5(model): Prints the feature weights in sorted order and shows the top 5 features with explanations.

Problem 6 & 8

problem_6(model, test_data): Identifies false positive and false negative predictions, prints the total number of errors and some examples to the console, and refers to the full analysis in Report.pdf.

problem_8(rand_acc, rec_acc, hobbs_f1, lr_f1): Generates a comparison table summarising all the approaches.

save_parse_trees_txt(data, out_path): Saves ASCII versions of the CFG trees for the first 5 test segments, with numbered NP chunk annotations, to parse_trees.txt.

convert_trees_txt_to_pdf(txt_path): Converts parse_trees.txt into parse_trees.pdf using macOS cupsfilter.