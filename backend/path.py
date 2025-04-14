import os
import sys
import concurrent.futures

def suppress_stderr():
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, sys.stderr.fileno())

suppress_stderr()

from app.stt.voice_recognition import VoiceAssistant
from app.models.groq_preprocess import process_query
from app.query_processor import determine_function
from app.tts.response_generator import generate_response
from app.tts.eleven_labs_tts import speak

# Access the last query
def handle_recognized_command(text):
    if text:
        print(f"[MAIN] Recognized: {text}")

        # Use ThreadPoolExecutor to run both `generate_response` and `speak` concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_response = executor.submit(generate_response, text)
            future_speech = executor.submit(speak, future_response.result())

        # Use another ThreadPoolExecutor to run `process_query` and `determine_function` concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_processed_query = executor.submit(process_query, text)
            future_determine_function = executor.submit(determine_function, future_processed_query.result())

    else:
        print("[MAIN] Nothing recognized.")

# Start hotword detection and taking user query in natural language
assistant = VoiceAssistant(hotword="jarvis", record_duration=4, on_recognized=handle_recognized_command)
assistant.start_hotword_listener()
