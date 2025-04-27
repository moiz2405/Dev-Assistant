from textual.widgets import Static

class StatusIndicator(Static):
    def __init__(self, *args, **kwargs):
        super().__init__("◌ Microphone: Inactive", *args, **kwargs)
        self.mic_active = False
    
    def toggle_mic(self) -> None:
        self.mic_active = not self.mic_active
        self.update_status()
    
    def update_status(self) -> None:
        if self.mic_active:
            self.update("● Microphone: Active")
        else:
            self.update("◌ Microphone: Inactive")
