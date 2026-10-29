import os
import json
import re
import time
from google.cloud import aiplatform

# --- Configuration ---
PROJECT_ID = "google.com:as-experiments"
#LOCATION = "us-west1"
#ENDPOINT_ID = "mg-endpoint-33c774b6-d0cf-42dc-903e-ec1dd4ce38be" #2B

LOCATION = "asia-southeast1" 
ENDPOINT_ID = "mg-endpoint-113c9689-f2f9-4d06-be45-d383bda7125d" #26B

def get_endpoint():
    """Initializes the Vertex AI SDK and returns the Endpoint."""
    try:
        print(f"Initializing Vertex AI for project {PROJECT_ID} in {LOCATION}")
        aiplatform.init(project=PROJECT_ID, location=LOCATION)
        endpoint_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/{ENDPOINT_ID}"
        print(f"Connecting to endpoint: {endpoint_name}")
        return aiplatform.Endpoint(endpoint_name=endpoint_name)
    except Exception as e:
        print(f"Error initializing Vertex AI endpoint: {e}")
        return None

def extract_guidelines(file_path):
    """Reads the entire instructions file to use as guidelines."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading instructions file: {e}")
        return ""

def parse_conll(file_path):
    """Reads a CoNLL file and yields sentences, ignoring metadata comments."""
    current_sentence = []
    current_words = []
    sentence_text = ""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                if current_words:
                    yield sentence_text, current_sentence
                    current_words = []
                    current_sentence = []
                    sentence_text = ""
                continue
            
            if line.startswith('#'):
                if not sentence_text and len(current_sentence) == 1:
                     sentence_text = line[1:].strip()
                current_sentence.append(line)
                continue
            
            parts = line.split()
            if len(parts) >= 2:
                current_words.append(parts[1])
                current_sentence.append(line)
                
    if current_words:
        yield sentence_text, current_sentence

def clean_output(text):
    """Filters the model output to retain only the annotated CoNLL lines."""
    if not text:
        return ""
    lines = text.split('\n')
    filtered_lines = []
    for line in lines:
        line = line.strip()
        # Match lines starting with a number followed by at least two string parts (Word, Tag)
        if re.match(r'^\d+\s+\S+\s+\S+', line):
            filtered_lines.append(line)
    return "\n".join(filtered_lines)

def annotate_sentence(endpoint, sentence_text, prompt_template, guidelines, raw_lines, max_retries=3, delay=5):
    """Calls the endpoint to annotate a sentence with retry logic."""
    
    words_to_annotate = []
    for line in raw_lines:
        if not line.startswith('#'):
             parts = line.split()
             if len(parts) >= 2:
                  words_to_annotate.append(f"{parts[0]}\t{parts[1]}")
                  
    words_text = "\n".join(words_to_annotate)
    
    # Remove the conflicting [TASK] section from the guidelines
    guidelines_cleaned = re.sub(r'\[TASK\].*', '', guidelines, flags=re.DOTALL).strip()
    
    prompt = prompt_template.format(
        guidelines=guidelines_cleaned, 
        sentence=sentence_text,
        words=words_text
    )
    
    instances = [
        {
            "prompt": prompt,
            "max_tokens": 1000,
            "temperature": 0.1,
            "top_p": 0.9,
        },
    ]
    
    for attempt in range(max_retries):
        try:
            response = endpoint.predict(instances=instances)
            
            if not response.predictions:
                print(f"Warning: No predictions returned on attempt {attempt + 1}/{max_retries}.")
                time.sleep(delay)
                continue
                
            prediction = response.predictions[0]
            
            generated_text = ""
            if isinstance(prediction, dict) and "generated_text" in prediction:
                 generated_text = prediction["generated_text"]
            else:
                 generated_text = str(prediction)
                 
            cleaned = clean_output(generated_text)
            if cleaned:
                 return cleaned
            else:
                 print(f"Warning: Cleaned output was empty on attempt {attempt + 1}/{max_retries}.")
                 time.sleep(delay)
                 continue
                 
        except Exception as e:
            print(f"Error during generation on attempt {attempt + 1}/{max_retries}: {e}")
            time.sleep(delay)
            
    print(f"Error: Failed to annotate sentence after {max_retries} attempts.")
    return None

def write_annotated_file(output_path, annotations, raw_files_data):
    """Writes the annotations back to a CoNLL-like file, maintaining original comments."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, annotation in enumerate(annotations):
            if annotation:
                raw_lines = raw_files_data[i]
                for line in raw_lines:
                     if line.startswith('#'):
                          f.write(line + "\n")
                
                f.write(annotation + "\n\n")

