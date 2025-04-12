# voice processor - cleans the audio 
#     1) passes it to query_processor for intent handling 
#     2) passes to text-to-speech model for responce to user

import os
import google.generativeai as genai

# Get API key from terminal export (no .env)
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please export it in your terminal before running this script.")

# Configure Gemini
genai.configure(api_key=api_key)

# Use Gemini Flash model
model = genai.GenerativeModel("gemini-2.0-flash")

def voice_processor(description: str) -> str:
    """
    Processes the given text using Gemini:
    - ONLY corrects grammar and typos.
    - Does NOT answer questions or add extra information.
    - Keeps commands, file paths, directory names, etc., untouched.

    Example input:


