import edge_tts
import asyncio
import pygame
import os
import datetime

# Hardcoded voice (you can change this to any voice you prefer)
voice_model = "en-US-AndrewNeural"
responses_dir = "responses"

# Ensure the responses directory exists
os.makedirs(responses_dir, exist_ok=True)

async def speak(text):
    """
    Function to speak the given text using the hardcoded voice.
    
    Args:
    - text (str): The text to be spoken.
    """
    # Create a timestamped filename for the new response
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{responses_dir}/res_voice_{timestamp}.mp3"  # or ".wav" if you prefer

    # Set the hardcoded voice for TTS
    communicate = edge_tts.Communicate(text, voice=voice_model)
    await communicate.save(filename)

    # Delete the previous response if it exists
    # List all files in the response directory, sorted by creation time (oldest first)
    existing_files = sorted(
        [f for f in os.listdir(responses_dir) if f.endswith(".mp3")], 
        key=lambda f: os.path.getctime(os.path.join(responses_dir, f))
    )

    if len(existing_files) > 1:  # If there's more than one file, delete the oldest
        oldest_file = existing_files[0]
        os.remove(os.path.join(responses_dir, oldest_file))  # Remove the oldest response

    # Initialize the pygame mixer
    pygame.mixer.init()
    
    # Load and play the saved audio file
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    # Wait until the audio finishes playing
    while pygame.mixer.music.get_busy():  
        pygame.time.Clock().tick(10)

def speak_text(text):
    """
    Callable function that triggers the TTS for the given text.
    
    Args:
    - text (str): The text to be spoken.
    """
    # print(f"Edge_tts called with {text}")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(speak(text))
