import os
import subprocess
import platform
import threading
import time
import queue

PROJECT_TYPE_ALIASES = {
    "react": ["react", "react.js", "reactjs"],
    "next": ["next", "next.js", "nextjs", "nextjs app"],
    "flask": ["flask"],
    "django": ["django", "jango"]
}

# Queue for communication between threads
output_queue = queue.Queue()

def is_wsl():
    """Check if running in Windows Subsystem for Linux"""
    return 'microsoft' in platform.uname().release.lower()

def to_wsl_path(path):
    """Convert Windows path to WSL path if running in WSL"""
    if is_wsl() and ':' in path:  # Windows path containing a drive letter
        # Convert D:// or D:/ to /mnt/d/
        drive, rest = path.split(':', 1)
        path = f"/mnt/{drive.lower()}/{rest.strip('/\\')}"
        return path.replace('\\', '/')
    return path

# def normalize_filename(name):
#     """Normalize filename for comparison"""
#     return name.lower().replace('_', ' ').replace('-', ' ').strip()

# def normalize_project_type(project_type: str) -> str:
#     """Normalize project type string to a standard format"""
#     project_type = normalize_filename(project_type).replace(" ", "")
#     for standard, aliases in PROJECT_TYPE_ALIASES.items():
#         if project_type in [normalize_filename(alias).replace(" ", "") for alias in aliases]:
#             return standard
#     raise ValueError(f"Unsupported project type '{project_type}'. Supported types: {list(PROJECT_TYPE_ALIASES.keys())}")

def normalize_filename(name):
    """Normalize filename for comparison"""
    # Removing special characters and converting to lowercase
    return ''.join(e for e in name.lower() if e.isalnum()).strip()

def normalize_project_type(project_type: str) -> str:
    """Normalize project type string to a standard format"""
    # Normalize and strip unnecessary spaces or special characters
    project_type = normalize_filename(project_type)
    for standard, aliases in PROJECT_TYPE_ALIASES.items():
        # Check for exact match after normalization
        if project_type in [normalize_filename(alias) for alias in aliases]:
            return standard
    raise ValueError(f"Unsupported project type '{project_type}'. Supported types: {list(PROJECT_TYPE_ALIASES.keys())}")

def get_available_path(base_path: str) -> str:
    """Find an available path by appending (2), (3), etc. if needed"""
    if not os.path.exists(base_path):
        return base_path

    counter = 2
    while True:
        new_path = f"{base_path} ({counter})"
        if not os.path.exists(new_path):
            return new_path
        counter += 1

