import os
import sklearn_crfsuite

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

def word2features(sent, i):
    word = sent[i][0]
    
    features = {
        'bias': 1.0,
        'word': word,
        'word.lower()': word.lower(),
        'word[-3:]': word[-3:],
        'word[-2:]': word[-2:],
        'word.isupper()': word.isupper(),
        'word.istitle()': word.istitle(),
        'word.isdigit()': word.isdigit(),
    }
    
    # Add prefixes
    features['word[:1]'] = word[:1]
    features['word[:2]'] = word[:2]
    features['word[:3]'] = word[:3]
    
    if i > 0:
        word1 = sent[i-1][0]
        features.update({
            '-1:word': word1,
            '-1:word.lower()': word1.lower(),
            '-1:word.istitle()': word1.istitle(),
            '-1:word.isupper()': word1.isupper(),
        })
    else:
        features['BOS'] = True

    if i < len(sent) - 1:
        word1 = sent[i+1][0]
        features.update({
            '+1:word': word1,
            '+1:word.lower()': word1.lower(),
            '+1:word.istitle()': word1.istitle(),
            '+1:word.isupper()': word1.isupper(),
        })
    else:
        features['EOS'] = True

    return features

def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]

def sent2labels(sent):
    return [label for token, label in sent]

class CRFTagger:
    def __init__(self):
        self.model = None
        
    def train(self, train_sentences):
        print("Extracting features...")
        X_train = [sent2features(s) for s in train_sentences]
        y_train = [sent2labels(s) for s in train_sentences]
        
        print("Training CRF...")
        self.model = sklearn_crfsuite.CRF(
            algorithm='lbfgs',
            c1=0.1,
            c2=0.1,
            max_iterations=100,
            all_possible_transitions=True
        )
        self.model.fit(X_train, y_train)
        print("Training complete.")
        
    def predict(self, sentence):
        if not self.model:
            raise Exception("Model not trained.")
        
        # If sentence is a list of words, convert to list of (word, dummy_tag) tuples
        if isinstance(sentence[0], str):
            dummy_sent = [(w, 'O') for w in sentence]
        else:
            dummy_sent = sentence
            
        features = sent2features(dummy_sent)
        return self.model.predict([features])[0]

if __name__ == "__main__":
    eng_train_path = '/Users/solankianshul/Documents/projects/temp_work/baani_work/assignments/semester2/cl1_14apr26/data/UD_English-EWT/en_ewt-ud-train.conllu'
    
    if os.path.exists(eng_train_path):
        print("Loading English training data...")
        eng_sentences = load_english_data(eng_train_path)
        print(f"Loaded {len(eng_sentences)} sentences.")
        
        # Train on a subset for quick testing
        subset_size = 1000
        tagger = CRFTagger()
        tagger.train(eng_sentences[:subset_size])
        
        test_sentence = ["The", "cat", "sat", "on", "the", "mat", "."]
        result = tagger.predict(test_sentence)
        print("Test Result:", result)
    else:
        print(f"File not found: {eng_train_path}")
