import requests
import pyaudio
import wave
import threading
import time
import json
import websocket
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Deepgram API Key from .env file
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
DEEPGRAM_URL = f"https://api.beta.deepgram.com/v1/speak?model=${MODEL_NAME}&performance=some&encoding=linear16&sample_rate=24000"

# Microphone settings
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Create PyAudio instance
p = pyaudio.PyAudio()

# Function to record from the microphone and send audio to Deepgram API
def record_and_stream():
    # Create the audio stream from microphone
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE)
    
    # Setup WebSocket for Deepgram API connection
    ws = websocket.WebSocketApp(
        DEEPGRAM_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    # Start the WebSocket connection in a separate thread
    ws_thread = threading.Thread(target=ws.run_forever)
    ws_thread.start()

    # Continuously read from microphone and send to Deepgram WebSocket
    while True:
        data = stream.read(CHUNK_SIZE)
        ws.send(data, opcode=websocket.ABNF.OPCODE_BINARY)
        
    # Close the microphone stream when done
    stream.stop_stream()
    stream.close()

# WebSocket callbacks
def on_open(ws):
    print("Connection to Deepgram opened")

def on_message(ws, message):
    # Handle transcription response from Deepgram
    try:
        response = json.loads(message)
        if response.get("channel"):
            transcript = response["channel"]["alternatives"][0]["transcript"]
            print(f"Transcript: {transcript}")
            # Here you can use the transcribed text for further processing
    except json.JSONDecodeError as e:
        print("Error decoding response:", e)

def on_error(ws, error):
    print(f"WebSocket Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Connection to Deepgram closed")

# Start the transcription process
def start_transcription():
    record_and_stream()

if __name__ == "__main__":
    start_transcription()
