from textual.widgets import Static
from textual.reactive import reactive
import asyncio

class DynamicVisualElement(Static):
    is_active = reactive(False)

    def on_mount(self) -> None:
        self.animation_task = asyncio.create_task(self.animate())
        self.update_status(False)
    
    def update_status(self, active: bool) -> None:
        self.is_active = active
        if active:
            self.add_class("animation-active")
            self.update("Microphone Active")
        else:
            self.add_class("animation-inactive")
            self.update("Microphone Inactive")

    async def animate(self) -> None:
        frame = 0
        frames = ["⬤", "◉", "○", "◎", "◉"]
        while True:
            if self.is_active:
                self.update(f"{frames[frame % len(frames)]} Microphone Active {frames[frame % len(frames)]}")
                frame += 1
            await asyncio.sleep(0.5)

    def toggle_status(self) -> None:
        self.update_status(not self.is_active)
