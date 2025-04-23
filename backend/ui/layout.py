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
        # Read the current log file and display its contents in the log panel
        self.logs = self.read_log_file()
        self.update("\n".join(self.logs))  # Update with raw text

    def append_log(self, message: str):
        self.logs.append(message)
        self.update("\n".join(self.logs))  # Update with raw text

    def read_log_file(self):
        """Read the logs from the log file and return as a list of log entries."""
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as log_file:
                return log_file.readlines()
        else:
            return ["Logs will appear here..."]

    async def tail_log_file(self):
        """Tail the log file and append new lines to the log panel."""
        while True:
            # Check for new lines
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r") as log_file:
                    log_file.seek(0, os.SEEK_END)  # Go to the end of the file
                    while True:
                        line = log_file.readline()
                        if line:
                            self.append_log(line.strip())
                        else:
                            await asyncio.sleep(0.1)  # Sleep briefly before checking for new lines
            else:
                await asyncio.sleep(1)  # Wait before retrying

class AssistantApp(App):
    def compose(self) -> None:
        self.log_panel = LogPanel(id="log_panel")
        yield self.log_panel  # Yield just the log panel

    async def on_startup(self) -> None:
        # Log to UI and terminal
        self.log_panel.append_log("🟢 App started")
        logger.info("🟢 App started")  # Log to terminal

        # Start tailing the log file in the background
        asyncio.create_task(self.log_panel.tail_log_file())  # Run tail_log_file asynchronously

if __name__ == "__main__":
    app = AssistantApp()  # Create an instance of AssistantApp
    app.run()  # Run the instance
