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
    Set up a project inside the given parent folder.
    """
    try:
        project_type = normalize_project_type(project_type)
    except ValueError as e:
        print(e)
        return

    # Normalize parent path
    parent_path = os.path.abspath(parent_path)
    parent_path = to_wsl_path(parent_path)

    # Ask for project folder name
    project_name = input(f"Enter project name for {project_type} project: ").strip()
    if not project_name:
        print("Project name cannot be empty.")
        return

    project_folder = os.path.join(parent_path, project_name)
    project_folder = get_available_path(project_folder)

    os.makedirs(project_folder, exist_ok=True)

    try:
        if project_type == "react":
            subprocess.run(["npx", "create-react-app", project_folder], check=True)

        elif project_type == "next":
            subprocess.run(["npx", "create-next-app@latest", project_folder, "--ts"], check=True)

        elif project_type == "flask":
            os.makedirs(os.path.join(project_folder, "app"), exist_ok=True)
            with open(os.path.join(project_folder, "app", "__init__.py"), "w") as f:
                f.write("""from flask import Flask\n\napp = Flask(__name__)\n\n@app.route('/')\ndef home():\n    return "Hello, Flask!"\n""")
            with open(os.path.join(project_folder, "run.py"), "w") as f:
                f.write("from app import app\n\nif __name__ == '__main__':\n    app.run(debug=True)\n")
            subprocess.run(["pip", "install", "flask"], check=True)

        elif project_type == "django":
            subprocess.run(["pip", "install", "django"], check=True)
            subprocess.run(["django-admin", "startproject", "config", project_folder], check=True)

        print(f"{project_type.capitalize()} project set up successfully at {project_folder}.")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred during setup: {e}")

