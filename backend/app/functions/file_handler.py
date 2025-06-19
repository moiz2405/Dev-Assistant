import os
import shutil
import platform
import difflib
import subprocess
# Global cache for indexed files
indexed_files_cache = {}
# from logger import logger
def is_wsl():
    return 'microsoft' in platform.uname().release.lower()

def convert_to_wsl_path(win_path: str) -> str:
    if ":" in win_path:
        drive, rest = win_path.split(":", 1)
        drive = drive.lower()
        rest = rest.replace("\\", "/").lstrip("/")
        return f"/mnt/{drive}/{rest}"
    return win_path

def normalize_filename(name):
    """Normalize filename by lowercasing and replacing underscores, hyphens, and spaces with a common separator."""
    return name.lower().replace('_', ' ').replace('-', ' ').strip()

def index_files_in_path(search_path):
    """
    Index all files in a directory (recursively) and cache it.
    :param search_path: Base path to search.
    :return: List of full file paths.
    """
    global indexed_files_cache

    if is_wsl():
        search_path = convert_to_wsl_path(search_path)

    indexed_files = []
    for root, _, files in os.walk(search_path):
        for file in files:
            full_path = os.path.join(root, file)
            indexed_files.append(full_path)

    # Store cache by normalized path
    indexed_files_cache[normalize_filename(search_path)] = indexed_files
    return indexed_files

def fuzzy_search_file(stt_filename, search_path):
    """
    Fuzzy search for a file using STT input to tolerate typos or phonetically similar names.
    Silently returns best match without user prompts.

    :param stt_filename: The filename received via voice (can have typos).
    :param search_path: The directory to search in.
    :return: Best match file path or None.
    """
    global indexed_files_cache

    # Convert to WSL path if needed
    if is_wsl():
        search_path = convert_to_wsl_path(search_path)

    normalized_path = normalize_filename(search_path)

    # Index files if not cached
    if normalized_path not in indexed_files_cache:
        print(f"Indexing files in: {search_path}")
        indexed_files_cache[normalized_path] = index_files_in_path(search_path)

    all_files = indexed_files_cache[normalized_path]
    if not all_files:
        return None

    normalized_input = normalize_filename(stt_filename)
    file_name_map = {normalize_filename(os.path.basename(f)): f for f in all_files}
    all_normalized_names = list(file_name_map.keys())

    # Close matches
    close_matches = difflib.get_close_matches(normalized_input, all_normalized_names, n=5, cutoff=0.5)
    # Also include partial contains matches
    partial_matches = [name for name in all_normalized_names if normalized_input in name]

    combined_matches = list(dict.fromkeys(close_matches + partial_matches))  # Unique

    if not combined_matches:
        return None

    # Return best match path
    return file_name_map[combined_matches[0]]


def open_file(stt_filename, search_path):
    """
    Fuzzy match and open a file if it exists, even from WSL to Windows.

    :param stt_filename: The (possibly typoed) filename to find and open.
    :param search_path: Where to search.
    """
    # logger.info(f"Searching for {stt_filename} in {search_path}")
    file_path = fuzzy_search_file(stt_filename, search_path)

    if not file_path:
        print("No matching file found!")
        return

    # If in WSL, convert the WSL path to a Windows path for opening
    if is_wsl():
        # Convert `/mnt/c/Users/...` to `C:\\Users\\...`
        if file_path.startswith("/mnt/"):
            drive_letter = file_path[5]
            rest = file_path[7:]
            windows_path = f"{drive_letter.upper()}:\\{rest.replace('/', '\\')}"
        else:
            windows_path = file_path  # fallback

        if os.path.exists(file_path):
            try:
                # logger.info(f"Opening {windows_path}")
                subprocess.run(["cmd.exe", "/C", "start", "", windows_path])
            except Exception as e:
                print(f"Error opening file: {e}")
        else:
            print("File does not exist (WSL check)!")
    else:
        # Native Windows path
        if os.path.exists(file_path):
            try:
                os.startfile(file_path)
                # logger.info(f"Opening {file_path}")
            except Exception as e:
                print(f"Error opening file: {e}")
        else:
            print("File does not exist!")

def list_files_by_type(file_type, path=None):
    """
    Lists all files of a given type in the provided directory.
    Falls back to the user's Documents folder if no path is provided.

    :param file_type: One of ['word', 'ppt', 'pdf', 'image']
    :param path: Directory to search in. Defaults to ~/Documents.
    :return: List of file paths.
    """
    extensions_map = {
        'word': ['.doc', '.docx'],
        'ppt': ['.ppt', '.pptx'],
        'pdf': ['.pdf'],
        'image': ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    }

    file_type = file_type.lower()
    if file_type not in extensions_map:
        raise ValueError(f"Unsupported file type: {file_type}")

    if not path:
        path = os.path.join(os.path.expanduser("~"), "Documents")
        print(f"No path provided. Using fallback path: {path}")

    if is_wsl():
        path = convert_to_wsl_path(path)

    matched_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions_map[file_type]):
                matched_files.append(os.path.join(root, file))

    return matched_files
