import edge_tts
import asyncio

async def speak(text):
    communicate = edge_tts.Communicate(text, voice='en-US-AriaNeural')
    await communicate.save("output.mp3")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(speak("Hello, this is a test with Edge TTS."))
