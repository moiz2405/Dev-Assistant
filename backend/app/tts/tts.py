# tts_module.py
import edge_tts
import asyncio
import pygame

# Hardcoded voice (you can change this to any voice you prefer)
voice_model = "en-US-AndrewNeural"

async def speak(text):
    """
    Function to speak the given text using the hardcoded voice.
    
    Args:
    - text (str): The text to be spoken.
    """
    # Set the hardcoded voice for TTS
    communicate = edge_tts.Communicate(text, voice=voice_model)
    await communicate.save("output.mp3")

    # Initialize the pygame mixer
    pygame.mixer.init()
    
    # Load and play the saved audio file
    pygame.mixer.music.load("output.mp3")
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
    loop = asyncio.get_event_loop()
    loop.run_until_complete(speak(text))
