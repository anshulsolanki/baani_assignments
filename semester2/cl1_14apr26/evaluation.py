import os
import sys
from seqeval.metrics import f1_score as seqeval_f1
from seqeval.metrics import classification_report
import numpy as np

# Add current directory to path
sys.path.append('/Users/solankianshul/Documents/projects/temp_work/baani_work/assignments/semester2/cl1_14apr26')

from hmm_tagger import HMMTagger
from crf_tagger import CRFTagger, sent2features, sent2labels

def load_combined_conll(file_path):
    """Load data from manual_dataset.conll and split into English and Hindi."""
    english_sentences = []
    hindi_sentences = []
    current_sentence = []
    
    is_hindi = False
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return english_sentences, hindi_sentences
        
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#Manually annotated dataset for hindi data'):
                is_hindi = True
                if current_sentence:
                    english_sentences.append(current_sentence)
                    current_sentence = []
                continue
            if line.startswith('#'):
                continue
            if line == '':
                if current_sentence:
                    if is_hindi:
                        hindi_sentences.append(current_sentence)
                    else:
                        english_sentences.append(current_sentence)
                    current_sentence = []
                continue
            
            parts = line.split('\t')
            if len(parts) >= 4:
                word = parts[0]
                pos = parts[1]
                chunk = parts[2]
                ner = parts[3]
                current_sentence.append((word, pos, chunk, ner))
                
    if current_sentence:
        if is_hindi:
            hindi_sentences.append(current_sentence)
        else:
            english_sentences.append(current_sentence)
            
    return english_sentences, hindi_sentences

def load_english_train_data(file_path):
    """Load English data from CoNLL-U file for POS tagging."""
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

def load_hindi_train_data(file_path, task='POS'):
    """Load Hindi data from SSF-like text file."""
    sentences = []
    current_sentence = []
    
    # POS Tag mapping
    pos_map = {
        'N_NN': 'NN',
        'N_NNP': 'NNP',
        'V_VM': 'VM',
        'V_VAUX': 'VAUX',
        'PSP': 'PSP',
        'CC_CCD': 'CC',
        'PR_PRP': 'PRP',
        'RD_PUNC': 'PUNC',
        'DM_DMD': 'DEM',
        'RP_INTF': 'INTF',
        'QT_QTC': 'QF',
        'RB': 'RB',
        'NEG': 'NEG'
    }
    
    # Chunk Tag mapping
    chunk_map = {
        'B-VGF': 'B-VP',
        'I-VGF': 'I-VP',
        'B-VGNN': 'B-VP',
        'I-VGNN': 'I-VP',
        'B-VGNF': 'B-VP',
        'I-VGNF': 'I-VP',
        'B-JJP': 'B-ADJP',
        'I-JJP': 'I-ADJP',
        'B-BLK': 'O',
        'B-CCP': 'O',
        'I-CCP': 'O'
    }
    
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
                chunk = parts[-1]
                
                if task == 'POS':
                    mapped_pos = pos_map.get(pos, pos)
                    current_sentence.append((word, mapped_pos))
                elif task == 'Chunk':
                    mapped_chunk = chunk_map.get(chunk, chunk)
                    current_sentence.append((word, mapped_chunk))
    if current_sentence:
        sentences.append(current_sentence)
    return sentences

def load_llm_ner_data(file_path):
    """Load English NER data from LLM-generated CoNLL file."""
    sentences = []
    current_sentence = []
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return sentences
        
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or line == '':
                if current_sentence:
                    sentences.append(current_sentence)
                    current_sentence = []
                continue
            parts = line.split('\t')
            if len(parts) >= 3:
                word = parts[0]
                ner = parts[2]
                current_sentence.append((word, ner))
    if current_sentence:
        sentences.append(current_sentence)
    return sentences

def evaluate_pos(predicted, gold):
    """Compute POS accuracy."""
    correct = 0
    total = 0
    for p_sent, g_sent in zip(predicted, gold):
        for p_tok, g_tok in zip(p_sent, g_sent):
            if p_tok[1] == g_tok[1]:
                correct += 1
            total += 1
    return correct / total if total > 0 else 0

