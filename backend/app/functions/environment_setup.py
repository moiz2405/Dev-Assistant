import os
import subprocess
import shutil
import platform
import difflib

indexed_dirs_cache = {}

# --- Utilities ---

def run_command(command, cwd=None):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True, cwd=cwd)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return e.stderr.strip()

def is_wsl():
    return 'microsoft' in platform.uname().release.lower()

def to_wsl_path(path):
    if is_wsl():
        if path.startswith("/mnt/"):
            return path
        try:
            result = subprocess.run(['wslpath', path], capture_output=True, text=True)
            return result.stdout.strip()
        except Exception:
            pass
    return path

def normalize_filename(name):
    return name.lower().replace('_', ' ').replace('-', ' ').strip()

def index_dirs_in_path(root_path):
    dir_paths = []
    for root, dirs, _ in os.walk(root_path):
        for d in dirs:
            dir_paths.append(os.path.join(root, d))
    return dir_paths

def fuzzy_search_dir(stt_dirname, search_path):
    global indexed_dirs_cache

    if is_wsl():
        search_path = to_wsl_path(search_path)

    normalized_path = normalize_filename(search_path)

    if normalized_path not in indexed_dirs_cache:
        print(f"Indexing directories in: {search_path}")
        indexed_dirs_cache[normalized_path] = index_dirs_in_path(search_path)

    all_dirs = indexed_dirs_cache[normalized_path]
    if not all_dirs:
        return None

    normalized_input = normalize_filename(stt_dirname)
    dir_name_map = {normalize_filename(os.path.basename(d)): d for d in all_dirs}
    all_normalized_names = list(dir_name_map.keys())

    close_matches = difflib.get_close_matches(normalized_input, all_normalized_names, n=5, cutoff=0.5)
    partial_matches = [name for name in all_normalized_names if normalized_input in name]

    combined_matches = list(dict.fromkeys(close_matches + partial_matches))

    if not combined_matches:
        return None

    return dir_name_map[combined_matches[0]]

# --- Project Setup ---

def detect_project_type(project_path):
    files_to_types = {
        "package.json": "node",
        "requirements.txt": "python",
        "pom.xml": "java",
        "Cargo.toml": "rust",
        "go.mod": "go"
    }
    for filename, project_type in files_to_types.items():
        if os.path.exists(os.path.join(project_path, filename)):
            return project_type
    return "unknown"


def install_dependencies(project_path, project_type):
    commands = {
        "node": "npm install",
        "python": "pip install -r requirements.txt",
        "java": "mvn install",
        "rust": "cargo build",
        "go": "go mod tidy"
    }
    if project_type in commands:
        print(f"Installing dependencies for {project_type}...")
        run_command(commands[project_type], cwd=project_path)
    else:
        print("Unknown project type. Manual setup may be needed.")

def try_running_project(project_path, project_type):
    commands = {
        "node": "npm run dev",
        "java": "mvn spring-boot:run" if os.path.exists(os.path.join(project_path, "pom.xml")) else "javac Main.java && java Main",
        "rust": "cargo run",
        "go": "go run ."
    }

    command = "python main.py" if project_type == "python" and os.path.exists(os.path.join(project_path, "main.py")) else commands.get(project_type, None)

    if not command:
        return False, "No known command to run this project."

    print(f"Running {project_type} project...")
    result = run_command(command, cwd=project_path)
    return True, result

def setup_existing_project(project_name, base_directory):
    """
    Main function to search, setup, and run a local project.
    """
    try:
        base_directory = to_wsl_path(base_directory)

        print(f"🔍 Searching for project: {project_name} in {base_directory}...")
        project_folder = fuzzy_search_dir(project_name, base_directory)

        if not project_folder or not os.path.exists(project_folder):
            print("❌ Project folder not found after fuzzy search. Exiting...")
            return

        print(f"✅ Project folder detected: {project_folder}")

        project_type = detect_project_type(project_folder)
        print(f"🛠 Detected project type: {project_type.upper()}")

        if project_type != "unknown":
            install_dependencies(project_folder, project_type)

            success, output = try_running_project(project_folder, project_type)

            if success:
                print("✅ Project is running successfully! 🎉")
            else:
                print(f"❌ Project failed to start. Error:\n{output}")
        else:
            print("⚠️ Could not detect project type. Manual setup may be needed.")

    except KeyboardInterrupt:
        print("\nSetup process interrupted by user. Exiting...")

# --- Example usage ---

# from this script you can now call:
# setup_existing_project("portfolio", "/home/moiz/myfolder/projects/devops-projects/environment_assistant")

