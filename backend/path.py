import sys
import os
import asyncio
import websockets
import json
from concurrent.futures import ThreadPoolExecutor
from app.stt.voice_recognition import VoiceAssistant
from app.models.groq_preprocess import cached_process_query
from app.query_processor import determine_function
from app.tts.response_generator import generate_response
from app.tts.edge_tts import speak_text
from app.functions.logger import logger

executor = ThreadPoolExecutor(max_workers=4)
UI_WS_URI = "ws://localhost:8765"

async def send_to_ui(message):
    try:
        async with websockets.connect(UI_WS_URI) as websocket:
            await websocket.send(json.dumps({"type": "log", "message": message}))
    except Exception as e:
        logger.error(f"[VOICE] WebSocket Error: {e}")

def run_speak_text(text):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(speak_text(generate_response(text)))
    except Exception as e:
        logger.error(f"[VOICE] Error in speaking text: {e}")

def handle_recognized_command(text):
    if not text:
        logger.info("[VOICE] Nothing recognized.")
        asyncio.run(send_to_ui("Nothing recognized."))
        return

    logger.info(f"[VOICE] Recognized: {text}")
    asyncio.run(send_to_ui(f"Recognized: {text}"))

    executor.submit(run_speak_text, text)
    executor.submit(lambda: determine_function(cached_process_query(text)))

assistant = VoiceAssistant(hotword="vision", record_duration=6, on_recognized=handle_recognized_command)

async def start_voice_assistant():
    logger.info("Starting hotword listener...")
    print("Starting hotword listener...")
    await asyncio.to_thread(assistant.start_hotword_listener)
    await send_to_ui("Hotword listener started.")