def evaluate_spans(predicted_labels, gold_labels):
    """Compute F1 score for spans (Chunking or NER) using seqeval."""
    return seqeval_f1(gold_labels, predicted_labels)

def print_errors(predicted, gold, label_type="POS", num_errors=5):
    """Print sample errors."""
    print(f"\n--- Sample Errors for {label_type} ---")
    count = 0
    for p_sent, g_sent in zip(predicted, gold):
        for p_tok, g_tok in zip(p_sent, g_sent):
            p_word, p_label = p_tok[0], p_tok[1]
            g_word, g_label = g_tok[0], g_tok[1]
            
            if p_label != g_label:
                print(f"Word: {p_word} | Predicted: {p_label} | Gold: {g_label}")
                count += 1
                if count >= num_errors:
                    return

def run_english_pipeline():
    print("=== Running English Pipeline ===")
    train_path = '/Users/solankianshul/Documents/projects/temp_work/baani_work/assignments/semester2/cl1_14apr26/data/UD_English-EWT/en_ewt-ud-train.conllu'
    manual_path = '/Users/solankianshul/Documents/projects/temp_work/baani_work/assignments/semester2/cl1_14apr26/2025114016/manual_dataset.conll'
    llm_path = '/Users/solankianshul/Documents/projects/temp_work/baani_work/assignments/semester2/cl1_14apr26/2025114016/llm_dataset.conll'
    
    eng_train = load_english_train_data(train_path)
    eng_manual, _ = load_combined_conll(manual_path)
    
    print(f"Loaded {len(eng_train)} training sentences.")
    print(f"Loaded {len(eng_manual)} manual evaluation sentences.")
    
    # Train HMM for POS
    hmm = HMMTagger(alpha=1.0)
    hmm.train(eng_train)
    
    # Train CRF for POS
    crf = CRFTagger()
    crf.train(eng_train)
    
    # Evaluate POS
    hmm_preds = []
    crf_preds = []
    
    for sent in eng_manual:
        words = [t[0] for t in sent]
        
        hmm_pred = hmm.viterbi(words)
        hmm_preds.append(hmm_pred)
        
        crf_pred = crf.predict(words)
        crf_preds.append(list(zip(words, crf_pred)))
        
    aligned_gold = [[(t[0], t[1]) for t in sent] for sent in eng_manual]
    
    hmm_acc = evaluate_pos(hmm_preds, aligned_gold)
    crf_acc = evaluate_pos(crf_preds, aligned_gold)
    
    print(f"English HMM POS Accuracy: {hmm_acc:.4f}")
    print(f"English CRF POS Accuracy: {crf_acc:.4f}")
    
    print_errors(crf_preds, aligned_gold, label_type="English CRF POS", num_errors=5)
    
    # --- NER Task ---
    print("\n--- Running English NER (CRF trained on LLM data) ---")
    llm_ner_data = load_llm_ner_data(llm_path)
    print(f"Loaded {len(llm_ner_data)} LLM sentences for NER training.")
    
    if llm_ner_data:
        crf_ner = CRFTagger()
        crf_ner.train(llm_ner_data)
        
        ner_preds = []
        for sent in eng_manual:
            words = [t[0] for t in sent]
            ner_pred = crf_ner.predict(words)
            ner_preds.append(list(ner_pred))
            
        gold_ner = [[t[3] for t in sent] for sent in eng_manual]
        
        # Clean gold NER if needed (sometimes they are not standard IOB)
        # Let's assume they are valid.
        
        ner_f1 = evaluate_spans(ner_preds, gold_ner)
        print(f"English CRF NER F1: {ner_f1:.4f}")
        
        ner_aligned = [[(sent[i][0], ner_preds[j][i]) for i in range(len(sent))] for j, sent in enumerate(eng_manual)]
        gold_ner_aligned = [[(t[0], t[3]) for t in sent] for sent in eng_manual]
        
        print_errors(ner_aligned, gold_ner_aligned, label_type="English CRF NER", num_errors=5)

