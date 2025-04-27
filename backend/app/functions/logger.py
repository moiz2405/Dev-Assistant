import sys
import logging
import os

# Create a 'logs' directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

LOG_FILE_PATH = "backend/ui/logs/assistant.log"

# Custom FileHandler that flushes immediately
class FlushAfterWriteHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()

# Set up logger
logger = logging.getLogger("assistant")
logger.setLevel(logging.DEBUG)

# Only add handlers if not already added (to avoid duplicate logs)
if not logger.handlers:
    file_handler = FlushAfterWriteHandler(LOG_FILE_PATH)
    file_handler.setLevel(logging.DEBUG)

    # Simplified formatter - only level and message
    formatter = logging.Formatter('%(levelname)s | %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

# Optional: add a console handler (nice for dev debugging)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(levelname)s | %(message)s'))
logger.addHandler(console_handler)

# Custom function to log to file
def log_to_file(message):
    logger.info(message)

# Optional: Custom print that also logs
def custom_print(*args, **kwargs):
    message = " ".join(map(str, args))
    log_to_file(message)