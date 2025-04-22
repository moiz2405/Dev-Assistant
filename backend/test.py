from concurrent.futures import ThreadPoolExecutor
import os
import sys
import asyncio
from app.stt.voice_recognition import VoiceAssistant
from app.models.groq_preprocess import cached_process_query
from app.query_processor import determine_function
from app.tts.response_generator import generate_response
from app.tts.edge_tts import speak_text

# Executor will manage threads for tasks, limit to 4 as per original config
executor = ThreadPoolExecutor(max_workers=4)

def suppress_stderr():
    # Save the original stderr file descriptor
    original_stderr = sys.stderr

    # Redirect stderr to devnull
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, sys.stderr.fileno())

    return original_stderr

# Call this to suppress stderr
original_stderr = suppress_stderr()

def handle_recognized_command(text):
    if not text:
        print("[MAIN] Nothing recognized.")
        return

    print(f"[MAIN] Recognized: {text}")

    # Submit speech synthesis task in the executor, we no longer need to manually create event loops
    executor.submit(run_speak_text, text)

    # Run other processing tasks asynchronously or in parallel
    executor.submit(lambda: determine_function(cached_process_query(text)))

def run_speak_text(text):
    try:
        # Create and set a new event loop in the thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Now, run the async function within this event loop
        asyncio.run(speak_text(generate_response(text)))
    except Exception as e:
        print(f"[MAIN] Error in speaking text: {e}")

# Start voice assistant with hotword "vision"
assistant = VoiceAssistant(hotword="vision", record_duration=6, on_recognized=handle_recognized_command)
assistant.start_hotword_listener()


# # from app.functions.github_handler import push_folder_to_github, list_github_repos, search_repo_url, clone_github_repo

# # # push_folder_to_github("test_repo", "/mnt/c/Users/km866/Downloads/test_folder")
# # # list_github_repos()

# # repo_name = "heritage"
# # clone_github_repo(repo_name,"D://")
# # print(repo_url)

# # import os
# # import sys
# # # def suppress_stderr():
# # #     devnull = os.open(os.devnull, os.O_WRONLY) 
# # #     os.dup2(devnull, sys.stderr.fileno())

# # # suppress_stderr()
# # from app.models.groq_preprocess import cached_process_query
# # from app.stt.voice_recognition import VoiceAssistant
# # from app.query_processor import determine_function

# # while(1):
# #     prompt = input()
# #     result = cached_process_query(prompt)
# #     # print(result)
# #     determine_function(cached_process_query(prompt))

# # def handle_recognized_command(text):
# #     if not text:
# #         print("[MAIN] Nothing recognized.")
# #         return

# #     print(f"[MAIN] Recognized: {text}")

# # assistant = VoiceAssistant(
# #     hotword="jarvis",
# #     record_duration=5,
# #     on_recognized=handle_recognized_command
# # )
# # assistant.start_hotword_listener()

# from app.tts.edge_tts import speak_text
# input = "Very good, cloning decentralized repository."
# speak_text(input)
# # from app.models.path_processor import list_directory_contents
# # while(1):
# #       user_path = input()
# #       contents = list_directory_contents(user_path)
# #       print(f"\nContents of '{user_path}':")
# #       for item in contents:
# #           print(f"[{item['type'].upper()}] {item['name']}")

# # from app.functions.file_handler import open_file
# # file_name = "college_notes"
# # path = "C:\\Users\\km866\\OneDrive\\Documents\\Documents"
# # open_file(file_name,path)


# # from app.functions.summarizer import summarizer, summarize_in_new_window
# # pdf_path = "C:\\Users\\km866\\OneDrive\\Documents\\Documents"
# # # summarizer(pdf_path)
# # file_name = "hall ticket"
# # summarize_in_new_window(pdf_path, file_name)


# # from app.functions.github_handler import push_folder_to_github, fuzzy_search_dir, list_github_repos

# # # repo_name = "codeforce"
# # # path = "D://va_projects"
# # list_github_repos()
# # push_folder_to_github(repo_name, path)
# # print(fuzzy_search_dir(repo_name,"D://va_projects"))
