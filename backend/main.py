# starting point 
from app.functions.file_handler import search_file, open_file, move_file

# Example: Searching for a file
# wsl path /home/moiz/myfolder/projects
file_path = "/mnt/d/"

search_results = search_file("one.txt", file_path)
if search_results:
    print("Found files:", search_results)
    file_to_open = search_results[0]  # Automatically selects the first match
    open_file(file_to_open)

# Example: Moving a file
# new_path = move_file(file_to_open, "/home/user/Desktop")
# if new_path:
#     print(f"File successfully moved to: {new_path}")

