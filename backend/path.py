import sys
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.stt.voice_recognition import VoiceAssistant
from app.models.groq_preprocess import cached_process_query
from app.query_processor import determine_function
from app.tts.response_generator import generate_response
from app.tts.edge_tts import speak_text
# from app.functions.logger.logger_setup import logger\
from app.logger.logger_setup import logger

def suppress_stderr():
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, sys.stderr.fileno())

suppress_stderr()

executor = ThreadPoolExecutor(max_workers=4)

# Run the speech synthesis in a separate thread
def run_speak_text(text):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        asyncio.run(speak_text(generate_response(text)))
    except Exception as e:
        logger.error(f"Error in speaking text: {e}")

# Handle recognized text
def handle_recognized_command(text):
    if not text:
        logger.info("Nothing recognized.")
        return

    logger.info(f"Recognized: {text}")
    
    executor.submit(run_speak_text, text)
    executor.submit(lambda: determine_function(cached_process_query(text)))

# Start voice assistant with hotword "vision"
assistant = VoiceAssistant(hotword="vision", record_duration=6, on_recognized=handle_recognized_command)

async def start_voice_assistant():
    logger.info("Starting hotword listener...")
    # Remove print statement and only use logger
    await asyncio.to_thread(assistant.start_hotword_listener)
    logger.info("Hotword listener started.")
    # Remove print statement and only use logger

if __name__ == "__main__":
    asyncio.run(start_voice_assistant())