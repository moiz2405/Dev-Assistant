# ui/layout.py
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Static
from core.logger import get_logger

logger = get_logger()

class LogPanel(Static):
    def on_mount(self) -> None:
        self.update("Logs will appear here...")

    def append_log(self, message: str):
        self.update(self.renderable + f"\n{message}")

class MainPanel(Static):
    def on_mount(self) -> None:
        self.update("Main AI Assistant Panel")

class AssistantApp(App):
    CSS_PATH = "ui/styles.css"

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

    async def action_test_log(self):
        msg = "Test action triggered"
        logger.info(msg)
        self.log_panel.append_log(f"🔔 {msg}")

if __name__ == "__main__":
    AssistantApp().run()
