# starting point 
from app.functions.file_handler import search_file, open_file, move_file

# Example: Searching for a file
search_results = search_file("receipt.txt", "/home/user/Documents")
if search_results:
    print("Found files:", search_results)
    file_to_open = search_results[0]  # Automatically selects the first match
    open_file(file_to_open)

# Example: Moving a file
# new_path = move_file(file_to_open, "/home/user/Desktop")
# if new_path:
#     print(f"File successfully moved to: {new_path}")

