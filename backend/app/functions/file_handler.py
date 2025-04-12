import os
import shutil
import platform

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


def open_file(file_path):
    """
    Open a file if it exists, even from WSL to Windows.

    :param file_path: The file path to open.
    """
    if is_wsl():
        wsl_path = convert_to_wsl_path(file_path)
        if os.path.exists(wsl_path):
            try:
                os.system(f'cmd.exe /C start "" "{file_path}"')  # open with Windows
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


def move_file(file_path, new_location):
    """
    Move a file to a new location.

    :param file_path: The file to be moved.
    :param new_location: The new directory where the file should go.
    :return: New path of the moved file or None if failed.
    """
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
