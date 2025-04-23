# voice_app.py
import sys
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.stt.voice_recognition import VoiceAssistant
from app.models.groq_preprocess import cached_process_query
from app.query_processor import determine_function
from app.tts.response_generator import generate_response
from app.tts.edge_tts import speak_text
from app.functions.logger import logger

executor = ThreadPoolExecutor(max_workers=4)

# Run the speech synthesis in a separate thread
def run_speak_text(text):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        asyncio.run(speak_text(generate_response(text)))
    except Exception as e:
        logger.error(f"[VOICE] Error in speaking text: {e}")

# Initialize UI reference (to be injected later)
app_instance = None

def inject_ui(app):
    global app_instance
    app_instance = app

def handle_recognized_command(text):
    if not text:
        logger.info("[VOICE] Nothing recognized.")
        if app_instance:
            app_instance.post_message(app_instance.update_log_message("Nothing recognized."))
        return

    logger.info(f"[VOICE] Recognized: {text}")
    if app_instance:
        app_instance.post_message(app_instance.update_log_message(f"Recognized: {text}"))

    executor.submit(run_speak_text, text)
    executor.submit(lambda: determine_function(cached_process_query(text)))

# Start voice assistant with hotword "vision"
assistant = VoiceAssistant(hotword="vision", record_duration=6, on_recognized=handle_recognized_command)

async def start_voice_assistant():
    logger.info("Starting hotword listener...")
    print("Starting hotword listener...")
    await asyncio.to_thread(assistant.start_hotword_listener)
    logger.info("Hotword listener started.")
    if app_instance:
        app_instance.post_message(app_instance.update_log_message("Hotword listener started."))
    print("Hotword listener started.")

if __name__ == "__main__":
    try:
        asyncio.run(start_voice_assistant())
    except KeyboardInterrupt:
        logger.info("Ctrl+C detected. Stopping voice assistant.")
        assistant.stop()
        sys.exit(0)
