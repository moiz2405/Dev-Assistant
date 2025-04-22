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
from ui.layout import AssistantApp

executor = ThreadPoolExecutor(max_workers=4)

# Suppress stderr for warnings and errors
def suppress_stderr():
    """Suppress stderr output (warnings/errors) by redirecting it to devnull."""
    original_stderr = sys.stderr
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, sys.stderr.fileno())
    return original_stderr

# original_stderr = suppress_stderr()

def handle_recognized_command(text):
    if not text:
        logger.info("[MAIN] Nothing recognized.")   
        return
    logger.info(f"[MAIN] Recognized: {text}")   

    executor.submit(run_speak_text, text)
    executor.submit(lambda: determine_function(cached_process_query(text)))

# Run the speech synthesis in a separate thread
def run_speak_text(text):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        asyncio.run(speak_text(generate_response(text)))
    except Exception as e:
        logger.error(f"[MAIN] Error in speaking text: {e}")  # Log any error that occurs

# Start voice assistant with hotword "vision"
assistant = VoiceAssistant(hotword="vision", record_duration=6, on_recognized=handle_recognized_command)

def start_assistant():
    """Start the hotword listener and the voice assistant."""
    try:
        # Start the voice assistant with hotword listener
        assistant.start_hotword_listener()
        logger.info("Voice assistant is listening for hotword...")
    except KeyboardInterrupt:
        logger.info("Voice assistant stopped.")
        cleanup()

def cleanup():
    """Cleanup resources and shutdown the application."""
    logger.info("Shutting down the application.")
    # Additional cleanup steps can be placed here if needed
    sys.exit(0)

if __name__ == "__main__":
    try:
        # Start the voice assistant
        start_assistant()

        # After hotword listener is started, start the UI
        logger.info("Now starting the UI...")
        asyncio.run(AssistantApp().run_async())

    except KeyboardInterrupt:
        logger.info("Ctrl+C detected. Stopping the assistant and UI.")
        cleanup()
