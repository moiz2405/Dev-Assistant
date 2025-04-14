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
import asyncio

async def handle_tts(text: str):
    response = generate_response(text)
    await speak(response)

async def handle_action(text: str):
    processed = process_query(text)
    determine_function(processed)

def handle_recognized_command(text: str):
    if text:
        print(f"[MAIN] Recognized: {text}")
        asyncio.run(run_parallel_tasks(text))
    else:
        print("[MAIN] Nothing recognized.")

async def run_parallel_tasks(text: str):
    await asyncio.gather(
        handle_tts(text),
        handle_action(text)
    )

# Start hotword detection and taking user query in natural language
assistant = VoiceAssistant(hotword="jarvis", record_duration=4, on_recognized=handle_recognized_command)
assistant.start_hotword_listener()