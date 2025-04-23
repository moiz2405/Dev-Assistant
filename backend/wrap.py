import sys
import os
import asyncio
import multiprocessing
from ui.layout import AssistantApp
from path import start_voice_assistant, send_to_ui
if sys.stdin.closed:
    sys.stdin = os.fdopen(sys.stdin.fileno(), 'r')
def run_ui():
    app = AssistantApp()
    asyncio.run(app.run_async())  # Ensure you use asyncio to run the app

def run_assistant():
    asyncio.run(start_voice_assistant())

if __name__ == "__main__":
    # Avoid I/O issues by keeping the UI and assistant in the same event loop
    ui_process = multiprocessing.Process(target=run_ui)
    assistant_process = multiprocessing.Process(target=run_assistant)

    ui_process.start()
    assistant_process.start()

    ui_process.join()
    assistant_process.join()
