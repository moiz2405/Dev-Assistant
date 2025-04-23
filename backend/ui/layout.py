# layout.py
import asyncio
import websockets
import json
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Static

class LogPanel(Static):
    def on_mount(self) -> None:
        self.logs = ["Logs will appear here..."]
        self.update("\n".join(self.logs))

    def append_log(self, message: str):
        self.logs.append(message)
        self.update("\n".join(self.logs))
        print(f"Appended log: {message}")

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
        print("App startup complete!")
        asyncio.create_task(self.start_websocket_server())

    async def start_websocket_server(self):
        async def handler(websocket):
            async for message in websocket:
                data = json.loads(message)
                if data.get("type") == "log":
                    self.log_panel.append_log(data["message"])

        self.log_panel.append_log("🟡 Starting WebSocket server...")
        await websockets.serve(handler, "localhost", 8765)
        self.log_panel.append_log("🟢 WebSocket server listening on ws://localhost:8765")

    def update_log_message(self, message: str):
        self.log_panel.append_log(message)

if __name__ == "__main__":
    print("Running the UI...")
    AssistantApp().run()
