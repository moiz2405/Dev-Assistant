from textual.app import App
from screens.loading_screen import LoadingScreen
from screens.main_screen import MainScreen

class VoiceAssistantUI(App):
    TITLE = "V.I.S.I.O.N"
    SUB_TITLE = "At your service"
    CSS_PATH = "styles.css"

    SCREENS = {
        "loading": LoadingScreen,
        "main": MainScreen,
    }
    
    def on_mount(self) -> None:
        self.push_screen("loading")


if __name__ == "__main__":
    app = VoiceAssistantUI()
    app.run()
