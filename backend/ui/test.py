import asyncio
import logging
import os
from textual.app import App
from textual.widgets import Static, Log
from textual.containers import Container

# Set up logging (both file and console)
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "assistant.log")

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logger
logger = logging.getLogger("AssistantApp")
logger.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# File handler
file_handler = logging.FileHandler("debug_viewer.log")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

class StatusBar(Static):
    """Shows app status and debugging info."""
    
    def update_status(self, message):
        self.update(f"Status: {message}")

class LogViewer(App):
    """Simple log file viewer with error logging."""
    
    def compose(self):
        self.status_bar = StatusBar("Status: Starting...")
        self.log_display = Log()
        
        yield Container(
            self.status_bar,
            self.log_display,
        )
    
    async def on_mount(self):
        logger.info("Application started")
        self.status_bar.update_status("Application started")
        
        # Write a test entry to the log file to verify writing works
        self.test_log_write()
        
        # Start file monitoring
        asyncio.create_task(self.monitor_log_file())
    
    def test_log_write(self):
        """Write a test entry to the log file."""
        try:
            # Ensure log directory exists
            os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
            
            # Write test entry
            with open(LOG_FILE, "a") as f:
                test_message = f"Log viewer test entry at {logging.Formatter().formatTime(None)}"
                f.write(f"{test_message}\n")
                f.flush()  # Force write to disk
                
            self.status_bar.update_status("Test log entry written successfully")
            logger.info("Test log entry written successfully")
        except Exception as e:
            error_msg = f"Error writing test log: {str(e)}"
            self.status_bar.update_status(error_msg)
            logger.error(error_msg)
    
    async def monitor_log_file(self):
        """Monitor the log file with detailed error reporting."""
        self.status_bar.update_status(f"Monitoring log file: {LOG_FILE}")
        logger.info(f"Monitoring log file: {LOG_FILE}")
        
        # Check if file exists
        if not os.path.exists(LOG_FILE):
            error_msg = f"Log file does not exist: {LOG_FILE}"
            self.status_bar.update_status(error_msg)
            logger.error(error_msg)
            
            # Create the file
            try:
                with open(LOG_FILE, "w") as f:
                    f.write("Log file created by viewer\n")
                self.status_bar.update_status(f"Created log file: {LOG_FILE}")
                logger.info(f"Created log file: {LOG_FILE}")
            except Exception as e:
                error_msg = f"Failed to create log file: {str(e)}"
                self.status_bar.update_status(error_msg)
                logger.error(error_msg)
                return
        
        # Start with the file size
        try:
            file_size = os.path.getsize(LOG_FILE)
            self.status_bar.update_status(f"Initial file size: {file_size} bytes")
            logger.info(f"Initial file size: {file_size} bytes")
        except Exception as e:
            error_msg = f"Error getting file size: {str(e)}"
            self.status_bar.update_status(error_msg)
            logger.error(error_msg)
            file_size = 0
        
        # Read existing content
        try:
            if file_size > 0:
                with open(LOG_FILE, "r") as f:
                    content = f.read()
                    lines = content.splitlines()
                    for line in lines[-100:]:  # Last 100 lines
                        self.log_display.write_line(line)
                self.status_bar.update_status(f"Loaded {len(lines)} existing log lines")
                logger.info(f"Loaded {len(lines)} existing log lines")
        except Exception as e:
            error_msg = f"Error reading existing logs: {str(e)}"
            self.status_bar.update_status(error_msg)
            logger.error(error_msg)
        
        # Monitor for changes
        position = file_size
        check_count = 0
        
        while True:
            try:
                check_count += 1
                current_size = os.path.getsize(LOG_FILE)
                
                # Log status every 50 checks (for debugging)
                if check_count % 50 == 0:
                    status_msg = f"Check #{check_count}: Size {current_size}, Position {position}"
                    logger.debug(status_msg)
                    if check_count % 200 == 0:  # Update UI less frequently
                        self.status_bar.update_status(status_msg)
                
                # If file has grown
                if current_size > position:
                    with open(LOG_FILE, "r") as f:
                        f.seek(position)
                        new_content = f.read()
                        new_lines = new_content.splitlines()
                        
                        for line in new_lines:
                            if line.strip():  # Skip empty lines
                                self.log_display.write_line(line)
                        
                        position = f.tell()
                        self.status_bar.update_status(f"Read {len(new_lines)} new lines, position now {position}")
                        logger.info(f"Read {len(new_lines)} new lines, position now {position}")
                
                # Handle file truncation
                elif current_size < position:
                    # File was truncated or recreated
                    logger.warning(f"File truncated: size={current_size}, was at position={position}")
                    self.status_bar.update_status(f"File truncated, reloading")
                    position = 0
                    with open(LOG_FILE, "r") as f:
                        content = f.read()
                        lines = content.splitlines()
                        self.log_display.clear()
                        for line in lines:
                            if line.strip():
                                self.log_display.write_line(line)
                        position = f.tell()
            
            except Exception as e:
                error_msg = f"Error monitoring log: {str(e)}"
                self.status_bar.update_status(error_msg)
                logger.error(error_msg)
            
            # Sleep before next check
            await asyncio.sleep(0.2)  # 5 checks per second

if __name__ == "__main__":
    app = LogViewer()
    app.run()