def run_hindi_pipeline():
    print("\n=== Running Hindi Pipeline ===")
    train_path = '/Users/solankianshul/Documents/projects/temp_work/baani_work/assignments/semester2/cl1_14apr26/data/ltrc_shallow_parsing/data/Hindi/hindi-train.txt'
    manual_path = '/Users/solankianshul/Documents/projects/temp_work/baani_work/assignments/semester2/cl1_14apr26/2025114016/manual_dataset.conll'
    
    _, hin_manual = load_combined_conll(manual_path)
    hin_train_pos = load_hindi_train_data(train_path, task='POS')
    hin_train_chunk = load_hindi_train_data(train_path, task='Chunk')
    
    print(f"Loaded {len(hin_train_pos)} training sentences (POS).")
    print(f"Loaded {len(hin_train_chunk)} training sentences (Chunk).")
    print(f"Loaded {len(hin_manual)} manual evaluation sentences.")
    
    # Train HMM for POS
    hmm_pos = HMMTagger(alpha=1.0)
    hmm_pos.train(hin_train_pos)
    
    # Train CRF for POS
    crf_pos = CRFTagger()
    crf_pos.train(hin_train_pos)
    
    # Evaluate POS
    hmm_preds = []
    crf_preds = []
    
    for sent in hin_manual:
        words = [t[0] for t in sent]
        
        hmm_pred = hmm_pos.viterbi(words)
        hmm_preds.append(hmm_pred)
        
        crf_pred = crf_pos.predict(words)
        crf_preds.append(list(zip(words, crf_pred)))
        
    aligned_gold_pos = [[(t[0], t[1]) for t in sent] for sent in hin_manual]
    
    hmm_acc = evaluate_pos(hmm_preds, aligned_gold_pos)
    crf_acc = evaluate_pos(crf_preds, aligned_gold_pos)
    
    print(f"Hindi HMM POS Accuracy: {hmm_acc:.4f}")
    print(f"Hindi CRF POS Accuracy: {crf_acc:.4f}")
    
    print_errors(crf_preds, aligned_gold_pos, label_type="Hindi CRF POS", num_errors=5)
    
    # Train HMM for Chunking
    hmm_chunk = HMMTagger(alpha=1.0)
    hmm_chunk.train(hin_train_chunk)
    
    # Train CRF for Chunking
    crf_chunk = CRFTagger()
    crf_chunk.train(hin_train_chunk)
    
    # Evaluate Chunking
    hmm_chunk_preds = []
    crf_chunk_preds = []
    
    for sent in hin_manual:
        words = [t[0] for t in sent]
        
        hmm_pred = hmm_chunk.viterbi(words)
        hmm_chunk_preds.append([t[1] for t in hmm_pred])
        
        crf_pred = crf_chunk.predict(words)
        crf_chunk_preds.append(list(crf_pred))
        
    gold_chunks = [[t[2] for t in sent] for sent in hin_manual]
    
    hmm_chunk_f1 = evaluate_spans(hmm_chunk_preds, gold_chunks)
    crf_chunk_f1 = evaluate_spans(crf_chunk_preds, gold_chunks)
    
    print(f"Hindi HMM Chunking F1: {hmm_chunk_f1:.4f}")
    print(f"Hindi CRF Chunking F1: {crf_chunk_f1:.4f}")
    
    crf_chunk_aligned = [[(sent[i][0], crf_chunk_preds[j][i]) for i in range(len(sent))] for j, sent in enumerate(hin_manual)]
    gold_chunk_aligned = [[(t[0], t[2]) for t in sent] for sent in hin_manual]
    
    print_errors(crf_chunk_aligned, gold_chunk_aligned, label_type="Hindi CRF Chunking", num_errors=5)

if __name__ == "__main__":
    run_english_pipeline()
    run_hindi_pipeline()
