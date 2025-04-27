import os
import asyncio
import time
import logging
from prompt_toolkit.application import Application
from prompt_toolkit.widgets import Frame, TextArea
from prompt_toolkit.layout import Layout, HSplit
from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyBindings
from rich.text import Text
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live

# Logging setup
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "assistant.log")
os.makedirs(LOG_DIR, exist_ok=True)

debug_logger = logging.getLogger("VoiceAssistantUI")
debug_logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("debug_ui.log")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
debug_logger.addHandler(file_handler)


# Rich Console
console = Console()

# Shared log buffer for UI
log_text = TextArea(text="", scrollbar=True, read_only=True, wrap_lines=False)
style = Style.from_dict({
    "frame.border": "cyan",
    "textarea": "white",
})


async def monitor_log():
    """Continuously monitor the log file and update the UI."""
    debug_logger.info("Starting log monitor")
    
    # Create log file if not exists
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write("Log file created\n")
        debug_logger.info(f"Created log file: {LOG_FILE}")

    # Start at the beginning of the file to make sure we catch everything
    position = 0
    debug_logger.info(f"Initial position: {position}")

    while True:
        try:
            if not os.path.exists(LOG_FILE):
                debug_logger.warning("Log file no longer exists")
                position = 0
                await asyncio.sleep(1)
                continue
                
            current_size = os.path.getsize(LOG_FILE)
            debug_logger.debug(f"Current file size: {current_size}, position: {position}")

            if current_size < position:
                debug_logger.info("Log file truncated")
                position = 0

            if current_size > position:
                debug_logger.info(f"New content detected: {current_size - position} bytes")
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    f.seek(position)
                    content = f.read()
                    position = f.tell()
                    
                    if content:
                        lines = content.splitlines()
                        debug_logger.info(f"Read {len(lines)} new lines")
                        
                        for line in lines:
                            if line.strip():
                                # Extract content part (remove timestamp)
                                if " - " in line:
                                    content = line.split(" - ", 1)[1]
                                    log_text.text += content + "\n"
                                    debug_logger.debug(f"Added log line: {content}")
                                else:
                                    log_text.text += line + "\n"
                                    debug_logger.debug(f"Added raw line: {line}")
                
                # Try different ways to update the UI
                app.invalidate()
                
        except Exception as e:
            debug_logger.error(f"Error monitoring log: {str(e)}", exc_info=True)

        await asyncio.sleep(0.3)

def write_test_logs():
    """Write some initial test logs to the file."""
    messages = [
        "Initial test log entry 1",
        "Initial test log entry 2",
        "Initial test log entry 3"
    ]
    
    for msg in messages:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp} - {msg}\n")
        debug_logger.info(f"Wrote test log: {msg}")

# Keybindings
kb = KeyBindings()

@kb.add("c-c")
@kb.add("q")
def _(event):
    "Quit the application."
    event.app.exit()


# App Layout
root_container = HSplit([
    Frame(title="V.I.S.I.O.N - Realtime Logs", body=log_text),
])

layout = Layout(root_container)

# Application
app = Application(
    layout=layout,
    key_bindings=kb,
    full_screen=True,
    style=style,
)

async def main():
    # Write some test logs before starting monitoring
    # write_test_logs()
    
    # Start monitoring
    monitor_task = asyncio.create_task(monitor_log())
    
    # Run the app
    try:
        await app.run_async()
    finally:
        # Make sure to clean up the task when application exits
        monitor_task.cancel()
        await asyncio.gather(monitor_task, return_exceptions=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        debug_logger.critical(f"Application crashed: {str(e)}", exc_info=True)
