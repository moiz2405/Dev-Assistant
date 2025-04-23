import asyncio
import logging
import os
import time
from typing import Optional

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import (
    Footer, Header, Input, Label, Log, LoadingIndicator, 
    ProgressBar, Static, Button
)

# Set up logging
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "assistant.log")
os.makedirs(LOG_DIR, exist_ok=True)

# Configure debug logger
debug_logger = logging.getLogger("VoiceAssistantUI")
debug_logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("debug_ui.log")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
debug_logger.addHandler(file_handler)


class LoadingScreen(Screen):
    """Loading screen with animation."""
    
    DEFAULT_CSS = """
    LoadingScreen {
        align: center middle;
        background: $surface;
    }
    
    .loading-container {
        width: 60%;
        height: 40%;
        background: $surface-darken-1;
        border: tall $primary;
        border-radius: 4;
        padding: 2;
        align: center middle;
    }
    
    .loading-label {
        text-align: center;
        margin-bottom: 2;
        height: 3;
        color: $text;
        text-style: bold;
    }
    
    LoadingIndicator {
        width: 100%;
        height: 3;
    }
    
    ProgressBar {
        width: 100%;
        margin-top: 1;
    }
    """
    
    progress = reactive(0.0)
    
    def compose(self) -> ComposeResult:
        with Container(classes="loading-container"):
            yield Label("Initializing Voice Assistant...", classes="loading-label")
            yield LoadingIndicator()
            yield ProgressBar(total=100, show_eta=False)
    
    def on_mount(self) -> None:
        """Start the loading simulation when the screen is mounted."""
        self.simulate_loading_task = asyncio.create_task(self.simulate_loading())
    
    async def simulate_loading(self) -> None:
        """Simulate a loading process."""
        progress_bar = self.query_one(ProgressBar)
        
        for i in range(1, 101):
            self.progress = i
            progress_bar.update(progress=i)
            # Simulate variable loading speeds
            delay = 0.01 if i > 80 else (0.03 if i > 50 else 0.05)
            await asyncio.sleep(delay)
        
        # Switch to main screen when loading completes
        self.app.push_screen("main")


