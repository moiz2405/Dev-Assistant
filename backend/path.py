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

# Executor will manage threads for tasks, limit to 4 as per original config
executor = ThreadPoolExecutor(max_workers=4)

# Custom print function to avoid recursion
def custom_print(message):
    """Custom print function to avoid recursion, print to stdout"""
    sys.stdout.write(message + '\n')  # Write directly to stdout (without recursion)

# Suppress stderr for warnings and errors
def suppress_stderr():
    """Suppress stderr output (warnings/errors) by redirecting it to devnull."""
    original_stderr = sys.stderr
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, sys.stderr.fileno())
    return original_stderr


original_stderr = suppress_stderr()

def handle_recognized_command(text):
    if not text:
        logger.info("[MAIN] Nothing recognized.")   
        return
    logger.info(f"[MAIN] Recognized: {text}")   # Log it for records

    # Submit speech synthesis task in the executor
    executor.submit(run_speak_text, text)

    # Run other processing tasks asynchronously or in parallel
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
assistant.start_hotword_listener()
