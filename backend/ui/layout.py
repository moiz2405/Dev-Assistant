from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Static

class LogPanel(Static):
    def on_mount(self) -> None:
        self.logs = ["Logs will appear here..."]
        self.update("\n".join(self.logs))

    def append_log(self, message: str):
        """Append a log message to the panel."""
        self.logs.append(message)
        self.update("\n".join(self.logs))
        print(f"Appended log: {message}")  # Debug print to confirm log is appended


class MainPanel(Static):
    def on_mount(self) -> None:
        self.update("Main AI Assistant Panel")

class AssistantApp(App):
    def compose(self) -> ComposeResult:
        self.log_panel = LogPanel(id="log_panel")
        self.main_panel = MainPanel(id="main_panel")

        yield Container(
            Vertical(self.log_panel, id="left"),
            self.main_panel,
            id="layout"
        )

    async def on_startup(self) -> None:
        self.log_panel.append_log("🟢 App started")
        print("App startup complete!")  # Debug print to ensure startup

    async def action_test_log(self):
        msg = "Test action triggered"
        self.log_panel.append_log(f"🔔 {msg}")

if __name__ == "__main__":
    print("Running the UI...")
    AssistantApp().run()
