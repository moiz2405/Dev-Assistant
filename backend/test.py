# from app.functions.project_handler.create_project import setup_project
# from app.functions.project_handler.create_runner import run_project_setup
# while(1):
#     target = input()
#     run_project_setup(target, "D://va_projects")

from app.models.groq_preprocess import cached_process_query
while(1):
    user_prompt = input("Enter your query: ")
    cached_process_query(user_prompt)

# from app.functions.project_handler.create_project import setup_project
# from app.functions.project_handler.setup_project import setup_existing_project


# path = "D://va_projects"
# name = input()
# setup_existing_project(name,path)


    # setup_project(type,path)

# from app.functions.github_handler import clone_github_repo
# target = input ()
# clone_github_repo(target,"D://va_projects")


# import sys
# import os
# import asyncio
# from concurrent.futures import ThreadPoolExecutor
# from app.stt.voice_recognition import VoiceAssistant
# from app.models.groq_preprocess import cached_process_query
# from app.query_processor import determine_function
# from app.tts.response_generator import generate_response
# from app.tts.edge_tts import speak_text
# from app.functions.logger import logger

# # Executor will manage threads for tasks, limit to 4 as per original config
# executor = ThreadPoolExecutor(max_workers=4)

# # Custom print function to avoid recursion
# def custom_print(message):
#     """Custom print function to avoid recursion, print to stdout"""
#     sys.stdout.write(message + '\n')  # Write directly to stdout (without recursion)

# # Suppress stderr for warnings and errors
# def suppress_stderr():
#     """Suppress stderr output (warnings/errors) by redirecting it to devnull."""
#     original_stderr = sys.stderr
#     devnull = os.open(os.devnull, os.O_WRONLY)
#     os.dup2(devnull, sys.stderr.fileno())
#     return original_stderr

# # Call this to suppress stderr
# original_stderr = suppress_stderr()

# # Handle recognized commands and log appropriately
# def handle_recognized_command(text):
#     if not text:
#         # custom_print("[MAIN] Nothing recognized.")  # Use custom print for terminal output
#         logger.info("[MAIN] Nothing recognized.")   # Log using logger
#         return

#     # custom_print(f"[MAIN] Recognized: {text}")  # Print to terminal
#     logger.info(f"[MAIN] Recognized: {text}")   # Log it for records

#     # Submit speech synthesis task in the executor
#     executor.submit(run_speak_text, text)

#     # Run other processing tasks asynchronously or in parallel
#     executor.submit(lambda: determine_function(cached_process_query(text)))

# # Run the speech synthesis in a separate thread
# def run_speak_text(text):
#     try:
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         asyncio.run(speak_text(generate_response(text)))
#     except Exception as e:
#         logger.error(f"[MAIN] Error in speaking text: {e}")  # Log any error that occurs

# # Start voice assistant with hotword "vision"
# assistant = VoiceAssistant(hotword="vision", record_duration=6, on_recognized=handle_recognized_command)
# assistant.start_hotword_listener()




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
