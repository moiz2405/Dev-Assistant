# does file handling tasks like , searching creating or opening a file 
import os
import shutil

def search_file(file_name, search_path):
    """
    Search for a file in the given directory and subdirectories.
    
    :param file_name: File name (partial match allowed).
    :param search_path: Directory path to search in.
    :return: Path of the first matching file, or None.
    """
    file_name = file_name.lower()
    matching_files = []

    for root, _, files in os.walk(search_path):
        for file in files:
            if file_name in file.lower():
                file_path = os.path.join(root, file)
                matching_files.append(file_path)

    return matching_files if matching_files else None

def open_file(file_path):
    """
    Open a file if it exists.
    
    :param file_path: The file path to open.
    """
    if os.path.exists(file_path):
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # MacOS/Linux
                os.system(f'xdg-open "{file_path}"')
        except Exception as e:
            print(f"⚠️ Error opening file: {e}")
    else:
        print("❌ File does not exist!")

def move_file(file_path, new_location):
    """
    Move a file to a new location.
    
    :param file_path: The file to be moved.
    :param new_location: The new directory where the file should go.
    :return: New path of the moved file or None if failed.
    """
    if not os.path.exists(file_path):
        print("❌ File does not exist!")
        return None

    if not os.path.exists(new_location):
        os.makedirs(new_location)  # Create destination folder if not exists

    try:
        new_path = os.path.join(new_location, os.path.basename(file_path))
        shutil.move(file_path, new_path)
        return new_path
    except Exception as e:
        print(f"⚠️ Error moving file: {e}")
        return None

# # starting point 
# from app.functions.file_handler import search_file, open_file, move_file

# # Example: Searching for a file
# search_results = search_file("receipt.txt", "/home/user/Documents")
# if search_results:
#     print("Found files:", search_results)
#     file_to_open = search_results[0]  # Automatically selects the first match
#     open_file(file_to_open)

# # Example: Moving a file
# # new_path = move_file(file_to_open, "/home/user/Desktop")
# # if new_path:
# #     print(f"File successfully moved to: {new_path}")

