# from concurrent.futures import ThreadPoolExecutor
# import os
# import sys
# import atexit
# from app.functions.file_handler import open_file,list_files_by_type
# target = "hallticket"
# path = "C:\\Users\\km866\\OneDrive\\Documents\\Documents"
# open_file(target,path)
from app.functions.app_handling import open_app, close_app
target = "whatsapp"
close_app(target)

# from app.functions.github_handler import clone_github_repo, push_folder_to_github,list_github_repos

# # list_github_repos()
# target = input("Enter Project name to Push to Github:  " )
# # clone_github_repo(target,"D://va_projects")
# push_folder_to_github(target, "D://va_projects")
# # from app.stt.voice_recognition import VoiceAssistant
# # from app.models.groq_preprocess import cached_process_query
# # from app.query_processor import determine_function
# # from app.tts.response_generator import generate_response
# # # from app.tts.eleven_labs_tts import speak
# # from app.tts.edge_tts import speak_text

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# from shared_todo_queue import enqueue,dequeue

# # enqueue("Hello")
# # enqueue("Hello")
# task = dequeue()
# print(task)
# # enqueue("another hello")


# # executor = ThreadPoolExecutor(max_workers=4)
# # atexit.register(lambda: executor.shutdown(wait=True))

# # def handle_recognized_command(text):
# #     if not text:
# #         print("[MAIN] Nothing recognized.")
# #         return

# #     print(f"[MAIN] Recognized: {text}")

# #     # Run TTS and processing in parallel
# #     executor.submit(lambda: speak_text(generate_response(text)))
# #     executor.submit(lambda: determine_function(cached_process_query(text)))

# # assistant = VoiceAssistant(hotword="vision",record_duration=6,on_recognized=handle_recognized_command)
# # assistant.start_hotword_listener()

# # while(1):
# #     prompt = input("Enter your prompt")
# #     determine_function(cached_process_query(prompt))