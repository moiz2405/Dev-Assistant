from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Static
from backend.app.functions.logger import logger

class LogPanel(Static):
    def on_mount(self) -> None:
        self.logs = ["Logs will appear here..."]
        self.update("\n".join(self.logs))

    def append_log(self, message: str):
        self.logs.append(message)
        self.update("\n".join(self.logs))

class MainPanel(Static):
    def on_mount(self) -> None:
        self.update("Main AI Assistant Panel")

class AssistantApp(App):
    CSS_PATH = "styles.css"
    BINDINGS = [("t", "test_log")]  # Bind 't' key to test log action

    def compose(self) -> ComposeResult:
        self.log_panel = LogPanel(id="log_panel")
        self.main_panel = MainPanel(id="main_panel")

        yield Container(
            Vertical(self.log_panel, id="left"),
            self.main_panel,
            id="layout"
        )

    async def on_startup(self) -> None:
        logger.info("App started successfully.")
        self.log_panel.append_log("🟢 App started")
        print("App startup complete!")  # Debug print to ensure startup

    async def action_test_log(self):
        msg = "Test action triggered"
        logger.info(msg)
        self.log_panel.append_log(f"🔔 {msg}")

if __name__ == "__main__":
    print("Running the UI...")
    AssistantApp().run()
