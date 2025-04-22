from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Static
from app.functions.logger import logger  # Import logger

class LogPanel(Static):
    def on_mount(self) -> None:
        # Initialize logs with a default message
        self.logs = ["Logs will appear here..."]
        self.update("\n".join(self.logs))

    def append_log(self, message: str):
        # Append new logs to the existing logs
        self.logs.append(message)
        self.update("\n".join(self.logs))

class MainPanel(Static):
    def on_mount(self) -> None:
        # Set up the main panel with a default message
        self.update("Main AI Assistant Panel")

class AssistantApp(App):
    CSS_PATH = "styles.css"
    BINDINGS = [("t", "test_log")]  # Bind 't' key to test log action

    def compose(self) -> ComposeResult:
        # Create LogPanel and MainPanel
        self.log_panel = LogPanel(id="log_panel")
        self.main_panel = MainPanel(id="main_panel")

        # Arrange the panels in a container layout
        yield Container(
            Vertical(self.log_panel, id="left"),
            self.main_panel,
            id="layout"
        )

    async def on_startup(self) -> None:
        # Log the app startup and append it to the LogPanel
        logger.info("App started successfully.")
        self.log_panel.append_log("🟢 App started")

    async def action_test_log(self):
        # This action will be triggered by pressing 't'
        msg = "Test action triggered"
        logger.info(msg)  # Log the action
        self.log_panel.append_log(f"🔔 {msg}")  # Display it in LogPanel

if __name__ == "__main__":
    # Run the app
    AssistantApp().run()
