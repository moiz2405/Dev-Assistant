import os
import subprocess
import platform
import sys

PROJECT_TYPE_ALIASES = {
    "react": ["react", "react.js", "reactjs"],
    "next": ["next", "next.js", "nextjs", "nextjs app"],
    "flask": ["flask"],
    "django": ["django", "jango"]
}

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

def normalize_filename(name):
    """Normalize filename for comparison"""
    return name.lower().replace('_', ' ').replace('-', ' ').strip()

def normalize_project_type(project_type: str) -> str:
    """Normalize project type string to a standard format"""
    project_type = normalize_filename(project_type).replace(" ", "")
    for standard, aliases in PROJECT_TYPE_ALIASES.items():
        if project_type in [normalize_filename(alias).replace(" ", "") for alias in aliases]:
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

def setup_project(project_type: str, parent_path: str):
    """Set up a project based on the type provided."""
    try:
        project_type = normalize_project_type(project_type)
    except ValueError as e:
        print(e)
        return

    # Convert Windows path to WSL path if needed
    parent_path = to_wsl_path(parent_path)
    
    # Create parent directory if it doesn't exist
    os.makedirs(parent_path, exist_ok=True)
    
    # Project folder under the parent path
    project_folder_name = f"{project_type}-project"
    project_folder_path = os.path.join(parent_path, project_folder_name)
    project_folder_path = get_available_path(project_folder_path)
    
    print(f"Setting up {project_type} project at: {project_folder_path}")

    # Create the project directory
    os.makedirs(project_folder_path, exist_ok=True)
    
    # Store current directory to restore later
    original_dir = os.getcwd()
    
    try:
        if project_type == "react":
            # For React, we'll use create-react-app which needs to be run from parent directory
            os.chdir(os.path.dirname(project_folder_path))
            subprocess.run(["npx", "create-react-app", os.path.basename(project_folder_path)], check=True)

        elif project_type == "next":
            # For Next.js, change to parent directory first
            os.chdir(os.path.dirname(project_folder_path))
            subprocess.run(["npx", "create-next-app@latest", os.path.basename(project_folder_path), "--ts"], check=True)

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
            
            print("Flask project created successfully. Run 'pip install -r requirements.txt' to install dependencies.")

        elif project_type == "django":
            # For Django, we need to change directory first
            os.chdir(parent_path)
            subprocess.run(["django-admin", "startproject", os.path.basename(project_folder_path)], check=True)

        print(f"{project_type.capitalize()} project set up successfully at {project_folder_path}.")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred during setup: {e}")
    finally:
        # Restore original directory
        os.chdir(original_dir)

# Example usage
if __name__ == "__main__":
    while True:
        print("\nAvailable project types:", list(PROJECT_TYPE_ALIASES.keys()))
        project_type = input("Enter project type (or 'exit' to quit): ")
        if project_type.lower() == 'exit':
            break
            
        parent_path = input("Enter path for project: ")
        setup_project(project_type, parent_path)