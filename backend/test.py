# import os; print("USERNAME:", os.getenv("GITHUB_USERNAME"))


# from app.functions.github_handler import push_folder_to_github, list_github_repos, search_repo_url

# # push_folder_to_github("test_repo", "/mnt/c/Users/km866/Downloads/test_folder")
# # list_github_repos()

# repo_url = search_repo_url("acc")
# print(repo_url)
import os
import sys
# def suppress_stderr():
#     devnull = os.open(os.devnull, os.O_WRONLY) 
#     os.dup2(devnull, sys.stderr.fileno())

# suppress_stderr()
from app.models.groq_preprocess import cached_process_query
from app.stt.voice_recognition import VoiceAssistant
# from app.models.test_preprocess import cached_process_query
from app.query_processor import determine_function
while(1):
    prompt = input()
    cached_process_query(prompt)
    determine_function(cached_process_query(prompt))

# def handle_recognized_command(text):
#     if not text:
#         print("[MAIN] Nothing recognized.")
#         return

#     print(f"[MAIN] Recognized: {text}")

# assistant = VoiceAssistant(
#     hotword="jarvis",
#     record_duration=5,
#     on_recognized=handle_recognized_command
# )
# assistant.start_hotword_listener()
# from app.models.path_processor import list_directory_contents
# while(1):
#       user_path = input()
#       contents = list_directory_contents(user_path)
#       print(f"\nContents of '{user_path}':")
#       for item in contents:
#           print(f"[{item['type'].upper()}] {item['name']}")

# from app.functions.file_handler import open_file
# file_name = "college_notes"
# path = "C:\\Users\\km866\\OneDrive\\Documents\\Documents"
# open_file(file_name,path)
