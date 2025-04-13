import httpx
import logging
import threading
import pyaudio
from deepgram import DeepgramClient, DeepgramClientOptions, LiveTranscriptionEvents, LiveOptions

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define the audio stream from the microphone
CHUNK_SIZE = 1024  # Size of each audio chunk (in bytes)
FORMAT = pyaudio.paInt16  # Format for audio (16-bit PCM)
CHANNELS = 1  # Mono audio
RATE = 16000  # Sample rate (Hz)
DEVICE_INDEX = None  # Default device, change this if necessary

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open the microphone stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE,
                input_device_index=DEVICE_INDEX)

# Create Deepgram Client
deepgram = DeepgramClient()

# WebSocket URL for Deepgram
dg_connection = deepgram.listen.websocket.v("1")

# Define the callback function for receiving transcriptions
def on_message(self, result, **kwargs):
    sentence = result.channel.alternatives[0].transcript
    if len(sentence) == 0:
        return
    print(f"Transcript: {sentence}")

# Connect to Deepgram WebSocket for live transcription
dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)

def mic_stream():
    try:
        # Start the WebSocket connection to Deepgram
        options = LiveOptions(model="nova-3")
        print("\n\nRecording... Press Enter to stop...\n\n")
        
        # Check if the connection is successful
        if not dg_connection.start(options):
            print("Failed to start connection")
            return
        
        while True:
            # Read microphone data in chunks
            audio_data = stream.read(CHUNK_SIZE)
            if audio_data:
                # Log the audio data size to confirm data is being received
                print(f"Sending audio data (size: {len(audio_data)} bytes)...")
                dg_connection.send(audio_data)
            else:
                print("No audio data received.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the WebSocket connection
        dg_connection.finish()
        print("Finished")

# Start the microphone stream in a separate thread
thread = threading.Thread(target=mic_stream)
thread.start()

# Wait for the user to press Enter to stop recording
input("Press Enter to stop recording...\n")

# Stop the stream and close everything
stream.stop_stream()
stream.close()
p.terminate()
thread.join()

print("Stopped")