def annotate_english_data(endpoint, file_path, output_path, guidelines):
    """Annotates English dataset using guidelines."""
    print(f"Annotating English data: {file_path}")
    
    prompt_template = """
    Framework Guidelines:
    {guidelines}
    
    Task: Annotate the following English sentence. For each word listed below, provide its POS tag and Karaka role based on the guidelines.
    
    Sentence: "{sentence}"
    
    Words to annotate:
    {words}
    
    Output Format:
    Return EXACTLY one line for each word in the input list, maintaining the index and word.
    Format: [Index] [Word] [POS Tag] [Karaka Role]
    
    Return ONLY the annotated lines, no extra text, notes, or examples.
    """
    
    results = []
    raw_files_data = []
    for sentence_text, raw_lines in parse_conll(file_path):
        print(f"Processing: {sentence_text}")
        response = annotate_sentence(endpoint, sentence_text, prompt_template, guidelines, raw_lines)
        if response:
            results.append(response)
            raw_files_data.append(raw_lines)
        else:
            print(f"Skipping sentence due to failed annotation.")
            
    write_annotated_file(output_path, results, raw_files_data)
    print(f"Saved to: {output_path}")

def annotate_hindi_data(endpoint, file_path, output_path, guidelines):
    """Annotates Hindi dataset using guidelines."""
    print(f"Annotating Hindi data: {file_path}")
    
    prompt_template = """
    Framework Guidelines:
    {guidelines}
    
    Task: Annotate the following Hindi sentence. For each word listed below, provide its POS tag and Karaka role based on the guidelines.
    
    Sentence: "{sentence}"
    
    Words to annotate:
    {words}
    
    Output Format:
    Return EXACTLY one line for each word in the input list, maintaining the index and word.
    Format: [Index] [Word] [POS Tag] [Karaka Role]
    
    Return ONLY the annotated lines, no extra text, notes, or examples.
    """
    
    results = []
    raw_files_data = []
    for sentence_text, raw_lines in parse_conll(file_path):
        print(f"Processing: {sentence_text}")
        response = annotate_sentence(endpoint, sentence_text, prompt_template, guidelines, raw_lines)
        if response:
            results.append(response)
            raw_files_data.append(raw_lines)
        else:
            print(f"Skipping sentence due to failed annotation.")
            
    write_annotated_file(output_path, results, raw_files_data)
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    endpoint = get_endpoint()
    if not endpoint:
        print("Failed to get endpoint. Exiting.")
        exit(1)
        
    script_dir = os.path.dirname(os.path.abspath(__file__))
    instructions_file = os.path.join(script_dir, "instructions.txt")
    
    # Extract guidelines
    print("Reading guidelines from instructions.txt...")
    guidelines = extract_guidelines(instructions_file)
    
    if not guidelines:
        print("Warning: Guidelines read were empty or could not be read.")
        
    english_file = os.path.join(script_dir, "batch3_english.conll")
    hindi_file = os.path.join(script_dir, "batch3_hindi.conll")
    
    english_output = os.path.join(script_dir, "batch3_english_annotated_with_inst.conll")
    hindi_output = os.path.join(script_dir, "batch3_hindi_annotated_with_inst.conll")
    
    # Process files
    annotate_english_data(endpoint, english_file, english_output, guidelines)
    annotate_hindi_data(endpoint, hindi_file, hindi_output, guidelines)