def _setup_project_thread(project_type, parent_path, process_id):
    """Worker function that runs in a separate thread"""
    try:
        # Convert Windows path to WSL path if needed
        parent_path = to_wsl_path(parent_path)
        
        # Create parent directory if it doesn't exist
        os.makedirs(parent_path, exist_ok=True)
        
        # Project folder under the parent path
        project_folder_name = f"{project_type}-project"
        project_folder_path = os.path.join(parent_path, project_folder_name)
        project_folder_path = get_available_path(project_folder_path)
        
        output_queue.put((process_id, f"Setting up {project_type} project at: {project_folder_path}"))

        # Create the project directory
        os.makedirs(project_folder_path, exist_ok=True)
        
        # Store current directory to restore later
        original_dir = os.getcwd()
        
        try:
            if project_type == "react":
                # For React, we'll use create-react-app which needs to be run from parent directory
                os.chdir(os.path.dirname(project_folder_path))
                subprocess.run(
                    ["npx", "create-react-app", os.path.basename(project_folder_path), "--use-npm", "--yes"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

            elif project_type == "next":
                # For Next.js, change to parent directory first
                os.chdir(os.path.dirname(project_folder_path))
                subprocess.run(
                    [
                        "npx", "create-next-app@latest", 
                        os.path.basename(project_folder_path),
                        "--typescript", 
                        "--eslint", 
                        "--tailwind", 
                        "--src-dir", 
                        "--app-router", 
                        "--turbopack"
                    ],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

            elif project_type == "flask":
                # For Flask, create files directly
                os.makedirs(os.path.join(project_folder_path, "app"), exist_ok=True)

                init_py_content = (
                    "from flask import Flask\n\n"
                    "app = Flask(__name__)\n\n"
                    "@app.route('/')\n"
                    "def home():\n"
                    "    return \"Hello, Flask!\"\n"
                )
                with open(os.path.join(project_folder_path, "app", "__init__.py"), "w") as f:
                    f.write(init_py_content)

                run_py_content = (
                    "from app import app\n\n"
                    "if __name__ == '__main__':\n"
                    "    app.run(debug=True)\n"
                )
                with open(os.path.join(project_folder_path, "run.py"), "w") as f:
                    f.write(run_py_content)

                # Create requirements.txt
                with open(os.path.join(project_folder_path, "requirements.txt"), "w") as f:
                    f.write("flask==2.2.3\n")
                
                output_queue.put((process_id, "Flask project created successfully. Run 'pip install -r requirements.txt' to install dependencies."))

            elif project_type == "django":
                # For Django, we need to change directory first
                os.chdir(parent_path)
                subprocess.run(
                    ["django-admin", "startproject", os.path.basename(project_folder_path)],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

            output_queue.put((process_id, f"{project_type.capitalize()} project set up successfully at {project_folder_path}."))
            output_queue.put((process_id, "COMPLETED"))

        except subprocess.CalledProcessError as e:
            output_queue.put((process_id, f"Error: {e}"))
            output_queue.put((process_id, "FAILED"))
        finally:
            # Restore original directory
            os.chdir(original_dir)
    except Exception as e:
        output_queue.put((process_id, f"Error: {str(e)}"))
        output_queue.put((process_id, "FAILED"))

def setup_project(project_type: str, parent_path: str):
    """
    Set up a project based on the type provided.
    Returns a process_id that can be used to track the progress.
    """
    try:
        project_type = normalize_project_type(project_type)
    except ValueError as e:
        print(f"Error: {e}")
        return None

    # Generate a unique process ID
    process_id = f"setup_{int(time.time() * 1000)}"
    
    # Start the setup process in a background thread
    thread = threading.Thread(
        target=_setup_project_thread,
        args=(project_type, parent_path, process_id),
        daemon=True
    )
    thread.start()
    
    return process_id

def check_project_status():
    """
    Check if there are any updates from the background processes.
    Returns a tuple of (process_id, message) or (None, None) if no updates.
    """
    try:
        return output_queue.get_nowait()
    except queue.Empty:
        return None, None

# Example usage
if __name__ == "__main__":
    active_processes = {}
    
    # Start a process
    project_type = "react"
    parent_path = "D:/va_projects"
    
    process_id = setup_project(project_type, parent_path)
    if process_id:
        active_processes[process_id] = {
            "type": project_type, 
            "path": parent_path,
            "status": "RUNNING"
        }
        print(f"Started process {process_id} for {project_type} project")
    
    # Main event loop
    try:
        while active_processes:
            # Check for updates
            process_id, message = check_project_status()
            
            if process_id is not None:
                if message in ["COMPLETED", "FAILED"]:
                    active_processes[process_id]["status"] = message
                    print(f"Process {process_id} {message}")
                    # Remove completed/failed processes after some time
                    # (In a real app, you might want to keep them for status reporting)
                else:
                    print(f"[{process_id}] {message}")
            
            # Clean up completed/failed processes
            completed = [pid for pid, info in active_processes.items() 
                        if info["status"] in ["COMPLETED", "FAILED"]]
            for pid in completed:
                del active_processes[pid]
                
            time.sleep(0.1)  # Small delay to prevent CPU hogging
            
    except KeyboardInterrupt:
        print("Exiting... (background processes will continue)")