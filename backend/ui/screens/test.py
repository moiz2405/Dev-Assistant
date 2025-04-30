from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Header, Footer, Input, Label, Log

import asyncio
import os
import logging

logger = logging.getLogger("assistant")

class MainScreen(Screen):
    """Redesigned main screen with two stacked panels: logs and input."""

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical(id="main-vertical"):
            # Logs panel (upper, takes most of the space)
            with Vertical(id="logs-panel"):
                yield Label("Vision LOGS", id="logs-label")
                yield Log(highlight=True, id="log-widget")

            # Input panel (bottom, fixed size)
            with Vertical(id="input-panel"):
                yield Label("Ask Vision", id="input-label")
                yield Input(placeholder="Type your message here...", id="text-input")

        yield Footer()

    def on_mount(self) -> None:
        self.log_widget = self.query_one("#log-widget", Log)
        self.text_input = self.query_one("#text-input", Input)

        asyncio.create_task(self.monitor_log_file())

        logger.info("Voice Assistant UI started")
        logger.info("Monitoring logs in real-time")

    def write_to_log(self, message: str) -> None:
        logger.info(message)

    async def monitor_log_file(self) -> None:
        LOG_FILE = "backend/ui/logs/assistant.log"
        if not os.path.exists(LOG_FILE):
            self.log_widget.write_line("Waiting for log file to be created...")
            while not os.path.exists(LOG_FILE):
                await asyncio.sleep(0.5)
            self.log_widget.write_line("Log file found, monitoring now")

        position = os.path.getsize(LOG_FILE)

        while True:
            try:
                if not os.path.exists(LOG_FILE):
                    self.log_widget.write_line("Log file missing, waiting for recreation...")
                    position = 0
                    await asyncio.sleep(1)
                    continue

                current_size = os.path.getsize(LOG_FILE)
                if current_size > position:
                    with open(LOG_FILE, "r") as f:
                        f.seek(position)
                        new_lines = f.read().splitlines()
                        for line in new_lines:
                            if line.strip():
                                self.log_widget.write_line(line)
                    position = current_size
                    self.log_widget.scroll_end(animate=False)

                elif current_size < position:
                    self.log_widget.write_line("Log file reset detected")
                    position = current_size

            except Exception as e:
                self.log_widget.write_line(f"Error monitoring log: {e}")

            await asyncio.sleep(0.2)