class DynamicVisualElement(Static):
    """A dynamic visual element that updates based on mic status."""
    
    DEFAULT_CSS = """
    DynamicVisualElement {
        width: 100%;
        height: 12;
        background: $surface-darken-1;
        border: wide $primary-darken-1;
        border-radius: 12;
        content-align: center middle;
        padding: 1;
    }
    
    .animation-active {
        border: wide $success;
        background: $success-darken-3;
    }
    
    .animation-inactive {
        border: wide $primary-darken-1;
        background: $surface-darken-1;
    }
    """
    
    is_active = reactive(False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.animation_task = None
    
    def on_mount(self) -> None:
        """Start animation when mounted."""
        self.animation_task = asyncio.create_task(self.animate())
        self.update_status(False)
    
    def update_status(self, active: bool) -> None:
        """Update the visual status."""
        self.is_active = active
        if active:
            self.add_class("animation-active")
            self.remove_class("animation-inactive")
            self.update("Microphone Active")
        else:
            self.add_class("animation-inactive")
            self.remove_class("animation-active")
            self.update("Microphone Inactive")
    
    async def animate(self) -> None:
        """Simple animation effect."""
        frame = 0
        while True:
            # Only animate when active
            if self.is_active:
                frames = ["⬤", "◉", "○", "◎", "◉"]
                self.update(f"{frames[frame % len(frames)]} Microphone Active {frames[frame % len(frames)]}")
                frame += 1
            await asyncio.sleep(0.5)
    
    def toggle_status(self) -> None:
        """Toggle the active status."""
        self.update_status(not self.is_active)


class StatusIndicator(Static):
    """Indicator for microphone and other statuses."""
    
    DEFAULT_CSS = """
    StatusIndicator {
        width: 100%;
        height: 6;
        background: $panel-darken-1;
        border: tall $primary-darken-2;
        border-radius: 3;
        padding: 1;
        content-align: center middle;
    }
    
    .status-active {
        color: $success;
    }
    
    .status-inactive {
        color: $error;
    }
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__("◌ Microphone: Inactive", *args, **kwargs)
        self.mic_active = False
    
    def toggle_mic(self) -> None:
        """Toggle microphone status."""
        self.mic_active = not self.mic_active
        self.update_status()
    
    def update_status(self) -> None:
        """Update the displayed status."""
        if self.mic_active:
            self.update("● Microphone: Active")
            self.add_class("status-active")
            self.remove_class("status-inactive")
        else:
            self.update("◌ Microphone: Inactive")
            self.add_class("status-inactive")
            self.remove_class("status-active")


class MainScreen(Screen):
    """Main application screen with split panels."""
    
    DEFAULT_CSS = """
    MainScreen {
        layout: vertical;
        background: $surface;
    }
    
    #main-container {
        width: 100%;
        height: 100%;
    }
    
    #main-panel {
        width: 70%;
        border-right: solid $primary;
        padding: 1;
    }
    
    #logs-panel {
        width: 30%;
        border-left: solid $primary;
    }
    
    #logs-label {
        background: $primary;
        color: $text;
        text-align: center;
        height: 3;
        padding-top: 1;
        text-style: bold;
    }
    
    Log {
        height: 100%;
        border: none;
        background: $surface-darken-1;
        color: $text;
    }
    
    Input {
        margin-top: 1;
        width: 100%;
        border: tall $primary-darken-2;
    }
    
    #voice-controls {
        margin-top: 1;
        width: 100%;
        height: 3;
    }
    
    Button {
        margin-right: 1;
    }
    """
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header()
        
        with Horizontal(id="main-container"):
            # Main panel with visual elements
            with Vertical(id="main-panel"):
                yield DynamicVisualElement(id="dynamic-element")
                yield StatusIndicator(id="status-indicator")
                yield Input(placeholder="Type your message here...", id="text-input")
                
                with Horizontal(id="voice-controls"):
                    yield Button("Toggle Mic", variant="primary", id="toggle-mic")
                    yield Button("Clear Input", variant="warning", id="clear-input")
                    yield Button("Submit", variant="success", id="submit-message")
            
            # Logs panel
            with Vertical(id="logs-panel"):
                yield Label("Realtime Logs Monitor", id="logs-label")
                yield Log(highlight=True, id="log-widget")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when the screen is mounted."""
        # Initialize log monitoring
        self.log_widget = self.query_one("#log-widget", Log)
        self.dynamic_element = self.query_one("#dynamic-element", DynamicVisualElement)
        self.status_indicator = self.query_one("#status-indicator", StatusIndicator)
        self.text_input = self.query_one("#text-input", Input)
        
        # Start monitoring logs
        asyncio.create_task(self.monitor_log_file())
        
        # Add a welcome message to logs
        self.write_to_log("Voice Assistant UI started")
        self.write_to_log("Monitoring logs in real-time")
    
    def write_to_log(self, message: str) -> None:
        """Convenience method to write to both the log file and UI."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp} - {message}\n")
        
        # Also write directly to the log widget for immediate feedback
        self.log_widget.write_line(f"{timestamp} - {message}")
    
    @on(Button.Pressed, "#toggle-mic")
    def toggle_microphone(self) -> None:
        """Handle toggle mic button press."""
        self.status_indicator.toggle_mic()
        self.dynamic_element.toggle_status()
        
        status = "activated" if self.status_indicator.mic_active else "deactivated"
        self.write_to_log(f"Microphone {status}")
    
    @on(Button.Pressed, "#clear-input")
    def clear_input(self) -> None:
        """Clear the text input."""
        self.text_input.clear()
    
    @on(Button.Pressed, "#submit-message")
    def submit_message(self) -> None:
        """Submit the message from the input field."""
        message = self.text_input.value
        if message.strip():
            self.write_to_log(f"User: {message}")
            self.text_input.clear()
            
            # Simulate a response
            asyncio.create_task(self.simulate_response(message))
    
    async def simulate_response(self, message: str) -> None:
        """Simulate an assistant response."""
        # Simulate thinking
        self.write_to_log("Assistant: Processing...")
        await asyncio.sleep(1.0)
        
        # Simple echo response for now
        response = f"You said: {message}"
        self.write_to_log(f"Assistant: {response}")
    
    async def monitor_log_file(self) -> None:
        """Monitor the log file for changes."""
        # Create file if it doesn't exist
        if not os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "w") as f:
                    f.write("Log file created\n")
            except Exception as e:
                debug_logger.error(f"Failed to create log file: {str(e)}")
                return
        
        # Get current size
        try:
            position = os.path.getsize(LOG_FILE)
        except Exception as e:
            debug_logger.error(f"Error getting file size: {str(e)}")
            position = 0
        
        # Monitor for changes
        while True:
            try:
                if not os.path.exists(LOG_FILE):
                    debug_logger.warning("Log file no longer exists, waiting for recreation")
                    position = 0
                    await asyncio.sleep(1)
                    continue
                    
                current_size = os.path.getsize(LOG_FILE)
                
                # If file has grown
                if current_size > position:
                    with open(LOG_FILE, "r") as f:
                        f.seek(position)
                        new_content = f.read()
                        new_lines = new_content.splitlines()
                        
                        for line in new_lines:
                            if line.strip():  # Skip empty lines
                                self.log_widget.write_line(line)
                        
                        position = f.tell()
                        
                        # Always scroll to the bottom to follow logs
                        self.log_widget.scroll_end(animate=False)
                
                # Handle file truncation
                elif current_size < position:
                    # File was truncated or recreated
                    debug_logger.warning(f"File truncated: size={current_size}, was at position={position}")
                    position = current_size
            
            except Exception as e:
                debug_logger.error(f"Error monitoring log: {str(e)}")
            
            # Sleep before next check
            await asyncio.sleep(0.2)  # 5 checks per second


class VoiceAssistantUI(App):
    """Voice Assistant UI application."""
    
    TITLE = "Voice Assistant UI"
    SUB_TITLE = "Textual TUI"
    CSS_PATH = None  # We're using component-specific DEFAULT_CSS instead
    
    SCREENS = {
        "loading": LoadingScreen,  # Classes, not instances
        "main": MainScreen,
    }
    
    def on_mount(self) -> None:
        """Start with the loading screen."""
        self.push_screen("loading")


if __name__ == "__main__":
    app = VoiceAssistantUI()
    app.run()