# import os; print("USERNAME:", os.getenv("GITHUB_USERNAME"))


# from app.functions.github_handler import push_folder_to_github, list_github_repos, search_repo_url

# # push_folder_to_github("test_repo", "/mnt/c/Users/km866/Downloads/test_folder")
# # list_github_repos()

# repo_url = search_repo_url("acc")
# print(repo_url)

from app.models.groq_preprocess import cached_process_query
from app.stt.voice_recognition import VoiceAssistant
# from app.models.test_preprocess import cached_process_query
from app.query_processor import determine_function
while(1):
    prompt = input()
    cached_process_query(prompt)
    # determine_function(cached_process_query(prompt))
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