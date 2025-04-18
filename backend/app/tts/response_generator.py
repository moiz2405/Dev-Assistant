import os
import json
import dotenv
from functools import lru_cache
import google.generativeai as genai

# === Setup === #
dotenv.load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

_model = genai.GenerativeModel("gemini-2.0-flash")

PROMPT = """
You are Jarvis, a poised and exceptionally articulate English butler.
Dont give a Full response unless asked to, dont ask questions dont suggest.
Do not repeat the command, never
You respond with short, elegant replies in a positive and natural manner. Begin your response with phrases like “Certainly, sir,” “At once,” or “Very good,” when given a command.

Maintain a refined, respectful tone at all times. Avoid slang and unnecessary verbosity. Keep your responses compact, composed, and helpful.
""".strip()

# === Persistent Cache === #
CACHE_PATH = "response_cache.json"

if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH, "r") as f:
        cache = json.load(f)
else:
    cache = {}

def save_cache():
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)

def normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())

# === Cached Response Function === #
@lru_cache(maxsize=100)  # Also keep in memory
def generate_response(text: str) -> str:
    if not text.strip():
        return "Pardon, sir? I didn’t quite catch that."

    norm_text = normalize(text)

    if norm_text in cache:
        print("[RESPONSE_CACHE HIT]")
        return cache[norm_text]

    print("[RESPONSE_CACHE MISS]")
    prompt = f"{PROMPT}\nUser: {text.strip()}"

    try:
        response = _model.generate_content(prompt)
        reply = response.text.strip()
        cache[norm_text] = reply
        save_cache()
        print(reply)
        return reply
    except Exception as e:
        print(f"[ERROR] Failed to generate response: {e}")
        return "Apologies, sir. I'm having trouble responding at the moment."
