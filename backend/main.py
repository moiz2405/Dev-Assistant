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
#access the last query
def handle_recognized_command(text):
    if text:
        print(f"[MAIN] Recognized: {text}")
        generated_response = generate_response(text)
        speak(generated_response)
        processed_query = process_query(text)
        determine_function(processed_query)
        # Call your query processor or route it here
    else:
        print("[MAIN] Nothing recognized.")

#start hotword detection and taking user query in natural language
assistant = VoiceAssistant(hotword="jarvis", record_duration=4,on_recognized=handle_recognized_command)
assistant.start_hotword_listener()
