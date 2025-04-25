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
    position = 0

    # Create log file if not exists
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write("Log file created\n")

    try:
        position = os.path.getsize(LOG_FILE)
    except Exception as e:
        debug_logger.error(f"Error reading log file size: {e}")

    while True:
        try:
            current_size = os.path.getsize(LOG_FILE)

            if current_size < position:
                # Truncated or rotated
                position = 0

            if current_size > position:
                with open(LOG_FILE, "r") as f:
                    f.seek(position)
                    lines = f.readlines()
                    position = f.tell()

                    for line in lines:
                        if line.strip():
                            log_text.buffer.insert_text(line)
        except Exception as e:
            debug_logger.error(f"Error monitoring log: {str(e)}")

        await asyncio.sleep(0.3)


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
    asyncio.create_task(monitor_log())
    await app.run_async()

if __name__ == "__main__":
    asyncio.run(main())
