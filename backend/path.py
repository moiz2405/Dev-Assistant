from concurrent.futures import ThreadPoolExecutor
import os
import sys

def suppress_stderr():
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, sys.stderr.fileno())

suppress_stderr()

from app.stt.voice_recognition import VoiceAssistant
from app.models.groq_preprocess import process_query
from app.query_processor import determine_function
from app.tts.response_generator import generate_response
from app.tts.eleven_labs_tts import speak

# Create a shared ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=4)

def handle_recognized_command(text):
    if not text:
        print("[MAIN] Nothing recognized.")
        return

    print(f"[MAIN] Recognized: {text}")

    # Task 1: TTS Pathway
    def run_tts_pipeline():
        response = generate_response(text)
        speak(response)

    # Task 2: Query Processor Pathway
    def run_action_pipeline():
        processed = process_query(text)
        determine_function(processed)

    # Run both in parallel
    executor.submit(run_tts_pipeline)
    executor.submit(run_action_pipeline)

# Start assistant
assistant = VoiceAssistant(
    hotword="jarvis",
    record_duration=4,
    on_recognized=handle_recognized_command
)
assistant.start_hotword_listener()
