from concurrent.futures import ThreadPoolExecutor
import os
import sys
import atexit

# def suppress_stderr():
#     devnull = os.open(os.devnull, os.O_WRONLY)
#     os.dup2(devnull, sys.stderr.fileno())

# suppress_stderr()

from app.stt.voice_recognition import VoiceAssistant
from app.models.groq_preprocess import cached_process_query
from app.query_processor import determine_function
from app.tts.response_generator import generate_response
from app.tts.eleven_labs_tts import speak

executor = ThreadPoolExecutor(max_workers=4)
atexit.register(lambda: executor.shutdown(wait=True))

def handle_recognized_command(text):
    if not text:
        print("[MAIN] Nothing recognized.")
        return

    print(f"[MAIN] Recognized: {text}")

    # Run TTS and processing in parallel
    executor.submit(lambda: speak(generate_response(text)))
    executor.submit(lambda: determine_function(cached_process_query(text)))

assistant = VoiceAssistant(hotword="vision",record_duration=6,on_recognized=handle_recognized_command)
assistant.start_hotword_listener()
