import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play

# Load API Key
load_dotenv()
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# Define reusable speak function
def speak(text: str):
    if not text.strip():
        return  # Skip empty strings

    audio = client.text_to_speech.convert(
        text=text,
        voice_id="JBFqnCBsd6RMkjVDRZzb",  # Your selected voice
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    play(audio)
