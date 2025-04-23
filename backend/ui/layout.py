import asyncio
import logging
import os
from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.containers import Container

LOG_FILE = "logs/assistant.log"

logger = logging.getLogger("AssistantApp")
logger.setLevel(logging.DEBUG)
stream = logging.StreamHandler()
stream.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(stream)

class LogPanel(Static):
    def on_mount(self):
        self.logs = []
        self.update("🟢 Waiting for logs...")

    def append_log(self, line: str):
        self.logs.append(line)
        self.update("\n".join(self.logs[-100:]))

class AssistantApp(App):
    CSS_PATH = None  # You can add custom CSS for styling

    def compose(self) -> ComposeResult:
        self.log_panel = LogPanel()
        yield Container(self.log_panel)

    async def on_startup(self):
        self.log_panel.append_log("🟢 App started")
        logger.info("🟢 App started")

        # Start background file watcher
        self.log_task = asyncio.create_task(self.watch_logs())

    async def watch_logs(self):
        """Tails the log file in a non-blocking async-friendly way."""
        if not os.path.exists(LOG_FILE):
            open(LOG_FILE, "w").close()

        # Keep track of the last position we read
        position = 0
        
        while True:
            # Open the file on each iteration to get fresh data
            with open(LOG_FILE, "r") as f:
                # Get file size
                f.seek(0, os.SEEK_END)
                file_size = f.tell()
                
                # If the file size has increased, read the new content
                if file_size > position:
                    f.seek(position)
                    new_lines = f.read()
                    position = file_size
                    
                    # Process any complete lines
                    for line in new_lines.splitlines():
                        if line:
                            self.log_panel.append_log(line.strip())
            
            # Wait a short time before checking again
            await asyncio.sleep(0.1)

if __name__ == "__main__":
    AssistantApp().run()
