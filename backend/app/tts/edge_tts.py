import os
import sys
import io
import tempfile
import asyncio
import edge_tts
import pygame

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

voice_model = "en-US-AndrewNeural"

def suppress_stdout_stderr():
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()

def restore_stdout_stderr():
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

async def speak(text):
    suppress_stdout_stderr()

    try:
        # Create a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            filename = tmp_file.name

        communicate = edge_tts.Communicate(text, voice=voice_model)
        await communicate.save(filename)

        restore_stdout_stderr()

        # Wait a bit to ensure file system flush (especially on Windows)
        await asyncio.sleep(0.1)

        # Initialize pygame mixer
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"ERROR | Error in speaking text: {e}")
    finally:
        # Cleanup the temp file
        if os.path.exists(filename):
            os.remove(filename)

async def speak_text(text):
    await speak(text)
