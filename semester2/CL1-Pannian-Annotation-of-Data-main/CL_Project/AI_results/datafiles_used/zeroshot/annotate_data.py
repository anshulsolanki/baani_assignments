import os
import json
import re
from google.cloud import aiplatform

# --- Configuration ---
PROJECT_ID = "google.com:as-experiments"
LOCATION = "us-west1"
ENDPOINT_ID = "mg-endpoint-33c774b6-d0cf-42dc-903e-ec1dd4ce38be"

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

def parse_conll(file_path):
    """Reads a CoNLL file and yields sentences."""
    current_sentence = []
    current_words = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                if current_words:
                    yield " ".join(current_words), current_sentence
                    current_words = []
                    current_sentence = []
                continue
            
            if line.startswith('#'):
                current_sentence.append(line)
                continue
            
            parts = line.split()
            if len(parts) >= 2:
                current_words.append(parts[1])
                current_sentence.append(line)
                
    if current_words:
        yield " ".join(current_words), current_sentence

def annotate_sentence(endpoint, sentence_text, prompt_template):
    """Calls the endpoint to annotate a sentence."""
    prompt = prompt_template.format(sentence=sentence_text)
    
    instances = [
        {
            "prompt": prompt,
            "max_tokens": 1000,
            "temperature": 0.1,
            "top_p": 0.9,
        },
    ]
    
    try:
        response = endpoint.predict(instances=instances)
        
        if not response.predictions:
            return None
            
        # Returning the first prediction. The exact structure depends on the model's serving container.
        # Often it's a string or a dictionary containing the generated text.
        prediction = response.predictions[0]
        
        # If it's a dictionary (common for some containers), try to extract the text
        if isinstance(prediction, dict) and "generated_text" in prediction:
             return prediction["generated_text"]
             
        return str(prediction)
        
    except Exception as e:
        print(f"Error during generation: {e}")
        return None

def write_annotated_file(output_path, annotations):
    """Writes the annotations back to a CoNLL-like file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in annotations:
            f.write(item + "\n\n")

def annotate_english_data(endpoint, file_path, output_path):
    """Annotates English dataset with Karaka roles and POS tags."""
    print(f"Annotating English data: {file_path}")
    
    prompt_template = """
    Role: You are a linguist specializing in Paninian Karaka theory.
    
    Task: Annotate the following English sentence with Karaka roles and Part-of-Speech (POS) tags for each word.
    
    Sentence: "{sentence}"
    
    Output Format:
    Return the result as a list of words with their corresponding POS tag and Karaka role, separated by tabs or spaces.
    Example:
    Word [TAB] POS [TAB] Karaka
    
    Return ONLY the annotated data, no extra text.
    """
    
    results = []
    for sentence_text, raw_lines in parse_conll(file_path):
        print(f"Processing: {sentence_text}")
        response = annotate_sentence(endpoint, sentence_text, prompt_template)
        if response:
            results.append(response)
            
    write_annotated_file(output_path, results)
    print(f"Saved to: {output_path}")

def annotate_hindi_data(endpoint, file_path, output_path):
    """Annotates Hindi dataset with Karaka roles and POS tags."""
    print(f"Annotating Hindi data: {file_path}")
    
    prompt_template = """
    Role: You are a linguist specializing in Paninian Karaka theory applied to Hindi.
    
    Task: Annotate the following Hindi sentence with Karaka roles and Part-of-Speech (POS) tags for each word.
    
    Sentence: "{sentence}"
    
    Output Format:
    Return the result as a list of words with their corresponding POS tag and Karaka role, separated by tabs or spaces.
    Example:
    Word [TAB] POS [TAB] Karaka
    
    Return ONLY the annotated data, no extra text.
    """
    
    results = []
    for sentence_text, raw_lines in parse_conll(file_path):
        print(f"Processing: {sentence_text}")
        response = annotate_sentence(endpoint, sentence_text, prompt_template)
        if response:
            results.append(response)
            
    write_annotated_file(output_path, results)
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    endpoint = get_endpoint()
    if not endpoint:
        print("Failed to get endpoint. Exiting.")
        exit(1)
        
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    english_file = os.path.join(script_dir, "batch1_english.conll")
    hindi_file = os.path.join(script_dir, "batch1_hindi.conll")
    
    english_output = os.path.join(script_dir, "batch1_english_annotated.conll")
    hindi_output = os.path.join(script_dir, "batch1_hindi_annotated.conll")
    
    # Process files
    annotate_english_data(endpoint, english_file, english_output)
    annotate_hindi_data(endpoint, hindi_file, hindi_output)
