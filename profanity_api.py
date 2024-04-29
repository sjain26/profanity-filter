import os
import json
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from janome.tokenizer import Tokenizer
import re
from nltk.tokenize import word_tokenize

# Initialize the FastAPI application
app = FastAPI()
# Configure CORS (adjust the origins as per your requirement)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the forbidden words once when the server starts
def load_forbidden_words(directory_path):
    all_strings = []
    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    all_strings.extend(data)
    return all_strings

directory_path = "data"
forbidden_words = load_forbidden_words(directory_path)

# Tokenizer for Japanese
tokenizer = Tokenizer()

def check_language(text):
    japanese_regex = r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f]'
    return 'ja' if re.search(japanese_regex, text) else "en"

def censor_text(input_string, forbidden_list):

    language = check_language(input_string)
    if language == "ja":
        tokens = tokenizer.tokenize(input_string)
        words = [token.surface for token in tokens]  # Extract the surface attribute
    else:
        words = word_tokenize(input_string)

    censored_words = ['*' * len(word) if word.lower() in forbidden_list else word for word in words]
    return ' '.join(censored_words)


@app.get("/profanity_filter")
async def profanity_filter(input_string: str):
    censored_message = censor_text(input_string, forbidden_words)
    return {"output_string": censored_message}

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
