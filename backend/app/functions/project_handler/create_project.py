import os
import subprocess
import platform

# Mapping of aliases to standard project types
PROJECT_TYPE_ALIASES = {
    "react": ["react", "react.js", "reactjs"],
    "next": ["next", "next.js", "nextjs", "nextjs app"],
    "flask": ["flask"],
    "django": ["django"]
}

def is_wsl():
    """Detect if the script is running inside WSL."""
    return 'microsoft' in platform.uname().release.lower()

def to_wsl_path(path):
    """Convert Windows path to WSL path if needed."""
    if is_wsl():
        if path.startswith("/mnt/"):
            return path  # Already WSL style
        try:
            result = subprocess.run(['wslpath', path], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
    return path

def normalize_filename(name):
    """Normalize filename: lowercase, replace underscores/hyphens with spaces."""
    return name.lower().replace('_', ' ').replace('-', ' ').strip()

def normalize_project_type(project_type: str) -> str:
    """Normalize project type input."""
    project_type = normalize_filename(project_type).replace(" ", "")
    for standard, aliases in PROJECT_TYPE_ALIASES.items():
        if project_type in [normalize_filename(alias).replace(" ", "") for alias in aliases]:
            return standard
    raise ValueError(f"Unsupported project type '{project_type}'. Supported types: {list(PROJECT_TYPE_ALIASES.keys())}")

def get_available_path(base_path: str) -> str:
    """Find an available folder path by appending (2), (3), etc."""
    if not os.path.exists(base_path):
        return base_path
    
    counter = 2
    while True:
        new_path = f"{base_path} ({counter})"
        if not os.path.exists(new_path):
            return new_path
        counter += 1

def setup_project(project_type: str, path: str):
    """
    Set up a project based on the type provided.

    Parameters:
    - project_type: Type of the project ('react', 'next', 'flask', 'django')
    - path: Directory path to create the project
    """
    try:
        # Normalize project type
        project_type = normalize_project_type(project_type)
    except ValueError as e:
        print(e)
        return

    # Normalize and handle WSL paths
    path = os.path.abspath(path)
    path = to_wsl_path(path)
    path = get_available_path(path)

    os.makedirs(path, exist_ok=True)
    os.chdir(path)

    try:
        if project_type == "react":
            subprocess.run(["npx", "create-react-app", "."], check=True)

        elif project_type == "next":
            subprocess.run(["npx", "create-next-app@latest", ".", "--ts"], check=True)

        elif project_type == "flask":
            os.makedirs("app", exist_ok=True)
            with open("app/__init__.py", "w") as f:
                f.write("""from flask import Flask\n\napp = Flask(__name__)\n\n@app.route('/')\ndef home():\n    return "Hello, Flask!"\n""")
            with open("run.py", "w") as f:
                f.write("from app import app\n\nif __name__ == '__main__':\n    app.run(debug=True)\n")
            subprocess.run(["pip", "install", "flask"], check=True)

        elif project_type == "django":
            subprocess.run(["pip", "install", "django"], check=True)
            subprocess.run(["django-admin", "startproject", "config", "."], check=True)

        print(f"{project_type.capitalize()} project set up successfully at {path}.")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred during setup: {e}")

