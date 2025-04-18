# takes repo name and path and sets up locally and runs|
import os
import subprocess
import shutil

def run_command(command, cwd=None):
    """Runs a shell command and returns output."""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True, cwd=cwd)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return e.stderr.strip()

def get_repo_folder(repo_link, target_directory):
    """Finds the correct repository folder after cloning."""
    repo_name = repo_link.split("/")[-1].replace(".git", "")
    repo_path = os.path.join(target_directory, repo_name)
    
    if os.path.exists(repo_path):
        return repo_path
    
    for folder in os.listdir(target_directory):
        folder_path = os.path.join(target_directory, folder)
        if os.path.isdir(folder_path) and repo_name.lower() in folder.lower():
            return folder_path
    
    print("ERROR: Repository folder not found after cloning.")
    return None

def detect_project_type(project_path):
    """Detects the project type."""
    if os.path.exists(os.path.join(project_path, "package.json")):
        return "node"
    elif os.path.exists(os.path.join(project_path, "requirements.txt")):
        return "python"
    elif os.path.exists(os.path.join(project_path, "pom.xml")):
        return "java"
    elif os.path.exists(os.path.join(project_path, "Cargo.toml")):
        return "rust"
    elif os.path.exists(os.path.join(project_path, "go.mod")):
        return "go"
    return "unknown"

def install_dependencies(project_path, project_type):
    """Installs dependencies."""
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
    """Runs the project."""
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

def setup_project(repo_link, target_directory):
    """Main function to setup the project."""
    try:
        os.makedirs(target_directory, exist_ok=True)
        
        print(f"📥 Cloning {repo_link} into {target_directory}...")
        run_command(f"git clone {repo_link}", cwd=target_directory)
        
        project_folder = get_repo_folder(repo_link, target_directory)
        
        if not project_folder or not os.path.exists(project_folder):
            print("ERROR: Repository folder not found. Exiting...")
            return
        
        print(f"Repository folder detected: {project_folder}")
        
        project_type = detect_project_type(project_folder)
        print(f"🛠 Detected project type: {project_type.upper()}")
        
        if project_type != "unknown":
            install_dependencies(project_folder, project_type)
            
            success, output = try_running_project(project_folder, project_type)
            
            if success:
                print("✅ Project is running successfully! 🎉")
            else:
                print(f"Project failed to start. Error:\n{output}")
        else:
            print("Could not detect project type. Manual setup required.")
    
    except KeyboardInterrupt:
        print("\nSetup process interrupted by user. Exiting...")

# # calls enviornment setup
# import subprocess

# # Define repo link and target directory
# repo_link = "https://github.com/moiz2405/portfolio"
# target_directory = "/home/moiz/myfolder/projects/devops-projects/environment_assistant"

# # Command to execute inside tmux
# command = f"python3 -c \"from setup import setup_project; setup_project('{repo_link}', '{target_directory}')\""

# def open_new_tmux_session(command):
#     """Opens a new tmux session and runs the command inside it."""
#     subprocess.Popen(["tmux", "new-session", "-d", command])

# # Run the setup script in a new tmux session
# open_new_tmux_session(command)
