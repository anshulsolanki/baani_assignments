import os
from data_loader import (load_sentences_from_csv,tokenize_corpus_sentences,load_wsd_data,)
from part1_embeddings import (part1_task_2_1,part1_task_2_2,part1_task_2_3,part1_task_2_4,)
from part2_preprocessing import (part2_problem_1,part2_problem_2,)
from part2_lesk import (part2_problem_3,part2_problem_4,part2_problem_5,part2_problem_6,)
from part2_naive_bayes import part2_problem_7_extra_credit


def main():
    base_dir=os.path.dirname(os.path.abspath(__file__))
    csv_path=os.path.join(base_dir,"train.csv")
    wsd_train_path=os.path.join(base_dir,"wsd-data","wsd_train.txt")

    # part 1: word embeddinsg
    print("=== PART 1: WORD EMBEDDINGS ===")
    raw_sentences = load_sentences_from_csv(csv_path, max_rows=20000)
    tokenized_sentences = tokenize_corpus_sentences(raw_sentences)
    print(f"Loaded and tokenized {len(tokenized_sentences)} sentences from train.csv")

    print("\n--- Task 2.1: Constructing the Co-occurrence Matrix (window_size=5) ---")
    cooc_matrix, word_to_id = part1_task_2_1(tokenized_sentences, window_size=5, max_vocab_size=5000)
    print(f"Vocabulary size: {len(word_to_id)}")
    print(f"Co-occurrence matrix shape: {cooc_matrix.shape}, Non-zero entries: {cooc_matrix.nnz}")

    print("\n--- Task 2.2: Dimensionality Reduction Using SVD (k=100) ---")
    u_matrix, singular_values, _ = part1_task_2_2(cooc_matrix, embedding_dim=100)
    print(f"Word embeddings matrix U shape: {u_matrix.shape}")
    print(f"Top 5 singular values: {[round(float(val), 2) for val in singular_values[:5]]}")

    print("\n--- Task 2.3: Evaluating Word Embeddings on 5 Word Pairs ---")
    word_pairs = [("company", "firm", "Synonyms"),("win", "lose", "Antonyms"),("computer", "software", "Topical / Domain Related"),("president", "government", "Political / Institutional"),("market", "football", "Unrelated"),]
    pair_scores = part1_task_2_3(u_matrix, word_to_id, word_pairs)
    for item in pair_scores:
        print(f"({item['word1']}, {item['word2']}) [{item['relation']}] -> Cosine Similarity: {item['similarity']:.4f}")

    print("\n--- Task 2.4: Comparing Context Window Sizes (w=2 vs w=5) ---")
    window_results = part1_task_2_4(tokenized_sentences, word_pairs, window_sizes=(2, 5), embedding_dim=100)
    for idx, (w1, w2, rel) in enumerate(word_pairs):
        sim_w2 = window_results[2][idx]["similarity"]
        sim_w5 = window_results[5][idx]["similarity"]
        print(f"({w1}, {w2}) [{rel}] -> w=2: {sim_w2:.4f} | w=5: {sim_w5:.4f}")

    #part2: wsd
    print("\n=== PART 2: WORD SENSE DISAMBIGUATION (WSD) ===")
    raw_wsd_data = load_wsd_data(wsd_train_path, max_rows=2500)

    print("\n--- Problem 1: Preprocessing and POS Tagging ---")
    preprocessed_data = part2_problem_1(raw_wsd_data)
    train_set = preprocessed_data[:2000]
    test_set = preprocessed_data[2000:2500]
    print(f"Preprocessed {len(train_set)} training sentences and {len(test_set)} test sentences.")
    print(f"Sample POS tags (Sentence 1): {train_set[0]['pos_tags'][:10]}")

    print("\n--- Problem 2: Listing Possible Senses (First 10 Sentences) ---")
    json_path = os.path.join(base_dir, "first_10_sentences_senses.json")
    part2_problem_2(train_set, json_path)
    print(f"Saved WordNet senses for first 10 sentences to {json_path}")

    print("\n--- Problem 3: Most Frequent Sense (MFS) Baseline ---")
    mfs_metrics, _ = part2_problem_3(train_set)
    print(f"MFS Baseline -> Precision: {mfs_metrics['precision']:.2f}%, Recall: {mfs_metrics['recall']:.2f}%, F1: {mfs_metrics['f1']:.2f}%")

    print("\n--- Problem 4: Simplified Lesk Algorithm ---")
    basic_metrics, basic_preds, example = part2_problem_4(train_set)
    print(f"Simplified Lesk -> Precision: {basic_metrics['precision']:.2f}%, Recall: {basic_metrics['recall']:.2f}%, F1: {basic_metrics['f1']:.2f}%")
    if example:
        print(f"\nIllustrative Example for word '{example['target_word']}':")
        print(f"Sentence: {example['sentence']}")
        print(f"Gold Sense: {example['gold_sense']} | Predicted Sense: {example['predicted_sense']}")
        for cand in example["candidates"][:6]:
            print(f"  {cand['sense']} (Overlap = {cand['overlap_count']}: {cand['overlap_words']}) -> Gloss: {cand['gloss']}")

    print("\n--- Problem 5: Improved Lesk Algorithm ---")
    imp_metrics, imp_preds = part2_problem_5(train_set)
    print(f"Improved Lesk -> Precision: {imp_metrics['precision']:.2f}%, Recall: {imp_metrics['recall']:.2f}%, F1: {imp_metrics['f1']:.2f}%")

    print("\n--- Problem 6: Evaluation of 10 Ambiguous Words ---")
    ten_words = part2_problem_6(train_set, basic_preds, imp_preds)
    for i, item in enumerate(ten_words, start=1):
        print(f"{i}. Word: '{item['word']}'")
        print(f"   Gold Sense    : {item['gold_sense']} ({item['gold_gloss']})")
        print(f"   Basic Lesk    : {item['basic_pred']} ({item['basic_gloss']})")
        print(f"   Improved Lesk : {item['improved_pred']} ({item['improved_gloss']})")

    print("\n--- Problem 7 (Extra Credit): Naive Bayes WSD on Test Set ---")
    test_results = part2_problem_7_extra_credit(train_set, test_set)
    for model_name, m in test_results.items():
        print(f"{model_name} -> Precision: {m['precision']:.2f}%, Recall: {m['recall']:.2f}%, F1: {m['f1']:.2f}%")


if __name__ == "__main__":
    main()
