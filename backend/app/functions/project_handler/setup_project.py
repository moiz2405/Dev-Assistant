import os
import subprocess
import platform
import difflib
import threading
import queue
import time

# Cache for indexed directories to improve performance
indexed_dirs_cache = {}
# Queue for communication between threads
output_queue = queue.Queue()

# --- Utilities ---

def run_command(command, cwd=None, capture_output=True):
    """Run a shell command and return the output"""
    try:
        if capture_output:
            result = subprocess.run(
                command, 
                shell=True, 
                check=True, 
                text=True, 
                capture_output=True, 
                cwd=cwd
            )
            return True, result.stdout.strip()
        else:
            # For long-running processes we might not want to capture output
            subprocess.run(command, shell=True, check=True, cwd=cwd)
            return True, "Command executed successfully"
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()

def is_wsl():
    """Check if running in Windows Subsystem for Linux"""
    return 'microsoft' in platform.uname().release.lower()

def to_wsl_path(path):
    """Convert Windows path to WSL path if running in WSL"""
    if is_wsl():
        if path.startswith("/mnt/"):
            return path
        elif ':' in path:  # Windows path containing a drive letter
            # Convert D:// or D:/ to /mnt/d/
            drive, rest = path.split(':', 1)
            path = f"/mnt/{drive.lower()}/{rest.strip('/\\')}"
            return path.replace('\\', '/')
        try:
            result = subprocess.run(['wslpath', path], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
    return path

def normalize_filename(name):
    """Normalize filename for comparison"""
    return name.lower().replace('_', ' ').replace('-', ' ').strip()

def index_dirs_in_path(root_path):
    """Index all directories under root_path"""
    dir_paths = []
    try:
        for root, dirs, _ in os.walk(root_path):
            for d in dirs:
                dir_paths.append(os.path.join(root, d))
    except Exception as e:
        output_queue.put((None, f"Error indexing directories: {str(e)}"))
    return dir_paths

def fuzzy_search_dir(stt_dirname, search_path):
    """Find most similar directory name using fuzzy matching"""
    global indexed_dirs_cache

    if is_wsl():
        search_path = to_wsl_path(search_path)

    normalized_path = normalize_filename(search_path)

    if normalized_path not in indexed_dirs_cache:
        output_queue.put((None, f"Indexing directories in: {search_path}"))
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

# --- Project Detection ---

def detect_project_type(project_path):
    """Detect project type based on files present"""
    files_to_types = {
        "package.json": "node",
        "requirements.txt": "python",
        "pom.xml": "java",
        "Cargo.toml": "rust",
        "go.mod": "go",
        "composer.json": "php",
        "Gemfile": "ruby",
        ".csproj": "dotnet",
        "build.gradle": "gradle"
    }
    
    # Additional checks for specific project types
    if os.path.exists(os.path.join(project_path, "package.json")):
        with open(os.path.join(project_path, "package.json"), 'r') as f:
            content = f.read()
            if "react" in content.lower():
                return "react"
            elif "next" in content.lower():
                return "next"
            elif "vue" in content.lower():
                return "vue"
            elif "angular" in content.lower():
                return "angular"
            else:
                return "node"
            
    # Check for Django
    if os.path.exists(os.path.join(project_path, "manage.py")):
        with open(os.path.join(project_path, "manage.py"), 'r') as f:
            if "django" in f.read().lower():
                return "django"
    
    # Check for Flask
    if os.path.exists(os.path.join(project_path, "app.py")) or os.path.exists(os.path.join(project_path, "wsgi.py")):
        with open(os.path.join(project_path, "app.py" if os.path.exists(os.path.join(project_path, "app.py")) else "wsgi.py"), 'r') as f:
            if "flask" in f.read().lower():
                return "flask"
    
    # Generic file checks
    for filename, project_type in files_to_types.items():
        if any(f.endswith(filename) for f in os.listdir(project_path)):
            return project_type
            
    return "unknown"

def install_dependencies(project_path, project_type, process_id):
    """Install project dependencies based on project type"""
    commands = {
        "node": "npm install",
        "react": "npm install", 
        "next": "npm install",
        "vue": "npm install",
        "angular": "npm install",
        "python": "pip install -r requirements.txt",
        "django": "pip install -r requirements.txt" if os.path.exists(os.path.join(project_path, "requirements.txt")) else "pip install django",
        "flask": "pip install -r requirements.txt" if os.path.exists(os.path.join(project_path, "requirements.txt")) else "pip install flask",
        "java": "mvn install",
        "gradle": "./gradlew build",
        "rust": "cargo build",
        "go": "go mod tidy",
        "php": "composer install",
        "ruby": "bundle install",
        "dotnet": "dotnet restore"
    }
    
    if project_type in commands:
        output_queue.put((process_id, f"Installing dependencies for {project_type}..."))
        success, result = run_command(commands[project_type], cwd=project_path)
        if not success:
            output_queue.put((process_id, f"Error installing dependencies: {result}"))
            return False
        output_queue.put((process_id, "Dependencies installed successfully"))
        return True
    else:
        output_queue.put((process_id, "Unknown project type. Manual setup may be needed."))
        return False

def try_running_project(project_path, project_type, process_id):
    """Attempt to run the project based on its type"""
    commands = {
        "node": "npm start",
        "react": "npm start",
        "next": "npm run dev",
        "vue": "npm run serve",
        "angular": "ng serve",
        "django": "python manage.py runserver",
        "flask": "python app.py" if os.path.exists(os.path.join(project_path, "app.py")) else 
                 "python wsgi.py" if os.path.exists(os.path.join(project_path, "wsgi.py")) else
                 "flask run",
        "java": "mvn spring-boot:run" if os.path.exists(os.path.join(project_path, "pom.xml")) else "javac Main.java && java Main",
        "gradle": "./gradlew bootRun" if os.path.exists(os.path.join(project_path, "build.gradle")) and "spring-boot" in open(os.path.join(project_path, "build.gradle")).read() else "./gradlew run",
        "rust": "cargo run",
        "go": "go run .",
        "php": "php -S localhost:8000",
        "ruby": "rails server" if os.path.exists(os.path.join(project_path, "config", "routes.rb")) else "ruby app.rb",
        "dotnet": "dotnet run"
    }

    # For Python projects, try to find a main file
    if project_type == "python":
        main_files = ["main.py", "app.py", "run.py"]
        for file in main_files:
            if os.path.exists(os.path.join(project_path, file)):
                command = f"python {file}"
                break
        else:
            command = "python"  # Default if no main file found
    else:
        command = commands.get(project_type)

    if not command:
        output_queue.put((process_id, "No known command to run this project."))
        return False

    output_queue.put((process_id, f"Running {project_type} project with command: {command}"))
    
    # For long-running processes, we don't want to wait for them to complete
    # Instead we'll start them and return success
    try:
        # Use Popen to start without waiting
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=project_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit to see if it starts successfully
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is None:
            output_queue.put((process_id, f"Project started successfully with PID: {process.pid}"))
            return True
        else:
            # Process exited quickly, might be an error
            stdout, stderr = process.communicate()
            if stderr:
                output_queue.put((process_id, f"Error running project: {stderr}"))
            else:
                output_queue.put((process_id, f"Project exited quickly: {stdout}"))
            return False
    except Exception as e:
        output_queue.put((process_id, f"Error running project: {str(e)}"))
        return False

# --- Async Project Setup ---

def _setup_existing_project_thread(project_name, base_directory, process_id):
    """Background thread function for setting up an existing project"""
    try:
        base_directory = to_wsl_path(base_directory)
        
        output_queue.put((process_id, f"Searching for project: {project_name} in {base_directory}..."))
        project_folder = fuzzy_search_dir(project_name, base_directory)
        
        if not project_folder or not os.path.exists(project_folder):
            output_queue.put((process_id, "Project folder not found after fuzzy search. Exiting..."))
            output_queue.put((process_id, "FAILED"))
            return
            
        output_queue.put((process_id, f"Project folder detected: {project_folder}"))
        
        project_type = detect_project_type(project_folder)
        output_queue.put((process_id, f"Detected project type: {project_type.upper()}"))
        
        if project_type != "unknown":
            success = install_dependencies(project_folder, project_type, process_id)
            
            if success:
                run_success = try_running_project(project_folder, project_type, process_id)
                
                if run_success:
                    output_queue.put((process_id, "Project is running successfully! 🎉"))
                    output_queue.put((process_id, "COMPLETED"))
                else:
                    output_queue.put((process_id, "Project failed to start."))
                    output_queue.put((process_id, "FAILED"))
            else:
                output_queue.put((process_id, "Failed to install dependencies."))
                output_queue.put((process_id, "FAILED"))
        else:
            output_queue.put((process_id, "Could not detect project type. Manual setup may be needed."))
            output_queue.put((process_id, "FAILED"))
            
    except Exception as e:
        output_queue.put((process_id, f"Error during project setup: {str(e)}"))
        output_queue.put((process_id, "FAILED"))

def setup_existing_project(project_name, base_directory):
    """
    Asynchronously set up an existing project.
    Returns a process_id that can be used to track the progress.
    """
    # Generate a unique process ID
    process_id = f"setup_{int(time.time() * 1000)}"
    
    # Start the setup process in a background thread
    thread = threading.Thread(
        target=_setup_existing_project_thread,
        args=(project_name, base_directory, process_id),
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

# --- Example usage ---
if __name__ == "__main__":
    active_processes = {}
    
    # Start a process
    project_name = "portfolio"  # Replace with your project name
    base_directory = "/home/user/projects"  # Replace with your base directory
    
    process_id = setup_existing_project(project_name, base_directory)
    if process_id:
        active_processes[process_id] = {
            "name": project_name, 
            "directory": base_directory,
            "status": "RUNNING"
        }
        print(f"Started process {process_id} for project {project_name}")
    
    # Main event loop
    try:
        while active_processes:
            # Check for updates
            process_id, message = check_project_status()
            
            if process_id is not None:
                if message in ["COMPLETED", "FAILED"]:
                    if process_id in active_processes:
                        active_processes[process_id]["status"] = message
                        print(f"Process {process_id} {message}")
                        # Remove completed/failed processes after some time
                else:
                    print(f"[{process_id}] {message}")
            
            # Clean up completed/failed processes
            completed = [pid for pid, info in active_processes.items() 
                        if info["status"] in ["COMPLETED", "FAILED"]]
            for pid in completed:
                del active_processes[pid]
                
            time.sleep(0.1)  # Small delay to prevent CPU hogging
            
    except KeyboardInterrupt:
        print("\nSetup process interrupted by user. Exiting...")