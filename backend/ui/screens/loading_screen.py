from textual.screen import Screen
from textual.containers import Container
from textual.widgets import Label, LoadingIndicator, ProgressBar
from textual.reactive import reactive
from textual.app import ComposeResult
import asyncio

class LoadingScreen(Screen):
    """Loading screen with animation."""
    
    progress = reactive(0.0)
    
    def compose(self) -> ComposeResult:
        with Container(classes="loading-container"):
            yield Label("Initializing Voice Assistant...", classes="loading-label")
            yield LoadingIndicator()
            yield ProgressBar(total=100, show_eta=False)
    
    def on_mount(self) -> None:
        self.simulate_loading_task = asyncio.create_task(self.simulate_loading())

    async def simulate_loading(self) -> None:
        progress_bar = self.query_one(ProgressBar)
        
        for i in range(1, 101):
            self.progress = i
            progress_bar.update(progress=i)
            await asyncio.sleep(0.03 if i < 50 else 0.01)
        
        self.app.push_screen("main")
