import asyncio
import logging
import os
from textual.app import App
from textual.widgets import Static

LOG_FILE = "logs/assistant.log"

# Set up terminal logger
logger = logging.getLogger("AssistantApp")
logger.setLevel(logging.DEBUG)
stream = logging.StreamHandler()
stream.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(stream)

class LogPanel(Static):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logs = []

    def on_mount(self):
        self.update("🟢 Waiting for logs...")

    def append_log(self, message: str):
        self.logs.append(message)
        self.update("\n".join(self.logs[-100:]))  # Show last 100 lines

# Read all new lines after the last known length
def get_new_log_lines(last_line_count: int) -> tuple[list[str], int]:
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            if len(lines) > last_line_count:
                new_lines = lines[last_line_count:]
                return [line.strip() for line in new_lines], len(lines)
    return [], last_line_count

class AssistantApp(App):
    def compose(self):
        self.log_panel = LogPanel()
        yield self.log_panel

    async def on_startup(self):
        self.log_panel.append_log("🟢 App started")
        logger.info("🟢 App started")
        asyncio.create_task(self.watch_log_file())

    async def watch_log_file(self):
        last_line_count = 0
        while True:
            new_lines, last_line_count = get_new_log_lines(last_line_count)
            for line in new_lines:
                self.log_panel.append_log(line)
            await asyncio.sleep(1)  # Poll every 1s

if __name__ == "__main__":
    AssistantApp().run()
