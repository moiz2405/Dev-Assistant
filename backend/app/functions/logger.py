import sys
import logging
import os

# Set up logger
logger = logging.getLogger("assistant")
logger.setLevel(logging.DEBUG)

# Create a 'logs' directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# File handler to log into a file
file_handler = logging.FileHandler("logs/assistant.log")
file_handler.setLevel(logging.DEBUG)

# Formatter for the logs
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
file_handler.setFormatter(formatter)

# Add file handler to the logger
logger.addHandler(file_handler)

# Custom print function to log to file
def log_to_file(message):
    logger.info(message)  # Log message to the file

# Use custom print only for logging purposes
def custom_print(*args, **kwargs):
    message = " ".join(map(str, args))
    
    # Log to the log file without changing the print behavior
    log_to_file(message)

# Example usage: log something
# print("This is printed in terminal.")  # This will still show in terminal
# custom_print("This message will be logged into the file.")
