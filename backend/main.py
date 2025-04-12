# starting point 
# file handling 
# -------------------------------------------------------------------------
# # from app.functions.file_handler import search_file, open_file, move_file

# # Example: Searching for a file
# # wsl path /home/moiz/myfolder/projects
# # file_path = "/mnt/d/"

# # search_results = search_file("one.txt", file_path)
# # if search_results:
# #     print("Found files:", search_results)
# #     file_to_open = search_results[0]  # Automatically selects the first match
# #     open_file(file_to_open)

# # Example: Moving a file
# # new_path = move_file(file_to_open, "/home/user/Desktop")
# # if new_path:
# #     print(f"File successfully moved to: {new_path}")
# ---------------------------------------------------------------------
# app handling 
# from app.functions.app_handling import open_app, close_app

# while(1):
#     app_name = input()
#     open_app(app_name)

# from app.tts.voice_processor import voice_processor

# while(1):
#     voice_input = input()
#     print(voice_processor(voice_input))

# from app.functions.file_handler import list_files_by_type


# # file_type, file_path=input()
# files = list_files_by_type("ppt","C:\\Users\\Shikhar\\Downloads")
# print(files)
import os
import sys

def suppress_stderr():
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, sys.stderr.fileno())

suppress_stderr()

from app.tts.voice_recognition import VoiceAssistant
from app.models.groq_preprocess import process_query
from app.query_processor import determine_function

#start hotword detection and taking user query in natural language
assistant = VoiceAssistant(hotword="jarvis", record_duration=5)
assistant.start_hotword_listener()



query = "open whatsapp"
result = process_query(query)
determine_function(result)
