import numpy as np
from collections import defaultdict, Counter
import os

class HMMTagger:
    def __init__(self, alpha=1.0):
        """
        Initialize the HMM Tagger.
        alpha: smoothing parameter for Laplace smoothing.
        """
        self.alpha = alpha
        self.tags = set()
        self.vocab = set()
        
        # Counts for probabilities
        self.emission_counts = defaultdict(Counter)  # tag -> word -> count
        self.transition_counts = defaultdict(Counter)  # tag1 -> tag2 -> count
        self.tag_counts = Counter()  # tag -> count
        self.start_tag_counts = Counter()  # start_tag -> count
        
        # Probabilities
        self.emission_probs = defaultdict(dict)
        self.transition_probs = defaultdict(dict)
        self.start_probs = {}
        
    def train(self, tagged_sentences):
        """
        Train the HMM on tagged sentences.
        tagged_sentences: list of lists of (word, tag) tuples.
        """
        print(f"Training HMM on {len(tagged_sentences)} sentences...")
        for sentence in tagged_sentences:
            if not sentence:
                continue
                
            # Handle start tag
            start_word, start_tag = sentence[0]
            self.start_tag_counts[start_tag] += 1
            self.tags.add(start_tag)
            self.vocab.add(start_word)
            self.emission_counts[start_tag][start_word] += 1
            self.tag_counts[start_tag] += 1
            
            for i in range(1, len(sentence)):
                prev_word, prev_tag = sentence[i-1]
                word, tag = sentence[i]
                
                self.tags.add(tag)
                self.vocab.add(word)
                
                self.emission_counts[tag][word] += 1
                self.transition_counts[prev_tag][tag] += 1
                self.tag_counts[tag] += 1
                
        # Compute probabilities with Laplace smoothing
        self._compute_probs()
        print("Training complete.")
        
    def _compute_probs(self):
        num_tags = len(self.tags)
        num_words = len(self.vocab)
        
        # Start probabilities
        total_sentences = sum(self.start_tag_counts.values())
        for tag in self.tags:
            self.start_probs[tag] = (self.start_tag_counts[tag] + self.alpha) / (total_sentences + self.alpha * num_tags)
            
        # Transition probabilities
        for t1 in self.tags:
            total_transitions = sum(self.transition_counts[t1].values())
            for t2 in self.tags:
                self.transition_probs[t1][t2] = (self.transition_counts[t1][t2] + self.alpha) / (total_transitions + self.alpha * num_tags)
                
        # Emission probabilities
        for tag in self.tags:
            total_emissions = self.tag_counts[tag]
            for word in self.vocab:
                self.emission_probs[tag][word] = (self.emission_counts[tag][word] + self.alpha) / (total_emissions + self.alpha * num_words)
                
    def get_emission_prob(self, tag, word):
        """Get emission probability with fallback for unknown words."""
        if word in self.emission_probs[tag]:
            return self.emission_probs[tag][word]
        else:
            # Smoothing for unknown words
            num_words = len(self.vocab)
            return self.alpha / (self.tag_counts[tag] + self.alpha * num_words)
            
    def viterbi(self, words):
        """
        Viterbi algorithm for decoding.
        words: list of words to tag.
        """
        if not words:
            return []
            
        T = list(self.tags)
        N = len(words)
        M = len(T)
        
        # Viterbi matrix: M x N
        viterbi_mat = np.zeros((M, N))
        # Backpointer matrix: M x N
        backpointer = np.zeros((M, N), dtype=int)
        
        # Initialization
        first_word = words[0]
        for i, tag in enumerate(T):
            viterbi_mat[i, 0] = self.start_probs[tag] * self.get_emission_prob(tag, first_word)
            backpointer[i, 0] = 0
            
        # Recursion
        for j in range(1, N):
            word = words[j]
            for i, tag in enumerate(T):
                # Find max probability from previous tags
                max_prob = -1
                best_prev_tag_idx = 0
                for prev_idx, prev_tag in enumerate(T):
                    prob = viterbi_mat[prev_idx, j-1] * self.transition_probs[prev_tag][tag] * self.get_emission_prob(tag, word)
                    if prob > max_prob:
                        max_prob = prob
                        best_prev_tag_idx = prev_idx
                        
                viterbi_mat[i, j] = max_prob
                backpointer[i, j] = best_prev_tag_idx
                
        # Termination
        best_last_tag_idx = np.argmax(viterbi_mat[:, N-1])
        
        # Path reconstruction
        best_path = [best_last_tag_idx]
        for j in range(N-1, 0, -1):
            best_path.insert(0, backpointer[best_path[0], j])
            
        # Map indices back to tags
        result_tags = [T[idx] for idx in best_path]
        return list(zip(words, result_tags))

def load_english_data(file_path):
    """Load English data from CoNLL-U file."""
    sentences = []
    current_sentence = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or line.strip() == '':
                if current_sentence:
                    sentences.append(current_sentence)
                    current_sentence = []
                continue
            parts = line.strip().split('\t')
            if len(parts) >= 5:
                word = parts[1]
                pos = parts[3]  # UPOS
                current_sentence.append((word, pos))
    if current_sentence:
        sentences.append(current_sentence)
    return sentences

def load_hindi_data(file_path):
    """Load Hindi data from SSF-like text file."""
    sentences = []
    current_sentence = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() == '':
                if current_sentence:
                    sentences.append(current_sentence)
                    current_sentence = []
                continue
            parts = line.strip().split()
            if len(parts) >= 3:
                word = parts[0]
                pos = parts[1]
                current_sentence.append((word, pos))
    if current_sentence:
        sentences.append(current_sentence)
    return sentences

if __name__ == "__main__":
    # Test with real data (subset)
    eng_train_path = '/Users/solankianshul/Documents/projects/temp_work/baani_work/assignments/semester2/cl1_14apr26/data/UD_English-EWT/en_ewt-ud-train.conllu'
    
    if os.path.exists(eng_train_path):
        print("Loading English training data...")
        eng_sentences = load_english_data(eng_train_path)
        print(f"Loaded {len(eng_sentences)} sentences.")
        
        # Train on a subset for quick testing
        subset_size = 1000
        tagger = HMMTagger(alpha=1.0)
        tagger.train(eng_sentences[:subset_size])
        
        test_sentence = ["The", "cat", "sat", "on", "the", "mat", "."]
        result = tagger.viterbi(test_sentence)
        print("Test Result:", result)
    else:
        print(f"File not found: {eng_train_path}")
