import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
def permutate(v):
    """Return all permutations of a list."""
    return list(permutations(v))

def prompt_gemini(prompt_text, api_key):
    """
    Sends a prompt to the Gemini API and returns the response.
    
    Args:
        prompt_text (str): The text prompt to send to the API.
        api_key (str): Your Gemini API key.
        
    Returns:
        str: The text response from the API.
    """
    url = "https://gemini.googleapis.com/v1alpha2/models/text-bison-001:generate"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "prompt": {
            "text": prompt_text
        },
        "temperature": 0.7,
        "maxOutputTokens": 500
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        result = response.json()
        return result.get("candidates", [{}])[0].get("content", "")
    else:
        return f"Error {response.status_code}: {response.text}"
#do the prompt here
# print(prompt_gemini("Hello, Gemini!", api_key))
