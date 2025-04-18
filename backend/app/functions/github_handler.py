import os
import subprocess
import json
import requests
import platform
from dotenv import load_dotenv

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
        try:
            result = subprocess.run(['wslpath', path], capture_output=True, text=True)
            return result.stdout.strip()
        except Exception:
            pass
    return path

def push_folder_to_github(repo_name, folder_path):
    """
    Creates a GitHub repo and pushes the local folder to it.
    """
    if not USERNAME or not TOKEN:
        raise Exception("GitHub credentials not set in .env file.")

    folder_path = to_wsl_path(folder_path)

    # Check if repo exists on GitHub
    check_url = f"{GITHUB_API}/repos/{USERNAME}/{repo_name}"
    check = requests.get(check_url, auth=(USERNAME, TOKEN))
    if check.status_code == 200:
        print(f"Repo '{repo_name}' already exists on GitHub.")
        return

    # Create repo
    print("Creating GitHub repository...")
    payload = {"name": repo_name, "private": False}
    r = requests.post(f"{GITHUB_API}/user/repos", json=payload, auth=(USERNAME, TOKEN))
    if r.status_code != 201:
        raise Exception(f"Failed to create repo: {r.status_code}, {r.json()}")

    # Initialize Git and push
    print("Initializing local repo and pushing to GitHub...")

    if not os.path.exists(os.path.join(folder_path, ".git")):
        subprocess.run(["git", "init"], cwd=folder_path, check=True)

    subprocess.run(["git", "add", "."], cwd=folder_path, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=folder_path, check=True)
    subprocess.run(
        ["git", "remote", "add", "origin", f"https://github.com/{USERNAME}/{repo_name}.git"],
        cwd=folder_path,
        check=True
    )
    subprocess.run(["git", "branch", "-M", "main"], cwd=folder_path, check=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=folder_path, check=True)

    print(f"Successfully pushed '{repo_name}' to GitHub.")

def list_github_repos(save_to_file=True, filename="github_repos.json"):
    """
    Fetches repository names and URLs for the authenticated user.
    Stores only name and html_url if saving.
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

    if save_to_file:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(repos_summary, f, indent=2)
        print(f"Saved {len(repos_summary)} repositories to '{filename}'")

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
    query = query.lower()
    repo_list = load_repo_list(path)

    if isinstance(repo_list, dict) and "error" in repo_list:
        return repo_list["error"]

    matches = [repo for repo in repo_list if query in repo["name"].lower()]
    if not matches:
        return f"No match found for '{query}'"

    return matches[0]["url"]

def clone_github_repo(repo_url, target_directory):
    """
    Clones a GitHub repository to the specified target directory.
    """
    if not USERNAME or not TOKEN:
        raise Exception("GitHub credentials not set in .env file.")

    target_directory = to_wsl_path(target_directory)
    print(f"Cloning {repo_url} into {target_directory}...")

    result = subprocess.run(["git", "clone", repo_url], cwd=target_directory, shell=True)
    if result.returncode == 0:
        print("Successfully cloned GitHub repository.")
    else:
        print("Cloning failed.")
