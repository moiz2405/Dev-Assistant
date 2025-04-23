# wrap.py
#calls both main.py and layout.py to run together 
import multiprocessing
import subprocess
import time

def run_ui():
    subprocess.run(["python", "ui/layout.py"])

def run_voice_assistant():
    subprocess.run(["python", "path.py"])

if __name__ == "__main__":
    ui_process = multiprocessing.Process(target=run_ui)
    assistant_process = multiprocessing.Process(target=run_voice_assistant)

    ui_process.start()
    time.sleep(2)  # Wait for WebSocket server to start
    assistant_process.start()

    ui_process.join()
    assistant_process.join()
