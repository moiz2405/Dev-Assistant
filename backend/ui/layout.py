import asyncio
import logging
import os
from textual.app import App
from textual.widgets import Header, Footer, Log
from textual.containers import Container
from textual.binding import Binding

# Set up logging (file only for main app, console for errors)
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "assistant.log")

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logger for debugging only
debug_logger = logging.getLogger("LogViewer")
debug_logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("debug_viewer.log")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
debug_logger.addHandler(file_handler)

class LogViewer(App):
    """Elegant log viewer for voice assistant."""
    
    TITLE = "V.I.S.I.O.N"
    SUB_TITLE = "Logs window"
    
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit"),
        Binding(key="c", action="clear", description="Clear"),
        Binding(key="r", action="refresh", description="Refresh"),
        Binding(key="f", action="follow", description="Toggle follow"),
    ]
    
    CSS = """
    Log {
        height: 100%;
        border: solid cornflowerblue;
        background: $surface-darken-1;
        color: $text;
    }
    
    #log-container {
        height: 100%;
    }
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.following = True  # Auto-follow logs by default
        self.log_widget = None  # Use a different name to avoid conflict
    
    def compose(self):
        yield Header()
        yield Container(
            Log(highlight=True),
            id="log-container"
        )
        yield Footer()
    
    def on_mount(self):
        """App is ready to start."""
        # Use a different name for the log widget
        self.log_widget = self.query_one(Log)
        
        # Start file monitoring
        asyncio.create_task(self.monitor_log_file())
    
    async def action_clear(self):
        """Clear the log display."""
        self.log_widget.clear()
    
    async def action_refresh(self):
        """Reload the entire log file."""
        await self.load_full_log()
    
    async def action_follow(self):
        """Toggle whether to automatically follow new logs."""
        self.following = not self.following
        self.notify(f"Log following: {'ON' if self.following else 'OFF'}")
    
    async def load_full_log(self):
        """Load the full log file content."""
        try:
            if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
                with open(LOG_FILE, "r") as f:
                    content = f.read()
                    lines = content.splitlines()
                    
                    self.log_widget.clear()
                    for line in lines:
                        if line.strip():
                            # Add directly without markup
                            self.log_widget.write_line(line)
                    
                    # Scroll to bottom if following
                    if self.following:
                        self.log_widget.scroll_end(animate=False)
        except Exception as e:
            debug_logger.error(f"Error loading log file: {str(e)}")
    
    async def monitor_log_file(self):
        """Monitor the log file for changes."""
        # Create file if it doesn't exist
        if not os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "w") as f:
                    f.write("Log file created\n")
            except Exception as e:
                debug_logger.error(f"Failed to create log file: {str(e)}")
                return
        
        # Load existing content
        await self.load_full_log()
        
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
                                # No markup formatting
                                self.log_widget.write_line(line)
                        
                        position = f.tell()
                        
                        # Scroll to bottom if following
                        if self.following:
                            self.log_widget.scroll_end(animate=False)
                
                # Handle file truncation
                elif current_size < position:
                    # File was truncated or recreated
                    debug_logger.warning(f"File truncated: size={current_size}, was at position={position}")
                    await self.load_full_log()
                    position = current_size
            
            except Exception as e:
                debug_logger.error(f"Error monitoring log: {str(e)}")
            
            # Sleep before next check
            await asyncio.sleep(0.2)  # 5 checks per second

if __name__ == "__main__":
    app = LogViewer()
    app.run()