import os
import platform

def convert_windows_path_to_wsl(path: str) -> str:
    """Converts Windows-style path to WSL-compatible path if needed."""
    if ':' in path:
        drive, rest = path.split(':', 1)
        drive = drive.lower()
        wsl_path = f"/mnt/{drive}/{rest.strip().replace('\\\\', '/').replace('\\', '/')}"
        return wsl_path
    return path

def list_directory_contents(path: str) -> list:
    """
    Returns the contents of the specified directory path (auto-converts Windows paths if on WSL).
    """
    try:
        # Convert to WSL path if needed
        if 'microsoft' in platform.uname().release.lower():
            path = convert_windows_path_to_wsl(path)

        contents = os.listdir(path)
        result = []
        for item in contents:
            full_path = os.path.join(path, item)
            result.append({
                "name": item,
                "type": "directory" if os.path.isdir(full_path) else "file"
            })
        return result

    except FileNotFoundError:
        raise FileNotFoundError(f"The specified path does not exist: {path}")
    except PermissionError:
        raise PermissionError(f"You do not have permission to access this path: {path}")
    except Exception as e:
        raise e
