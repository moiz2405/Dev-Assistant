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
def handle_recognized_command(text, app: AssistantApp):
    """Callback for when hotword is recognized, update the UI log."""
    if not text:
        logger.info("[MAIN] Nothing recognized.")
        app.post_message(app.update_log_message("Nothing recognized."))
        return
    logger.info(f"[MAIN] Recognized: {text}")
    app.post_message(app.update_log_message(f"Recognized: {text}"))

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
async def start_hotword_listener(app: AssistantApp):
    """Run hotword listener asynchronously while keeping the UI responsive."""
    logger.info("Starting hotword listener...")
    print("Starting hotword listener...")  # Debug print to confirm it's being called
    await asyncio.to_thread(assistant.start_hotword_listener)
    logger.info("Hotword listener started.")
    app.post_message(app.update_log_message("Hotword listener started."))
    print("Hotword listener started.")  # Debug print to confirm it's running


# Run the assistant UI and hotword listener
async def run_ui_and_hotword_listener():
    """Run both the UI and the hotword listener concurrently."""
    app = AssistantApp()
    
    # Run the UI in the background
    ui_task = asyncio.create_task(app.run_async())
    
    # Start the hotword listener in the background
    listener_task = asyncio.create_task(start_hotword_listener(app))
    
    # Wait for both tasks to finish
    await asyncio.gather(ui_task, listener_task)
if __name__ == "__main__":
    try:
        # Start the combined UI and hotword listener
        asyncio.run(run_ui_and_hotword_listener())

    except KeyboardInterrupt:
        logger.info("Ctrl+C detected. Stopping the assistant and UI.")
        # Cleanup when stopping
        assistant.stop()  # Assuming you have a stop method in your VoiceAssistant class
        sys.exit(0)
