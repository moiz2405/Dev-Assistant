import os
import dotenv
import google.generativeai as genai
from functools import lru_cache

# Load API Key once
dotenv.load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Instantiate model once globally
_model = genai.GenerativeModel("gemini-2.0-flash")

# Define preprompt once
PROMPT = """
You are Jarvis, a poised and exceptionally articulate English butler.

You respond with short, elegant replies in a positive and natural manner. Begin your response with phrases like “Certainly, sir,” “At once,” or “Very good,” when given a command.

Maintain a refined, respectful tone at all times. Avoid slang and unnecessary verbosity. Keep your responses compact, composed, and helpful.
""".strip()

# Cached version of the function
@lru_cache(maxsize=100)
def generate_response(text: str) -> str:
    if not text.strip():
        return "Pardon, sir? I didn’t quite catch that."

    prompt = f"{PROMPT}\nUser: {text.strip()}"
    
    try:
        response = _model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[ERROR] Failed to generate response: {e}")
        return "Apologies, sir. I'm having trouble responding at the moment."
