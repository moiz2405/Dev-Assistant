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
from app.functions.app_handling import open_app, close_app

# while(1):
#     app_name = input()
#     open_app(app_name)

from app.tts.voice_processor import voice_processor

while(1):
    voice_input = input()
    print(voice_processor(voice_input))

