from concurrent.futures import ThreadPoolExecutor
import os
import sys
import atexit

# Suppress stderr
# def suppress_stderr():
#     devnull = os.open(os.devnull, os.O_WRONLY)
#     os.dup2(devnull, sys.stderr.fileno())

# suppress_stderr()

# Imports
from app.stt.voice_recognition import VoiceAssistant
from app.models.groq_preprocess import cached_process_query
from app.query_processor import determine_function
from app.tts.response_generator import generate_response
from app.tts.eleven_labs_tts import speak

# Shared ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=4)

# Ensure executor is properly shutdown on exit
atexit.register(lambda: executor.shutdown(wait=True))

# Handle recognized command
def handle_recognized_command(text):
    if not text:
        print("[MAIN] Nothing recognized.")
        return

    print(f"[MAIN] Recognized: {text}")

    # Run TTS and processing in parallel
    # executor.submit(lambda: speak(generate_response(text)))
    # executor.submit(lambda: determine_function(cached_process_query(text)))

# Start the assistant
assistant = VoiceAssistant(
    hotword="jarvis",
    record_duration=5,
    on_recognized=handle_recognized_command
)
assistant.start_hotword_listener()
