from app.tts.response_generator import generate_response
from app.tts.eleven_labs_tts import speak
import asyncio
def response_wrapper(text):
    generated_response = generate_response(text)
    asyncio.runspeak((generated_response))