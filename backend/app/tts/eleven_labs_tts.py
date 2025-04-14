import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from functools import lru_cache
from multiprocessing import Process
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Load .env variables only once
load_dotenv()

# Global cache for client
_client = None

def get_eleven_client():
    global _client
    if _client is None:
        _client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
    return _client

# Cached audio for repeat phrases
@lru_cache(maxsize=100)
def get_audio_from_text(text: str):
    client = get_eleven_client()
    return client.text_to_speech.convert(
        text=text,
        voice_id="JBFqnCBsd6RMkjVDRZzb",  # Your selected voice
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )

# Background audio player
def _play_audio(audio):
    play(audio)

# Synchronous speak (non-blocking)
def speak(text: str):
    if not text.strip():
        return
    audio = get_audio_from_text(text)
    Process(target=_play_audio, args=(audio,)).start()

# Optional: Asynchronous speak (if using with FastAPI or asyncio apps)
executor = ThreadPoolExecutor()

async def speak_async(text: str):
    if not text.strip():
        return
    audio = get_audio_from_text(text)
    await asyncio.get_event_loop().run_in_executor(executor, play, audio)
