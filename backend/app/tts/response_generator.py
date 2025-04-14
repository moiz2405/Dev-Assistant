# generates response from STT from user, taken from voice recognition and calls eleven_labs_tts
import os
import dotenv
import google.generativeai as genai

# Load API Key from .env
dotenv.load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Define a butler-like preprompt
PROMPT = """
You are Jarvis, a poised and exceptionally articulate English butler.

You respond with short, elegant replies in a positive and natural manner. Begin your response with phrases like “Certainly, sir,” “At once,” or “Very good,” when given a command.

Maintain a refined, respectful tone at all times. Avoid slang and unnecessary verbosity. Keep your responses compact, composed, and helpful.
"""

# Create a callable bot function
def generate_response(text: str) -> str:
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    # Merge preprompt and user input into the first message
    prompt = f"{PROMPT}\nUser: {text}"
    
    response = model.generate_content(prompt)
    
    return response.text.strip()


# Example usage
# if __name__ == "__main__":
#     user_input = "open whatsapp"
#     reply = generate_response(user_input)
#     print(reply)
