from textual.screen import Screen
from textual.app import ComposeResult, on
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Button, Label, Log

from widgets.dynamic_element import DynamicVisualElement
from widgets.status_indicator import StatusIndicator
import asyncio
import time
import os

LOG_FILE = "backend/ui/logs/assistant.log"

class MainScreen(Screen):
    """Main application screen with split panels."""

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header()

        with Horizontal(id="main-container"):
            # Main panel with visual elements
            with Vertical(id="main-panel"):
                yield StatusIndicator(id="status-indicator")
                yield DynamicVisualElement(id="dynamic-element")
                yield Input(placeholder="Type your message here...", id="text-input")
                
                with Horizontal(id="voice-controls"):
                    yield Button("Toggle Mic", variant="primary", id="toggle-mic")
                    yield Button("Clear Input", variant="warning", id="clear-input")
                    yield Button("Submit", variant="success", id="submit-message")

            # Logs panel
            with Vertical(id="logs-panel"):
                yield Label("Monitor Logs", id="logs-label")
                yield Log(highlight=True, id="log-widget")

        yield Footer()

    def on_mount(self) -> None:
        """Called when the screen is mounted."""
        # Query widgets
        self.log_widget = self.query_one("#log-widget", Log)
        self.dynamic_element = self.query_one("#dynamic-element", DynamicVisualElement)
        self.status_indicator = self.query_one("#status-indicator", StatusIndicator)
        self.text_input = self.query_one("#text-input", Input)

        # Ensure logs folder exists
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

        # Start monitoring logs
        asyncio.create_task(self.monitor_log_file())

        # Write startup logs
        self.write_to_log("Voice Assistant UI started")
        self.write_to_log("Monitoring logs in real-time")

    def write_to_log(self, message: str) -> None:
        """Write a log entry to file and UI."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {message}"

        try:
            with open(LOG_FILE, "a") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            self.log_widget.write_line(f"Error writing to log file: {e}")

        self.log_widget.write_line(log_entry)

    @on(Button.Pressed, "#toggle-mic")
    def toggle_microphone(self) -> None:
        """Toggle microphone state."""
        self.status_indicator.toggle_mic()
        self.dynamic_element.toggle_status()

        status = "activated" if self.status_indicator.mic_active else "deactivated"
        self.write_to_log(f"Microphone {status}")

    @on(Button.Pressed, "#clear-input")
    def clear_input(self) -> None:
        """Clear the text input field."""
        self.text_input.value = ""

    @on(Button.Pressed, "#submit-message")
    def submit_message(self) -> None:
        """Handle message submission."""
        message = self.text_input.value.strip()
        if message:
            self.write_to_log(f"User: {message}")
            self.text_input.value = ""
            asyncio.create_task(self.simulate_response(message))

    async def simulate_response(self, message: str) -> None:
        """Simulate an assistant response."""
        self.write_to_log("Assistant: Processing...")
        await asyncio.sleep(1)
        response = f"You said: {message}"
        self.write_to_log(f"Assistant: {response}")

    async def monitor_log_file(self) -> None:
        """Monitor the log file for changes and update log widget."""
        if not os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "w") as f:
                    f.write("Log file created\n")
            except Exception as e:
                self.log_widget.write_line(f"Error creating log file: {e}")
                return

        position = os.path.getsize(LOG_FILE)

        while True:
            try:
                if not os.path.exists(LOG_FILE):
                    self.write_to_log("Log file missing, recreating...")
                    position = 0
                    await asyncio.sleep(1)
                    continue

                current_size = os.path.getsize(LOG_FILE)

                if current_size > position:
                    with open(LOG_FILE, "r") as f:
                        f.seek(position)
                        new_content = f.read()
                        new_lines = new_content.splitlines()

                        for line in new_lines:
                            if line.strip() and not line.startswith(time.strftime("%Y-%m-%d")):
                                self.log_widget.write_line(line)

                    position = current_size
                    self.log_widget.scroll_end(animate=False)

                elif current_size < position:
                    # File was truncated or recreated
                    self.write_to_log("Log file reset detected")
                    position = current_size

            except Exception as e:
                self.log_widget.write_line(f"Error monitoring log: {e}")

            await asyncio.sleep(0.2)
