import os
import shutil
import platform
import difflib

def is_wsl():
    return 'microsoft' in platform.uname().release.lower()

def convert_to_wsl_path(win_path: str) -> str:
    if ":" in win_path:
        drive, rest = win_path.split(":", 1)
        drive = drive.lower()
        rest = rest.replace("\\", "/").lstrip("/")
        return f"/mnt/{drive}/{rest}"
    return win_path


def search_file(file_name, search_path):
    """
    Search for a file in the given directory and subdirectories.

    :param file_name: File name (partial match allowed).
    :param search_path: Directory path to search in.
    :return: List of matching file paths, or None.
    """
    file_name = file_name.lower()
    matching_files = []

    # Handle path for WSL context
    if is_wsl():
        search_path = convert_to_wsl_path(search_path)

    for root, _, files in os.walk(search_path):
        for file in files:
            if file_name in file.lower():
                file_path = os.path.join(root, file)
                matching_files.append(file_path)

    return matching_files if matching_files else None


def fuzzy_search_file(stt_filename, search_path):
    """
    Fuzzy search for a file using STT input to tolerate typos or phonetically similar names.

    :param stt_filename: The filename received via voice (can have typos).
    :param search_path: The directory to search in.
    :return: Best match file path or None.
    """
    all_files = search_file("", search_path)  # Get all files

    if not all_files:
        return None

    file_names = [os.path.basename(f) for f in all_files]
    matches = difflib.get_close_matches(stt_filename.lower(), [f.lower() for f in file_names], n=1, cutoff=0.6)

    if matches:
        match_index = file_names.index(next(f for f in file_names if f.lower() == matches[0]))
        return all_files[match_index]

    return None


def open_file(stt_filename, search_path):
    """
    Fuzzy match and open a file if it exists, even from WSL to Windows.

    :param stt_filename: The (possibly typoed) filename to find and open.
    :param search_path: Where to search.
    """
    file_path = fuzzy_search_file(stt_filename, search_path)
    if not file_path:
        print("❌ No matching file found!")
        return

    if is_wsl():
        wsl_path = convert_to_wsl_path(file_path)
        if os.path.exists(wsl_path):
            try:
                os.system(f'cmd.exe /C start "" "{file_path}"')  # Open with Windows
            except Exception as e:
                print(f"⚠️ Error opening file: {e}")
        else:
            print("❌ File does not exist (WSL check)!")
    elif os.path.exists(file_path):  # Native Windows
        try:
            os.startfile(file_path)
        except Exception as e:
            print(f"⚠️ Error opening file: {e}")
    else:
        print("❌ File does not exist!")


def move_file(stt_filename, search_path, new_location):
    """
    Fuzzy match and move a file to a new location.

    :param stt_filename: The (possibly typoed) filename to move.
    :param search_path: Where to search for it.
    :param new_location: The target directory to move the file into.
    :return: New path of the moved file or None if failed.
    """
    file_path = fuzzy_search_file(stt_filename, search_path)
    if not file_path:
        print("❌ No matching file found to move!")
        return None

    check_path = convert_to_wsl_path(file_path) if is_wsl() else file_path

    if not os.path.exists(check_path):
        print("❌ File does not exist!")
        return None

    if not os.path.exists(new_location):
        os.makedirs(new_location)

    try:
        new_path = os.path.join(new_location, os.path.basename(file_path))
        shutil.move(file_path, new_path)
        return new_path
    except Exception as e:
        print(f"⚠️ Error moving file: {e}")
        return None


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
        raise ValueError(f"❌ Unsupported file type: {file_type}")

    if not path:
        path = os.path.join(os.path.expanduser("~"), "Documents")
        print(f"📁 No path provided. Using fallback path: {path}")

    if is_wsl():
        path = convert_to_wsl_path(path)

    matched_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions_map[file_type]):
                matched_files.append(os.path.join(root, file))

    return matched_files
