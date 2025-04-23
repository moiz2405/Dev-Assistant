import asyncio
import logging
from textual.app import App
from textual.widgets import Static
import os
import time

# Set up logger for terminal output
logger = logging.getLogger("AssistantApp")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

LOG_FILE = "logs/assistant.log"  # Ensure the log file exists in the logs folder

class LogPanel(Static):
    def on_mount(self) -> None:
        self.logs = self.read_log_file()
        self.update("\n".join(self.logs))  # Update with raw text

    def append_log(self, message: str):
        self.logs.append(message)
        self.update("\n".join(self.logs[-100:]))  # Keep last 100 lines for performance

    def read_log_file(self):
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as log_file:
                return [line.strip() for line in log_file.readlines()]
        return ["Logs will appear here..."]

class AssistantApp(App):
    def compose(self):
        self.log_panel = LogPanel()
        yield self.log_panel

    async def on_startup(self):
        self.log_panel.append_log("🟢 App started")
        logger.info("🟢 App started")
        asyncio.create_task(self.tail_log_file())

    async def tail_log_file(self):
        """Non-blocking log watcher that tails new lines from file."""
        last_line_count = 0
        while True:
            try:
                # Open the file asynchronously (non-blocking)
                await asyncio.to_thread(self.read_new_logs, last_line_count)
            except Exception as e:
                logger.warning(f"Error reading log file: {e}")
            await asyncio.sleep(1)  # Check for updates every 1 second

    def read_new_logs(self, last_line_count):
        """Reads new lines from the log file."""
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            new_lines = lines[last_line_count:]
            for line in new_lines:
                self.log_panel.append_log(line.strip())
            return len(lines)

if __name__ == "__main__":
    app = AssistantApp()  # Create an instance of AssistantApp
    app.run()  # Run the instance
