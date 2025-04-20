import os
import subprocess
import json
import requests
import platform
import difflib
from dotenv import load_dotenv

indexed_dirs_cache = {}
# Load environment
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../..', '.env.local'))

# GitHub credentials
GITHUB_API = "https://api.github.com"
USERNAME = os.getenv("GITHUB_USERNAME")
TOKEN = os.getenv("GITHUB_TOKEN")

def is_wsl():
    return 'microsoft' in platform.uname().release.lower()

def to_wsl_path(path):
    if is_wsl():
        if path.startswith("/mnt/"):
            return path  # Already a WSL path
        try:
            result = subprocess.run(['wslpath', path], capture_output=True, text=True)
            return result.stdout.strip()
        except Exception:
            pass
    return path


def normalize_filename(name):
    """Normalize filename by lowercasing and replacing underscores, hyphens, and spaces with a common separator."""
    return name.lower().replace('_', ' ').replace('-', ' ').strip()


def index_dirs_in_path(root_path):
    """
    Walk through a directory and collect all subdirectory paths.
    """
    dir_paths = []
    for root, dirs, _ in os.walk(root_path):
        for d in dirs:
            dir_paths.append(os.path.join(root, d))
    return dir_paths

def fuzzy_search_dir(stt_dirname, search_path):
    """
    Fuzzy search for a directory using STT input to tolerate typos or phonetically similar names.
    Silently returns best match without user prompts.

    :param stt_dirname: The directory name received via voice (can have typos).
    :param search_path: The root directory to search in.
    :return: Best match directory path or None.
    """
    global indexed_dirs_cache

    # Convert to WSL path if needed
    if is_wsl():
        search_path = to_wsl_path(search_path)

    normalized_path = normalize_filename(search_path)

    # Index folders if not cached
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

    combined_matches = list(dict.fromkeys(close_matches + partial_matches))  # Unique

    if not combined_matches:
        return None

    return dir_name_map[combined_matches[0]]


def push_folder_to_github(repo_name, folder_path):
    """
    Creates a GitHub repo and pushes the local folder to it using fuzzy directory match.
    """
    if not USERNAME or not TOKEN:
        raise Exception("GitHub credentials not set in .env file.")

    # Fuzzy search for the correct folder
    matched_folder = fuzzy_search_dir(repo_name, folder_path)
    if not matched_folder:
        raise FileNotFoundError(f"No matching folder found for: {repo_name} in {folder_path}")

    print(f"Using matched folder: {matched_folder}")
    folder_path = to_wsl_path(matched_folder)

    # Extract folder name to use as repo name
    final_repo_name = os.path.basename(matched_folder)

    # Check if repo exists on GitHub
    check_url = f"{GITHUB_API}/repos/{USERNAME}/{final_repo_name}"
    check = requests.get(check_url, auth=(USERNAME, TOKEN))
    if check.status_code == 200:
        print(f"Repo '{final_repo_name}' already exists on GitHub.")
    else:
        # Create repo only if it doesn't already exist
        print("Creating GitHub repository...")
        payload = {"name": final_repo_name, "private": False}
        r = requests.post(f"{GITHUB_API}/user/repos", json=payload, auth=(USERNAME, TOKEN))
        if r.status_code != 201:
            raise Exception(f"Failed to create repo: {r.status_code}, {r.json()}")

    # Initialize Git and push
    print("Initializing local repo and pushing to GitHub...")

    if not os.path.exists(os.path.join(folder_path, ".git")):
        subprocess.run(["git", "init"], cwd=folder_path, check=True)

    repo_url = f"https://{USERNAME}:{TOKEN}@github.com/{USERNAME}/{final_repo_name}.git"
    subprocess.run(["git", "add", "."], cwd=folder_path, check=True)

    try:
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=folder_path, check=True)
    except subprocess.CalledProcessError:
        print("No changes to commit.")

    remotes = subprocess.run(["git", "remote"], cwd=folder_path, capture_output=True, text=True).stdout
    if "origin" not in remotes:
        subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=folder_path, check=True)
    else:
        subprocess.run(["git", "remote", "set-url", "origin", repo_url], cwd=folder_path, check=True)

    subprocess.run(["git", "branch", "-M", "main"], cwd=folder_path, check=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=folder_path, check=True)

    print(f"Successfully pushed '{final_repo_name}' to GitHub.")


def list_github_repos(save_to_file=True, filename="github_repos.json"):
    """
    Fetches repository names and URLs for the authenticated user.
    Stores only name and html_url if saving.
    Also prints an indexed list of repository names.
    """
    if not USERNAME or not TOKEN:
        raise Exception("GitHub credentials not set in .env file.")

    filename = to_wsl_path(filename)
    print("Fetching repository list...")

    repos_summary = []
    page = 1
    per_page = 100

    while True:
        url = f"{GITHUB_API}/user/repos?per_page={per_page}&page={page}"
        response = requests.get(url, auth=(USERNAME, TOKEN))

        if response.status_code != 200:
            print(f"Failed to fetch repositories: {response.status_code}")
            return

        repos = response.json()
        if not repos:
            break

        for repo in repos:
            name = repo["name"]
            url = repo["html_url"]
            repos_summary.append({"name": name, "url": url})

        page += 1

    # Print indexed list of names
    print("\nRepositories:")
    for idx, repo in enumerate(repos_summary, start=1):
        print(f"{idx}. {repo['name']}")

    if save_to_file:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(repos_summary, f, indent=2)
        print(f"\nSaved {len(repos_summary)} repositories to '{filename}'")

    print("Repository fetching complete.")

def load_repo_list(path="backend/github_repos.json"):
    path = to_wsl_path(path)
    try:
        with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"error": f"File not found at {path}"}

def search_repo_url(query, path="backend/github_repos.json"):
    print(f"Searching for query: {query}")
    # query = query.lower()
    repo_list = load_repo_list(path)

    if isinstance(repo_list, dict) and "error" in repo_list:
        return repo_list["error"]

    matches = [repo for repo in repo_list if query in repo["name"].lower()]
    if not matches:
        return f"No match found for '{query}'"

    return matches[0]["url"]

def clone_github_repo(repo_name, target_directory):
    """
    Clones a GitHub repository to the specified target directory.
    """
    print("repo name")
    print(repo_name)
    repo_url = search_repo_url(repo_name)
    print("repo url")
    print(repo_url)
    if not USERNAME or not TOKEN:
        raise Exception("GitHub credentials not set in .env file.")

    target_directory = to_wsl_path(target_directory)
    print(f"Cloning {repo_url} into {target_directory}...")

    result = subprocess.run(["git", "clone", repo_url], cwd=target_directory)
    if result.returncode == 0:
        print("Successfully cloned GitHub repository.")
    else:
        print("Cloning failed.")
