import math
from collections import Counter, defaultdict
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds

# constructing the cooccurence matrix, building vocab from corpus sentences and count of frequency with which the target word appears with each context word and within the window size
def part1_task_2_1(tokenized_sentences, window_size=2, max_vocab_size=5000):
    word_counts = Counter()
    for tokens in tokenized_sentences:
        word_counts.update(tokens)

    vocab_words = [word for word, _ in word_counts.most_common(max_vocab_size)]
    word_to_id = {word: idx for idx, word in enumerate(vocab_words)}

    cooc_counts = defaultdict(float)
    for tokens in tokenized_sentences:
        token_ids = [word_to_id[w] for w in tokens if w in word_to_id]
        n = len(token_ids)

        for i in range(n):
            target_id = token_ids[i]
            start = max(0, i - window_size)
            end = min(n, i + window_size + 1)

            for j in range(start, end):
                if i != j:
                    context_id = token_ids[j]
                    cooc_counts[(target_id, context_id)] += 1.0

    rows, cols, values = [], [], []
    for (r, c), count in cooc_counts.items():
        rows.append(r)
        cols.append(c)
        values.append(count)

    vocab_size = len(word_to_id)
    cooc_matrix = csr_matrix((values, (rows, cols)), shape=(vocab_size, vocab_size), dtype=np.float64)
    return cooc_matrix, word_to_id

# using svd to do dimensionaltiy reduction; decomposing co-occurrence matrix M=U*Sigma*V^T using svds to get target word matrix U
def part1_task_2_2(cooc_matrix, embedding_dim=100):
    u_matrix, singular_values, vt_matrix = svds(cooc_matrix, k=embedding_dim)

    #soritng singular vals and corresponding vectors in desc order
    order = np.argsort(singular_values)[::-1]
    u_matrix = u_matrix[:, order] 
    singular_values = singular_values[order]
    vt_matrix = vt_matrix[order, :]

    return u_matrix, singular_values, vt_matrix

# computing cosine similarity cos(a,b) = (a . b)/(||a||*||b||)
def compute_cosine_similarity(vec_a, vec_b):
    dot_product = 0.0
    norm_a = 0.0
    norm_b = 0.0

    for i in range(len(vec_a)):
        a = float(vec_a[i])
        b = float(vec_b[i])
        dot_product += a * b
        norm_a += a * a
        norm_b += b * b

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (math.sqrt(norm_a) * math.sqrt(norm_b))

# evaluating the word embeddigns
def part1_task_2_3(u_matrix, word_to_id, word_pairs):
    results = []
    for word1, word2, relation in word_pairs:
        if word1 in word_to_id and word2 in word_to_id:
            vec1 = u_matrix[word_to_id[word1]]
            vec2 = u_matrix[word_to_id[word2]]
            similarity = compute_cosine_similarity(vec1, vec2)
        else:
            similarity = 0.0

        results.append({"word1": word1,"word2": word2,"relation": relation,"similarity": similarity,})
    return results

# analysis for diff context window sizes, getting similarity socres for each window
def part1_task_2_4(tokenized_sentences, word_pairs, window_sizes=(2, 5), embedding_dim=100):
    window_results = {}
    for w in window_sizes:
        cooc_matrix, word_to_id = part1_task_2_1(tokenized_sentences, window_size=w)
        u_matrix, _, _ = part1_task_2_2(cooc_matrix, embedding_dim=embedding_dim)
        scores = part1_task_2_3(u_matrix, word_to_id, word_pairs)
        window_results[w] = scores

    return window_results
