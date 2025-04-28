import os
import subprocess
import platform

PROJECT_TYPE_ALIASES = {
    "react": ["react", "react.js", "reactjs"],
    "next": ["next", "next.js", "nextjs", "nextjs app"],
    "flask": ["flask"],
    "django": ["django", "jango"]
}

def is_wsl():
    return 'microsoft' in platform.uname().release.lower()

def to_wsl_path(path):
    if is_wsl():
        if path.startswith("/mnt/"):
            return path
        try:
            result = subprocess.run(['wslpath', path], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
    return path

def normalize_filename(name):
    return name.lower().replace('_', ' ').replace('-', ' ').strip()

def normalize_project_type(project_type: str) -> str:
    project_type = normalize_filename(project_type).replace(" ", "")
    for standard, aliases in PROJECT_TYPE_ALIASES.items():
        if project_type in [normalize_filename(alias).replace(" ", "") for alias in aliases]:
            return standard
    raise ValueError(f"Unsupported project type '{project_type}'. Supported types: {list(PROJECT_TYPE_ALIASES.keys())}")

def get_available_path(base_path: str) -> str:
    if not os.path.exists(base_path):
        return base_path

    counter = 2
    while True:
        new_path = f"{base_path} ({counter})"
        if not os.path.exists(new_path):
            return new_path
        counter += 1

def setup_project(project_type: str, parent_path: str):
    """
    Automatically set up a project inside the given parent folder without asking anything.
    """

    try:
        project_type = normalize_project_type(project_type)
    except ValueError as e:
        print(e)
        return

    # Normalize parent path
    parent_path = os.path.abspath(parent_path)
    parent_path = to_wsl_path(parent_path)

    # Generate automatic project folder name
    project_folder_name = f"{project_type}-project"
    project_folder_path = os.path.join(parent_path, project_folder_name)
    project_folder_path = get_available_path(project_folder_path)

    try:
        if project_type == "react":
            subprocess.run(["npx", "create-react-app", project_folder_path], check=True)

        elif project_type == "next":
            subprocess.run(["npx", "create-next-app@latest", project_folder_path, "--ts"], check=True)

        elif project_type == "flask":
            # Create the folder
            subprocess.run(["mkdir", "-p", os.path.join(project_folder_path, "app")], check=True, shell=True)

            # Create __init__.py
            init_py_content = (
                "from flask import Flask\n\n"
                "app = Flask(__name__)\n\n"
                "@app.route('/')\n"
                "def home():\n"
                "    return \"Hello, Flask!\"\n"
            )
            subprocess.run(
                ["bash", "-c", f"echo \"{init_py_content}\" > \"{os.path.join(project_folder_path, 'app', '__init__.py')}\""],
                check=True
            )

            # Create run.py
            run_py_content = (
                "from app import app\n\n"
                "if __name__ == '__main__':\n"
                "    app.run(debug=True)\n"
            )
            subprocess.run(
                ["bash", "-c", f"echo \"{run_py_content}\" > \"{os.path.join(project_folder_path, 'run.py')}\""],
                check=True
            )

            subprocess.run(["pip", "install", "flask"], check=True)

        elif project_type == "django":
            subprocess.run(["pip", "install", "django"], check=True)
            subprocess.run(["django-admin", "startproject", "config", project_folder_path], check=True)

        print(f"{project_type.capitalize()} project set up successfully at {project_folder_path}.")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred during setup: {e}")
